"""Sprint 6 Backend Tests — Recovery Engine + Voice Service.

Stories 3.1–3.6: 6-Level Recovery Engine
Stories 1.1–1.5: Voice Service, routes, silence detection
"""

from __future__ import annotations

import asyncio
import base64
import math
import struct
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.recovery_engine import (
    ALTERNATIVE_METHODS,
    RecoveryAttempt,
    RecoveryContext,
    RecoveryEngine,
    RecoveryLevel,
    RecoveryResult,
)
from app.services.voice_service import (
    SilenceDetectionResult,
    TranscriptionResult,
    VoiceConfig,
    VoiceService,
)


# ═══════════════════════════════════════════════════════════
# RECOVERY ENGINE TESTS (Stories 3.1–3.6)
# ═══════════════════════════════════════════════════════════


class TestRecoveryLevel:
    """Test RecoveryLevel enum values."""

    def test_levels_ordered(self):
        assert RecoveryLevel.L1_RETRY == 1
        assert RecoveryLevel.L2_ALTERNATIVE == 2
        assert RecoveryLevel.L3_REVERIFY == 3
        assert RecoveryLevel.L4_REPLAN == 4
        assert RecoveryLevel.L5_USER_CONFIRM == 5
        assert RecoveryLevel.L6_IMPOSSIBLE == 6

    def test_levels_are_int(self):
        for level in RecoveryLevel:
            assert isinstance(level.value, int)


class TestRecoveryAttempt:
    """Test RecoveryAttempt dataclass."""

    def test_create_attempt(self):
        a = RecoveryAttempt(
            level=RecoveryLevel.L1_RETRY,
            method="retry",
            success=True,
            duration_ms=150.0,
        )
        assert a.level == RecoveryLevel.L1_RETRY
        assert a.success is True
        assert a.duration_ms == 150.0
        assert a.error is None
        assert a.timestamp > 0

    def test_attempt_with_error(self):
        a = RecoveryAttempt(
            level=RecoveryLevel.L2_ALTERNATIVE,
            method="alt:yarn",
            success=False,
            duration_ms=300.0,
            error="Yarn not found",
        )
        assert a.error == "Yarn not found"


class TestRecoveryResult:
    """Test RecoveryResult and total_duration."""

    def test_total_duration(self):
        attempts = [
            RecoveryAttempt(RecoveryLevel.L1_RETRY, "retry", False, 100.0),
            RecoveryAttempt(RecoveryLevel.L2_ALTERNATIVE, "alt", True, 200.0),
        ]
        r = RecoveryResult(True, RecoveryLevel.L2_ALTERNATIVE, attempts)
        assert r.total_duration_ms == 300.0

    def test_empty_attempts(self):
        r = RecoveryResult(False, RecoveryLevel.L6_IMPOSSIBLE, [])
        assert r.total_duration_ms == 0.0


class TestRecoveryContext:
    """Test RecoveryContext default values."""

    def test_defaults(self):
        ctx = RecoveryContext(
            execution_id="exec-1",
            step_index=0,
            agent_name="test-agent",
            action="test",
            parameters={},
            error="timeout",
        )
        assert ctx.max_retries == 3
        assert ctx.base_timeout == 30.0
        assert ctx.backoff_multiplier == 1.5
        assert ctx.confidence_threshold == 0.75
        assert ctx.skippable is True


