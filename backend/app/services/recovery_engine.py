"""
JARVIS AI — 6-Level Error Recovery Engine.

Stories 3.1–3.6: Implements escalating recovery strategy chain.
Level 1: Timeout retry (exponential backoff)
Level 2: Alternative method
Level 3: Re-verification with screenshots
Level 4: Replan with SAA (LLM)
Level 5: User confirmation dialog
Level 6: Mark impossible
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Callable, Coroutine

logger = logging.getLogger("jarvis.recovery")


class RecoveryLevel(IntEnum):
    """Escalation levels in order."""
    L1_RETRY = 1
    L2_ALTERNATIVE = 2
    L3_REVERIFY = 3
    L4_REPLAN = 4
    L5_USER_CONFIRM = 5
    L6_IMPOSSIBLE = 6


@dataclass
class RecoveryAttempt:
    """Record of a single recovery attempt."""
    level: RecoveryLevel
    method: str
    success: bool
    duration_ms: float
    details: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    timestamp: float = field(default_factory=time.time)


@dataclass
class RecoveryResult:
    """Final result of the recovery process."""
    success: bool
    final_level: RecoveryLevel
    attempts: list[RecoveryAttempt]
    output: Any = None
    action_taken: str | None = None  # 'retry', 'skip', 'cancel', 'impossible'

    @property
    def total_duration_ms(self) -> float:
        return sum(a.duration_ms for a in self.attempts)


@dataclass
class RecoveryContext:
    """Context passed through recovery levels."""
    execution_id: str
    step_index: int
    agent_name: str
    action: str
    parameters: dict[str, Any]
    error: str
    workflow_id: str | None = None
    max_retries: int = 3
    base_timeout: float = 30.0
    backoff_multiplier: float = 1.5
    confidence_threshold: float = 0.75
    skippable: bool = True

    # Callbacks (injected by orchestrator)
    execute_fn: Callable[..., Coroutine] | None = None
    screenshot_fn: Callable[..., Coroutine] | None = None
    analyze_screenshot_fn: Callable[..., Coroutine] | None = None
    replan_fn: Callable[..., Coroutine] | None = None
    user_confirm_fn: Callable[..., Coroutine] | None = None
    notify_fn: Callable[..., Coroutine] | None = None


# Pre-configured alternative methods
ALTERNATIVE_METHODS: dict[str, list[str]] = {
    "npm": ["yarn", "pnpm"],
    "yarn": ["npm", "pnpm"],
    "pnpm": ["npm", "yarn"],
    "powershell": ["cmd", "bash"],
    "cmd": ["powershell", "bash"],
    "bash": ["powershell", "cmd"],
    "curl": ["wget", "invoke-webrequest"],
    "wget": ["curl", "invoke-webrequest"],
    "git": ["gh"],
    "gh": ["git"],
    "pip": ["pip3", "python -m pip"],
    "pip3": ["pip", "python -m pip"],
}


class RecoveryEngine:
    """
    Executes the 6-level recovery escalation chain.

    Usage:
        engine = RecoveryEngine()
        result = await engine.recover(context)

    The engine tries each level in order. If a level succeeds, it stops.
    If all levels fail, returns result with action_taken='impossible'.
    """

    def __init__(self):
        self._metrics: dict[str, int] = {
            "l1_attempts": 0, "l1_successes": 0,
            "l2_attempts": 0, "l2_successes": 0,
            "l3_attempts": 0, "l3_successes": 0,
            "l4_attempts": 0, "l4_successes": 0,
            "l5_attempts": 0, "l5_successes": 0,
            "l6_triggers": 0,
        }

    async def recover(self, ctx: RecoveryContext) -> RecoveryResult:
        """Execute escalating recovery from L1 through L6."""
        attempts: list[RecoveryAttempt] = []

        # L1: Timeout retry with exponential backoff
        attempt = await self._l1_retry(ctx)
        attempts.append(attempt)
        if attempt.success:
            return RecoveryResult(True, RecoveryLevel.L1_RETRY, attempts, output=attempt.details.get("output"))

        # L2: Alternative method
        attempt = await self._l2_alternative(ctx)
        attempts.append(attempt)
        if attempt.success:
            return RecoveryResult(True, RecoveryLevel.L2_ALTERNATIVE, attempts, output=attempt.details.get("output"))

        # L3: Re-verification
        attempt = await self._l3_reverify(ctx)
        attempts.append(attempt)
        if attempt.success:
            return RecoveryResult(True, RecoveryLevel.L3_REVERIFY, attempts, output=attempt.details.get("output"))

        # L4: Replan with SAA
        attempt = await self._l4_replan(ctx)
        attempts.append(attempt)
        if attempt.success:
            return RecoveryResult(True, RecoveryLevel.L4_REPLAN, attempts, output=attempt.details.get("output"))

        # L5: User confirmation
        attempt = await self._l5_user_confirm(ctx)
        attempts.append(attempt)
        if attempt.success:
            return RecoveryResult(
                True, RecoveryLevel.L5_USER_CONFIRM, attempts,
                output=attempt.details.get("output"),
                action_taken=attempt.details.get("user_choice", "retry"),
            )

        # L6: Mark impossible
        attempt = await self._l6_impossible(ctx)
        attempts.append(attempt)
        return RecoveryResult(
            False, RecoveryLevel.L6_IMPOSSIBLE, attempts,
            action_taken="impossible",
        )

    async def _l1_retry(self, ctx: RecoveryContext) -> RecoveryAttempt:
        """Level 1: Retry with exponential backoff."""
        self._metrics["l1_attempts"] += 1
        start = time.time()

        if not ctx.execute_fn:
            return RecoveryAttempt(
                RecoveryLevel.L1_RETRY, "retry", False, 0,
                error="No execute function provided",
            )

        timeout = ctx.base_timeout
        for attempt_num in range(1, ctx.max_retries + 1):
            logger.info(
                "L1 retry attempt %d/%d for %s.%s (timeout: %.1fs)",
                attempt_num, ctx.max_retries, ctx.agent_name, ctx.action, timeout,
            )
            if ctx.notify_fn:
                await ctx.notify_fn({
                    "type": "recovery",
                    "level": 1,
                    "message": f"Retrying... (Attempt {attempt_num}/{ctx.max_retries})",
                    "execution_id": ctx.execution_id,
                    "step_index": ctx.step_index,
                })

            try:
                result = await asyncio.wait_for(
                    ctx.execute_fn(ctx.agent_name, ctx.action, ctx.parameters),
                    timeout=timeout,
                )
                self._metrics["l1_successes"] += 1
                duration = (time.time() - start) * 1000
                return RecoveryAttempt(
                    RecoveryLevel.L1_RETRY, "retry", True, duration,
                    details={"output": result, "attempt": attempt_num},
                )
            except Exception as e:
                logger.warning("L1 retry %d failed: %s", attempt_num, str(e))
                timeout *= ctx.backoff_multiplier

        duration = (time.time() - start) * 1000
        return RecoveryAttempt(
            RecoveryLevel.L1_RETRY, "retry", False, duration,
            error=f"All {ctx.max_retries} retries failed",
        )

    async def _l2_alternative(self, ctx: RecoveryContext) -> RecoveryAttempt:
        """Level 2: Try alternative methods."""
        self._metrics["l2_attempts"] += 1
        start = time.time()

        if not ctx.execute_fn:
            return RecoveryAttempt(
                RecoveryLevel.L2_ALTERNATIVE, "alternative", False, 0,
                error="No execute function provided",
            )

        # Find alternatives based on action name
        action_lower = ctx.action.lower()
        alternatives = []
        for key, alts in ALTERNATIVE_METHODS.items():
            if key in action_lower:
                alternatives = alts
                break

        if not alternatives:
            duration = (time.time() - start) * 1000
            return RecoveryAttempt(
                RecoveryLevel.L2_ALTERNATIVE, "alternative", False, duration,
                error="No alternative methods available",
            )

        for alt in alternatives:
            alt_action = ctx.action.replace(action_lower, alt)
            logger.info("L2 trying alternative: %s → %s", ctx.action, alt_action)

            if ctx.notify_fn:
                await ctx.notify_fn({
                    "type": "recovery",
                    "level": 2,
                    "message": f"Trying alternative: {alt}",
                    "execution_id": ctx.execution_id,
                    "step_index": ctx.step_index,
                })

            try:
                result = await asyncio.wait_for(
                    ctx.execute_fn(ctx.agent_name, alt_action, ctx.parameters),
                    timeout=ctx.base_timeout * 2,
                )
                self._metrics["l2_successes"] += 1
                duration = (time.time() - start) * 1000
                return RecoveryAttempt(
                    RecoveryLevel.L2_ALTERNATIVE, f"alt:{alt}", True, duration,
                    details={"output": result, "alternative": alt},
                )
            except Exception as e:
                logger.warning("L2 alternative %s failed: %s", alt, str(e))

        duration = (time.time() - start) * 1000
        return RecoveryAttempt(
            RecoveryLevel.L2_ALTERNATIVE, "alternative", False, duration,
            error="All alternatives failed",
        )

    async def _l3_reverify(self, ctx: RecoveryContext) -> RecoveryAttempt:
        """Level 3: Re-verification with screenshots."""
        self._metrics["l3_attempts"] += 1
        start = time.time()

        if not ctx.screenshot_fn or not ctx.analyze_screenshot_fn:
            return RecoveryAttempt(
                RecoveryLevel.L3_REVERIFY, "reverify", False, 0,
                error="Screenshot functions not available",
            )

        try:
            if ctx.notify_fn:
                await ctx.notify_fn({
                    "type": "recovery",
                    "level": 3,
                    "message": "Re-verifying with screenshot analysis...",
                    "execution_id": ctx.execution_id,
                    "step_index": ctx.step_index,
                })

            screenshot = await ctx.screenshot_fn(ctx.execution_id, ctx.step_index)
            analysis = await ctx.analyze_screenshot_fn(screenshot, ctx.action)

            confidence = analysis.get("confidence", 0.0)
            logger.info("L3 re-verification confidence: %.2f (threshold: %.2f)", confidence, ctx.confidence_threshold)

            if confidence >= ctx.confidence_threshold:
                self._metrics["l3_successes"] += 1
                duration = (time.time() - start) * 1000
                return RecoveryAttempt(
                    RecoveryLevel.L3_REVERIFY, "reverify", True, duration,
                    details={"output": analysis, "confidence": confidence},
                )

            duration = (time.time() - start) * 1000
            return RecoveryAttempt(
                RecoveryLevel.L3_REVERIFY, "reverify", False, duration,
                error=f"Confidence {confidence:.2f} below threshold {ctx.confidence_threshold}",
                details={"confidence": confidence},
            )
        except Exception as e:
            duration = (time.time() - start) * 1000
            return RecoveryAttempt(
                RecoveryLevel.L3_REVERIFY, "reverify", False, duration,
                error=str(e),
            )

    async def _l4_replan(self, ctx: RecoveryContext) -> RecoveryAttempt:
        """Level 4: Replan with SAA (LLM-based replanning)."""
        self._metrics["l4_attempts"] += 1
        start = time.time()

        if not ctx.replan_fn:
            return RecoveryAttempt(
                RecoveryLevel.L4_REPLAN, "replan", False, 0,
                error="Replan function not available",
            )

        try:
            if ctx.notify_fn:
                await ctx.notify_fn({
                    "type": "recovery",
                    "level": 4,
                    "message": "Replanning approach with AI analysis...",
                    "execution_id": ctx.execution_id,
                    "step_index": ctx.step_index,
                })

            new_plan = await ctx.replan_fn(
                ctx.agent_name, ctx.action, ctx.parameters, ctx.error
            )

            if not new_plan or not new_plan.get("steps"):
                duration = (time.time() - start) * 1000
                return RecoveryAttempt(
                    RecoveryLevel.L4_REPLAN, "replan", False, duration,
                    error="SAA could not generate alternative plan",
                )

            # Execute each step in the new plan
            for step in new_plan["steps"]:
                try:
                    result = await asyncio.wait_for(
                        ctx.execute_fn(
                            step.get("agent", ctx.agent_name),
                            step.get("action", "execute"),
                            step.get("parameters", {}),
                        ),
                        timeout=ctx.base_timeout * 2,
                    )
                except Exception as step_error:
                    logger.warning("L4 replan step failed: %s", str(step_error))
                    duration = (time.time() - start) * 1000
                    return RecoveryAttempt(
                        RecoveryLevel.L4_REPLAN, "replan", False, duration,
                        error=f"Replan step failed: {str(step_error)}",
                    )

            self._metrics["l4_successes"] += 1
            duration = (time.time() - start) * 1000
            return RecoveryAttempt(
                RecoveryLevel.L4_REPLAN, "replan", True, duration,
                details={"output": result, "plan": new_plan},
            )
        except Exception as e:
            duration = (time.time() - start) * 1000
            return RecoveryAttempt(
                RecoveryLevel.L4_REPLAN, "replan", False, duration,
                error=str(e),
            )

    async def _l5_user_confirm(self, ctx: RecoveryContext) -> RecoveryAttempt:
        """Level 5: Ask user what to do (retry/skip/cancel)."""
        self._metrics["l5_attempts"] += 1
        start = time.time()

        if not ctx.user_confirm_fn:
            # If no user confirmation handler, auto-skip if skippable
            duration = (time.time() - start) * 1000
            if ctx.skippable:
                return RecoveryAttempt(
                    RecoveryLevel.L5_USER_CONFIRM, "auto-skip", True, duration,
                    details={"user_choice": "skip"},
                )
            return RecoveryAttempt(
                RecoveryLevel.L5_USER_CONFIRM, "user_confirm", False, duration,
                error="No user confirmation handler and step not skippable",
            )

        try:
            if ctx.notify_fn:
                await ctx.notify_fn({
                    "type": "recovery",
                    "level": 5,
                    "message": "Waiting for user decision...",
                    "execution_id": ctx.execution_id,
                    "step_index": ctx.step_index,
                    "options": ["retry", "skip", "cancel"],
                })

            user_choice = await ctx.user_confirm_fn(
                ctx.execution_id, ctx.step_index, ctx.error
            )

            choice = user_choice.get("action", "cancel")
            duration = (time.time() - start) * 1000

            if choice == "retry":
                # Re-run L1
                retry_result = await self._l1_retry(ctx)
                if retry_result.success:
                    self._metrics["l5_successes"] += 1
                    return RecoveryAttempt(
                        RecoveryLevel.L5_USER_CONFIRM, "user-retry", True, duration + retry_result.duration_ms,
                        details={"output": retry_result.details.get("output"), "user_choice": "retry"},
                    )
                return RecoveryAttempt(
                    RecoveryLevel.L5_USER_CONFIRM, "user-retry", False, duration + retry_result.duration_ms,
                    error="User retry also failed",
                    details={"user_choice": "retry"},
                )

            if choice == "skip" and ctx.skippable:
                self._metrics["l5_successes"] += 1
                return RecoveryAttempt(
                    RecoveryLevel.L5_USER_CONFIRM, "user-skip", True, duration,
                    details={"user_choice": "skip"},
                )

            return RecoveryAttempt(
                RecoveryLevel.L5_USER_CONFIRM, "user-cancel", False, duration,
                details={"user_choice": choice},
            )
        except Exception as e:
            duration = (time.time() - start) * 1000
            return RecoveryAttempt(
                RecoveryLevel.L5_USER_CONFIRM, "user_confirm", False, duration,
                error=str(e),
            )

    async def _l6_impossible(self, ctx: RecoveryContext) -> RecoveryAttempt:
        """Level 6: Mark step as impossible."""
        self._metrics["l6_triggers"] += 1
        start = time.time()

        logger.error(
            "L6 IMPOSSIBLE: Step %d (%s.%s) in execution %s",
            ctx.step_index, ctx.agent_name, ctx.action, ctx.execution_id,
        )

        if ctx.notify_fn:
            await ctx.notify_fn({
                "type": "recovery",
                "level": 6,
                "message": f"✗ Step {ctx.step_index + 1} cannot complete. Marking as impossible.",
                "execution_id": ctx.execution_id,
                "step_index": ctx.step_index,
                "options": ["try_manually", "abort", "save_for_later"],
            })

        duration = (time.time() - start) * 1000
        return RecoveryAttempt(
            RecoveryLevel.L6_IMPOSSIBLE, "mark_impossible", False, duration,
            details={
                "agent": ctx.agent_name,
                "action": ctx.action,
                "suggestion": "Check system state and try manually, or abort the workflow.",
            },
        )

    @property
    def metrics(self) -> dict[str, int]:
        """Return recovery metrics for analytics."""
        return dict(self._metrics)


# Singleton
recovery_engine = RecoveryEngine()