class TestL1Retry:
    """Story 3.1 — Timeout Recovery L1."""

    @pytest.mark.asyncio
    async def test_l1_success_on_first_retry(self):
        engine = RecoveryEngine()
        call_count = 0

        async def exec_fn(agent, action, params):
            nonlocal call_count
            call_count += 1
            if call_count >= 1:
                return {"result": "ok"}
            raise RuntimeError("timeout")

        ctx = RecoveryContext(
            execution_id="e1", step_index=0, agent_name="a1",
            action="do_thing", parameters={}, error="timeout",
            max_retries=3, base_timeout=1.0, backoff_multiplier=1.5,
            execute_fn=exec_fn,
        )

        result = await engine.recover(ctx)
        assert result.success is True
        assert result.final_level == RecoveryLevel.L1_RETRY

    @pytest.mark.asyncio
    async def test_l1_all_retries_fail(self):
        engine = RecoveryEngine()

        async def exec_fn(agent, action, params):
            raise RuntimeError("always fails")

        ctx = RecoveryContext(
            execution_id="e2", step_index=0, agent_name="a1",
            action="do_thing", parameters={}, error="timeout",
            max_retries=2, base_timeout=0.01, backoff_multiplier=1.0,
            execute_fn=exec_fn,
        )

        # Recovery should escalate past L1
        result = await engine.recover(ctx)
        # L1 failed, no alternatives, no screenshot, no replan → L5 auto-skip → success
        assert len(result.attempts) > 1

    @pytest.mark.asyncio
    async def test_l1_no_execute_fn(self):
        engine = RecoveryEngine()
        ctx = RecoveryContext(
            execution_id="e3", step_index=0, agent_name="a1",
            action="do_thing", parameters={}, error="timeout",
            execute_fn=None,
        )
        result = await engine.recover(ctx)
        assert result.attempts[0].success is False
        assert "No execute function" in result.attempts[0].error

    @pytest.mark.asyncio
    async def test_l1_backoff_increases(self):
        engine = RecoveryEngine()
        timeouts = []

        async def exec_fn(agent, action, params):
            raise RuntimeError("fail")

        original_wait_for = asyncio.wait_for

        async def mock_wait_for(coro, *, timeout=None):
            timeouts.append(timeout)
            return await original_wait_for(coro, timeout=timeout)

        ctx = RecoveryContext(
            execution_id="e4", step_index=0, agent_name="a1",
            action="do_thing", parameters={}, error="timeout",
            max_retries=3, base_timeout=10.0, backoff_multiplier=1.5,
            execute_fn=exec_fn,
        )

        with patch("app.services.recovery_engine.asyncio.wait_for", side_effect=mock_wait_for):
            await engine._l1_retry(ctx)

        # Should have 3 retries with increasing timeouts: 10, 15, 22.5
        assert len(timeouts) == 3
        assert timeouts[0] == 10.0
        assert timeouts[1] == pytest.approx(15.0)
        assert timeouts[2] == pytest.approx(22.5)

    @pytest.mark.asyncio
    async def test_l1_notify_callback(self):
        engine = RecoveryEngine()
        notifications = []

        async def exec_fn(agent, action, params):
            raise RuntimeError("fail")

        async def notify_fn(msg):
            notifications.append(msg)

        ctx = RecoveryContext(
            execution_id="e5", step_index=1, agent_name="a1",
            action="act", parameters={}, error="timeout",
            max_retries=2, base_timeout=0.01, backoff_multiplier=1.0,
            execute_fn=exec_fn, notify_fn=notify_fn,
        )

        await engine._l1_retry(ctx)
        assert len(notifications) == 2
        assert all(n["level"] == 1 for n in notifications)
        assert all(n["step_index"] == 1 for n in notifications)


class TestL2Alternative:
    """Story 3.2 — Alternative Method Recovery L2."""

    @pytest.mark.asyncio
    async def test_l2_finds_alternative(self):
        engine = RecoveryEngine()

        async def exec_fn(agent, action, params):
            if "yarn" in action:
                return {"result": "installed"}
            raise RuntimeError("npm failed")

        ctx = RecoveryContext(
            execution_id="e1", step_index=0, agent_name="a1",
            action="npm install", parameters={}, error="npm failed",
            execute_fn=exec_fn,
        )

        attempt = await engine._l2_alternative(ctx)
        assert attempt.success is True
        assert "yarn" in attempt.method

    @pytest.mark.asyncio
    async def test_l2_no_alternatives(self):
        engine = RecoveryEngine()

        async def exec_fn(agent, action, params):
            raise RuntimeError("fail")

        ctx = RecoveryContext(
            execution_id="e2", step_index=0, agent_name="a1",
            action="custom_command", parameters={}, error="failed",
            execute_fn=exec_fn,
        )

        attempt = await engine._l2_alternative(ctx)
        assert attempt.success is False
        assert "No alternative" in attempt.error

    @pytest.mark.asyncio
    async def test_l2_all_alternatives_fail(self):
        engine = RecoveryEngine()

        async def exec_fn(agent, action, params):
            raise RuntimeError("all fail")

        ctx = RecoveryContext(
            execution_id="e3", step_index=0, agent_name="a1",
            action="npm install", parameters={}, error="failed",
            base_timeout=0.01,
            execute_fn=exec_fn,
        )

        attempt = await engine._l2_alternative(ctx)
        assert attempt.success is False
        assert "All alternatives failed" in attempt.error

    def test_alternative_methods_bidirectional(self):
        """Verify mappings exist for common tools."""
        assert "npm" in ALTERNATIVE_METHODS
        assert "yarn" in ALTERNATIVE_METHODS["npm"]
        assert "npm" in ALTERNATIVE_METHODS["yarn"]
        assert "powershell" in ALTERNATIVE_METHODS
        assert "cmd" in ALTERNATIVE_METHODS["powershell"]


class TestL3Reverify:
    """Story 3.3 — Re-Verification L3."""

    @pytest.mark.asyncio
    async def test_l3_high_confidence(self):
        engine = RecoveryEngine()

        async def screenshot_fn(exec_id, step_idx):
            return b"fake_screenshot"

        async def analyze_fn(screenshot, action):
            return {"confidence": 0.85, "analysis": "looks correct"}

        ctx = RecoveryContext(
            execution_id="e1", step_index=0, agent_name="a1",
            action="act", parameters={}, error="err",
            confidence_threshold=0.75,
            screenshot_fn=screenshot_fn,
            analyze_screenshot_fn=analyze_fn,
        )

        attempt = await engine._l3_reverify(ctx)
        assert attempt.success is True
        assert attempt.details["confidence"] == 0.85

    @pytest.mark.asyncio
    async def test_l3_low_confidence(self):
        engine = RecoveryEngine()

        async def screenshot_fn(exec_id, step_idx):
            return b"fake_screenshot"

        async def analyze_fn(screenshot, action):
            return {"confidence": 0.5}

        ctx = RecoveryContext(
            execution_id="e2", step_index=0, agent_name="a1",
            action="act", parameters={}, error="err",
            confidence_threshold=0.75,
            screenshot_fn=screenshot_fn,
            analyze_screenshot_fn=analyze_fn,
        )

        attempt = await engine._l3_reverify(ctx)
        assert attempt.success is False
        assert "0.50" in attempt.error

    @pytest.mark.asyncio
    async def test_l3_no_screenshot_fn(self):
        engine = RecoveryEngine()
        ctx = RecoveryContext(
            execution_id="e3", step_index=0, agent_name="a1",
            action="act", parameters={}, error="err",
            screenshot_fn=None, analyze_screenshot_fn=None,
        )

        attempt = await engine._l3_reverify(ctx)
        assert attempt.success is False
        assert "not available" in attempt.error


class TestL4Replan:
    """Story 3.4 — Replan with SAA L4."""

    @pytest.mark.asyncio
    async def test_l4_successful_replan(self):
        engine = RecoveryEngine()

        async def replan_fn(agent, action, params, error):
            return {
                "steps": [
                    {"agent": "a1", "action": "alt_step_1", "parameters": {}},
                ]
            }

        async def exec_fn(agent, action, params):
            return {"result": "done"}

        ctx = RecoveryContext(
            execution_id="e1", step_index=0, agent_name="a1",
            action="act", parameters={}, error="err",
            base_timeout=1.0,
            execute_fn=exec_fn, replan_fn=replan_fn,
        )

        attempt = await engine._l4_replan(ctx)
        assert attempt.success is True

    @pytest.mark.asyncio
    async def test_l4_no_replan_fn(self):
        engine = RecoveryEngine()
        ctx = RecoveryContext(
            execution_id="e2", step_index=0, agent_name="a1",
            action="act", parameters={}, error="err",
            replan_fn=None,
        )

        attempt = await engine._l4_replan(ctx)
        assert attempt.success is False
        assert "not available" in attempt.error

    @pytest.mark.asyncio
    async def test_l4_empty_plan(self):
        engine = RecoveryEngine()

        async def replan_fn(agent, action, params, error):
            return {"steps": []}

        ctx = RecoveryContext(
            execution_id="e3", step_index=0, agent_name="a1",
            action="act", parameters={}, error="err",
            replan_fn=replan_fn,
        )

        attempt = await engine._l4_replan(ctx)
        assert attempt.success is False
        assert "could not generate" in attempt.error

    @pytest.mark.asyncio
    async def test_l4_replan_step_fails(self):
        engine = RecoveryEngine()

        async def replan_fn(agent, action, params, error):
            return {
                "steps": [
                    {"agent": "a1", "action": "will_fail", "parameters": {}},
                ]
            }

        async def exec_fn(agent, action, params):
            raise RuntimeError("step failed")

        ctx = RecoveryContext(
            execution_id="e4", step_index=0, agent_name="a1",
            action="act", parameters={}, error="err",
            base_timeout=0.5,
            execute_fn=exec_fn, replan_fn=replan_fn,
        )

        attempt = await engine._l4_replan(ctx)
        assert attempt.success is False
        assert "step failed" in attempt.error


class TestL5UserConfirm:
    """Story 3.5 — User Confirmation L5."""

    @pytest.mark.asyncio
    async def test_l5_user_chooses_skip(self):
        engine = RecoveryEngine()

        async def user_fn(exec_id, step_idx, error):
            return {"action": "skip"}

        ctx = RecoveryContext(
            execution_id="e1", step_index=0, agent_name="a1",
            action="act", parameters={}, error="err",
            skippable=True,
            user_confirm_fn=user_fn,
        )

        attempt = await engine._l5_user_confirm(ctx)
        assert attempt.success is True
        assert attempt.details["user_choice"] == "skip"

    @pytest.mark.asyncio
    async def test_l5_user_chooses_cancel(self):
        engine = RecoveryEngine()

        async def user_fn(exec_id, step_idx, error):
            return {"action": "cancel"}

        ctx = RecoveryContext(
            execution_id="e2", step_index=0, agent_name="a1",
            action="act", parameters={}, error="err",
            user_confirm_fn=user_fn,
        )

        attempt = await engine._l5_user_confirm(ctx)
        assert attempt.success is False
        assert attempt.details["user_choice"] == "cancel"

    @pytest.mark.asyncio
    async def test_l5_auto_skip_when_no_handler(self):
        engine = RecoveryEngine()
        ctx = RecoveryContext(
            execution_id="e3", step_index=0, agent_name="a1",
            action="act", parameters={}, error="err",
            skippable=True,
            user_confirm_fn=None,
        )

        attempt = await engine._l5_user_confirm(ctx)
        assert attempt.success is True
        assert attempt.method == "auto-skip"

    @pytest.mark.asyncio
    async def test_l5_no_handler_not_skippable(self):
        engine = RecoveryEngine()
        ctx = RecoveryContext(
            execution_id="e4", step_index=0, agent_name="a1",
            action="act", parameters={}, error="err",
            skippable=False,
            user_confirm_fn=None,
        )

        attempt = await engine._l5_user_confirm(ctx)
        assert attempt.success is False

    @pytest.mark.asyncio
    async def test_l5_user_retry_succeeds(self):
        engine = RecoveryEngine()
        call_count = 0

        async def user_fn(exec_id, step_idx, error):
            return {"action": "retry"}

        async def exec_fn(agent, action, params):
            nonlocal call_count
            call_count += 1
            return "retry_ok"

        ctx = RecoveryContext(
            execution_id="e5", step_index=0, agent_name="a1",
            action="act", parameters={}, error="err",
            max_retries=1, base_timeout=1.0,
            execute_fn=exec_fn, user_confirm_fn=user_fn,
        )

        attempt = await engine._l5_user_confirm(ctx)
        assert attempt.success is True
        assert attempt.method == "user-retry"


class TestL6Impossible:
    """Story 3.6 — Mark Impossible L6."""

    @pytest.mark.asyncio
    async def test_l6_marks_impossible(self):
        engine = RecoveryEngine()
        notifications = []

        async def notify_fn(msg):
            notifications.append(msg)

        ctx = RecoveryContext(
            execution_id="e1", step_index=2, agent_name="a1",
            action="act", parameters={}, error="err",
            notify_fn=notify_fn,
        )

        attempt = await engine._l6_impossible(ctx)
        assert attempt.success is False
        assert attempt.method == "mark_impossible"
        assert "suggestion" in attempt.details
        assert len(notifications) == 1
        assert notifications[0]["level"] == 6


class TestRecoveryMetrics:
    """Test engine metrics tracking."""

    @pytest.mark.asyncio
    async def test_metrics_increment(self):
        engine = RecoveryEngine()

        async def exec_fn(agent, action, params):
            return "ok"

        ctx = RecoveryContext(
            execution_id="e1", step_index=0, agent_name="a1",
            action="act", parameters={}, error="err",
            max_retries=1, base_timeout=1.0,
            execute_fn=exec_fn,
        )

        await engine.recover(ctx)
        m = engine.metrics
        assert m["l1_attempts"] >= 1
        assert m["l1_successes"] >= 1

    @pytest.mark.asyncio
    async def test_l6_trigger_counted(self):
        engine = RecoveryEngine()
        ctx = RecoveryContext(
            execution_id="e2", step_index=0, agent_name="a1",
            action="act", parameters={}, error="err",
            skippable=False,
            execute_fn=None,
        )

        await engine.recover(ctx)
        assert engine.metrics["l6_triggers"] >= 1


class TestFullRecoveryChain:
    """Test escalation through multiple levels."""

    @pytest.mark.asyncio
    async def test_escalates_l1_to_l5_skip(self):
        """L1 fails → L2 no alt → L3 no screenshot → L4 no replan → L5 auto-skip."""
        engine = RecoveryEngine()

        async def exec_fn(agent, action, params):
            raise RuntimeError("always fails")

        ctx = RecoveryContext(
            execution_id="chain-1", step_index=0, agent_name="a1",
            action="custom_action", parameters={}, error="timeout",
            max_retries=1, base_timeout=0.01, backoff_multiplier=1.0,
            skippable=True,
            execute_fn=exec_fn,
        )

        result = await engine.recover(ctx)
        # Should succeed via L5 auto-skip
        assert result.success is True
        assert result.final_level == RecoveryLevel.L5_USER_CONFIRM
        assert result.action_taken == "skip"
        assert len(result.attempts) == 5  # L1, L2, L3, L4, L5

    @pytest.mark.asyncio
    async def test_escalates_to_l6_impossible(self):
        """All levels fail on non-skippable step → L6 impossible."""
        engine = RecoveryEngine()

        async def exec_fn(agent, action, params):
            raise RuntimeError("always fails")

        ctx = RecoveryContext(
            execution_id="chain-2", step_index=0, agent_name="a1",
            action="custom_action", parameters={}, error="timeout",
            max_retries=1, base_timeout=0.01, backoff_multiplier=1.0,
            skippable=False,
            execute_fn=exec_fn,
        )

        result = await engine.recover(ctx)
        assert result.success is False
        assert result.final_level == RecoveryLevel.L6_IMPOSSIBLE
        assert result.action_taken == "impossible"
        assert len(result.attempts) == 6  # L1 through L6


# ═══════════════════════════════════════════════════════════
# VOICE SERVICE TESTS (Stories 1.1–1.5)
# ═══════════════════════════════════════════════════════════


class TestTranscriptionResult:
    """Test TranscriptionResult dataclass."""

    def test_to_dict(self):
        r = TranscriptionResult(
            text="hello world",
            confidence=0.95,
            language="en",
            duration_ms=150.0,
            source="voice",
            auto_accepted=True,
        )
        d = r.to_dict()
        assert d["text"] == "hello world"
        assert d["confidence"] == 0.95
        assert d["auto_accepted"] is True
        assert d["needs_re_speak"] is False


class TestVoiceConfig:
    """Test VoiceConfig."""

    def test_defaults(self):
        cfg = VoiceConfig()
        assert cfg.confidence_threshold == 0.90
        assert cfg.silence_db_threshold == 5.0
        assert cfg.silence_duration == 1.5
        assert cfg.max_recording_seconds == 30

    def test_to_dict(self):
        cfg = VoiceConfig(confidence_threshold=0.85, language="es")
        d = cfg.to_dict()
        assert d["confidence_threshold"] == 0.85
        assert d["language"] == "es"

    def test_from_settings(self):
        """VoiceConfig.from_settings with custom settings."""
        mock_settings = MagicMock()
        mock_settings.voice_confidence_threshold = 0.88
        mock_settings.voice_auto_accept_threshold = 0.92
        mock_settings.voice_re_speak_threshold = 0.75
        mock_settings.voice_silence_db = 3.0
        mock_settings.voice_silence_duration = 2.0
        mock_settings.voice_max_duration = 45

        cfg = VoiceConfig.from_settings(mock_settings)
        assert cfg.confidence_threshold == 0.88
        assert cfg.auto_accept_threshold == 0.92
        assert cfg.silence_duration == 2.0
        assert cfg.max_recording_seconds == 45


class TestSilenceDetection:
    """Story 1.4 — Silence detection."""

    def test_detect_silence_quiet(self):
        """Very quiet audio should be detected as silence."""
        svc = VoiceService.__new__(VoiceService)
        svc._settings = MagicMock()
        svc._config = VoiceConfig(silence_db_threshold=10.0, silence_duration=0.5)
        svc._device_profiles = {}

        # Generate near-silent 16-bit PCM data (very low amplitude ~5.69 dB)
        num_samples = 8000  # 0.5s at 16kHz
        silent_bytes = struct.pack(f"<{num_samples}h", *([1] * num_samples))

        result = svc.detect_silence(silent_bytes, sample_rate=16000, sample_width=2)
        assert result.is_silent is True
        assert result.avg_db < 10.0

    def test_detect_silence_loud(self):
        """Loud audio should not be detected as silence."""
        svc = VoiceService.__new__(VoiceService)
        svc._settings = MagicMock()
        svc._config = VoiceConfig(silence_db_threshold=5.0, silence_duration=0.5)
        svc._device_profiles = {}

        # Generate loud 16-bit PCM data
        num_samples = 8000
        loud_bytes = struct.pack(f"<{num_samples}h", *([20000] * num_samples))

        result = svc.detect_silence(loud_bytes, sample_rate=16000, sample_width=2)
        assert result.is_silent is False
        assert result.avg_db > 5.0

    def test_detect_silence_empty(self):
        """Empty audio returns silent with 0 duration."""
        svc = VoiceService.__new__(VoiceService)
        svc._settings = MagicMock()
        svc._config = VoiceConfig()
        svc._device_profiles = {}

        result = svc.detect_silence(b"", sample_rate=16000, sample_width=2)
        assert result.is_silent is True
        assert result.duration_seconds == 0.0

    def test_should_submit_after_silence(self):
        """Submit flag when silence exceeds duration threshold."""
        svc = VoiceService.__new__(VoiceService)
        svc._settings = MagicMock()
        svc._config = VoiceConfig(
            silence_db_threshold=10.0, silence_duration=0.5,
        )
        svc._device_profiles = {}

        # 1 second of silence (amplitude 1 → ~5.69 dB, below 10.0)
        num_samples = 16000
        silent_bytes = struct.pack(f"<{num_samples}h", *([1] * num_samples))

        result = svc.detect_silence(silent_bytes, sample_rate=16000, sample_width=2)
        assert result.is_silent is True
        assert result.should_submit is True
        assert result.duration_seconds >= 0.5

    def test_no_submit_short_silence(self):
        """No submit when silence is shorter than threshold."""
        svc = VoiceService.__new__(VoiceService)
        svc._settings = MagicMock()
        svc._config = VoiceConfig(
            silence_db_threshold=10.0, silence_duration=2.0,
        )
        svc._device_profiles = {}

        # Only 0.1 seconds of silence (amplitude 1 → ~5.69 dB, below 10.0)
        num_samples = 1600
        silent_bytes = struct.pack(f"<{num_samples}h", *([1] * num_samples))

        result = svc.detect_silence(silent_bytes, sample_rate=16000, sample_width=2)
        assert result.is_silent is True
        assert result.should_submit is False


class TestVoiceServiceConfig:
    """Test voice service config management."""

    def test_get_global_config(self):
        svc = VoiceService.__new__(VoiceService)
        svc._settings = MagicMock()
        svc._config = VoiceConfig()
        svc._device_profiles = {}

        cfg = svc.get_device_config()
        assert cfg.confidence_threshold == 0.9

    def test_set_device_config(self):
        svc = VoiceService.__new__(VoiceService)
        svc._settings = MagicMock()
        svc._config = VoiceConfig()
        svc._device_profiles = {}

        custom = VoiceConfig(confidence_threshold=0.85)
        svc.set_device_config("mic-1", custom)

        cfg = svc.get_device_config("mic-1")
        assert cfg.confidence_threshold == 0.85
        assert cfg.device_id == "mic-1"

    def test_update_config(self):
        svc = VoiceService.__new__(VoiceService)
        svc._settings = MagicMock()
        svc._config = VoiceConfig()
        svc._device_profiles = {}

        updated = svc.update_config(confidence_threshold=0.80, language="es")
        assert updated.confidence_threshold == 0.80
        assert updated.language == "es"


class TestTranscription:
    """Story 1.2 — Whisper STT transcription."""

    @pytest.mark.asyncio
    async def test_transcribe_with_ollama(self):
        svc = VoiceService.__new__(VoiceService)
        svc._settings = MagicMock()
        svc._settings.voice_model = "whisper"
        svc._settings.ollama_host = "http://localhost:11434"
        svc._config = VoiceConfig()
        svc._device_profiles = {}
        svc._ollama_url = "http://localhost:11434"
        svc._timeout = 60.0

        audio = b"fake audio wav data"

        with patch.object(svc, "_transcribe_via_ollama") as mock_ollama:
            mock_ollama.return_value = TranscriptionResult(
                text="test transcription", confidence=0.92,
                language="en", source="voice",
            )
            result = await svc.transcribe(audio)

        assert result.text == "test transcription"
        assert result.confidence == 0.92
        assert result.auto_accepted is True  # 0.92 > 0.90

    @pytest.mark.asyncio
    async def test_transcribe_fallback(self):
        svc = VoiceService.__new__(VoiceService)
        svc._settings = MagicMock()
        svc._settings.voice_model = "whisper"
        svc._config = VoiceConfig()
        svc._device_profiles = {}
        svc._ollama_url = "http://localhost:11434"
        svc._timeout = 60.0

        with patch.object(svc, "_transcribe_via_ollama", side_effect=RuntimeError("no whisper")):
            result = await svc.transcribe(b"audio data")

        assert result.text == ""
        assert result.confidence == 0.0

    @pytest.mark.asyncio
    async def test_transcribe_low_confidence_flags_re_speak(self):
        svc = VoiceService.__new__(VoiceService)
        svc._settings = MagicMock()
        svc._config = VoiceConfig(
            auto_accept_threshold=0.90,
            re_speak_threshold=0.80,
        )
        svc._device_profiles = {}
        svc._ollama_url = "http://localhost:11434"
        svc._timeout = 60.0

        with patch.object(svc, "_transcribe_via_ollama") as mock:
            mock.return_value = TranscriptionResult(
                text="unclear", confidence=0.65,
                language="en", source="voice",
            )
            result = await svc.transcribe(b"audio")

        assert result.needs_re_speak is True
        assert result.auto_accepted is False


class TestVoiceStatus:
    """Test Whisper availability check."""

    @pytest.mark.asyncio
    async def test_check_whisper_available(self):
        svc = VoiceService.__new__(VoiceService)
        svc._settings = MagicMock()
        svc._ollama_url = "http://localhost:11434"

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {
                "models": [
                    {"name": "qwen2.5:3b"},
                    {"name": "whisper:base"},
                ]
            }
            mock_client.get = AsyncMock(return_value=mock_resp)
            mock_client_cls.return_value = mock_client

            result = await svc.check_whisper_available()

        assert result["available"] is True
        assert "whisper:base" in result["models"]

    @pytest.mark.asyncio
    async def test_check_whisper_unavailable(self):
        svc = VoiceService.__new__(VoiceService)
        svc._settings = MagicMock()
        svc._ollama_url = "http://localhost:11434"

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.get = AsyncMock(side_effect=Exception("connection refused"))
            mock_client_cls.return_value = mock_client

            result = await svc.check_whisper_available()

        assert result["available"] is False
        assert result["ollama_reachable"] is False


# ═══════════════════════════════════════════════════════════
# VOICE ROUTES TESTS
# ═══════════════════════════════════════════════════════════


class TestVoiceRoutes:
    """Test voice API endpoints."""

    @pytest.mark.asyncio
    async def test_transcribe_endpoint(self, client):
        audio = base64.b64encode(b"fake audio").decode()
        with patch("app.routes.voice.voice_service") as mock_svc:
            mock_svc.transcribe = AsyncMock(return_value=TranscriptionResult(
                text="hello", confidence=0.95, language="en",
                duration_ms=100.0, source="voice",
                auto_accepted=True,
            ))
            resp = await client.post("/api/voice/transcribe", json={
                "audio_b64": audio,
            })
        assert resp.status_code == 200
        data = resp.json()
        assert data["text"] == "hello"
        assert data["confidence"] == 0.95
        assert data["auto_accepted"] is True

    @pytest.mark.asyncio
    async def test_transcribe_invalid_b64(self, client):
        resp = await client.post("/api/voice/transcribe", json={
            "audio_b64": "!!!invalid!!!",
        })
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_transcribe_empty_audio(self, client):
        audio = base64.b64encode(b"").decode()
        resp = await client.post("/api/voice/transcribe", json={
            "audio_b64": audio,
        })
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_silence_endpoint(self, client):
        # Generate silent PCM audio
        num_samples = 1600
        pcm = struct.pack(f"<{num_samples}h", *([1] * num_samples))
        audio = base64.b64encode(pcm).decode()

        resp = await client.post("/api/voice/silence", json={
            "audio_b64": audio,
            "sample_rate": 16000,
            "sample_width": 2,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "is_silent" in data
        assert "avg_db" in data

    @pytest.mark.asyncio
    async def test_get_config_endpoint(self, client):
        resp = await client.get("/api/voice/config")
        assert resp.status_code == 200
        data = resp.json()
        assert "confidence_threshold" in data
        assert "silence_db_threshold" in data

    @pytest.mark.asyncio
    async def test_update_config_endpoint(self, client):
        resp = await client.put("/api/voice/config", json={
            "confidence_threshold": 0.85,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["confidence_threshold"] == 0.85

    @pytest.mark.asyncio
    async def test_voice_status_endpoint(self, client):
        with patch("app.routes.voice.voice_service") as mock_svc:
            mock_svc.config = VoiceConfig()
            mock_svc.check_whisper_available = AsyncMock(return_value={
                "available": False, "models": [], "ollama_reachable": True,
            })
            resp = await client.get("/api/voice/status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["service"] == "operational"
        assert "whisper" in data
