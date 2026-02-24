/**
 * VoiceSettings — Configuration UI for voice thresholds.
 * Story 1.5: Confidence threshold slider (70–100%, default 90%).
 * Story 1.4: Silence detection thresholds.
 */
import { useState, useEffect, useCallback } from 'react';
import type { VoiceConfig } from '../types';
import { api } from '../services/api';

interface VoiceSettingsProps {
  className?: string;
}

export default function VoiceSettings({ className = '' }: VoiceSettingsProps) {
  const [config, setConfig] = useState<VoiceConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadConfig = useCallback(async () => {
    try {
      setLoading(true);
      const resp = await api.request<VoiceConfig>('/api/voice/config');
      setConfig(resp);
      setError(null);
    } catch (err) {
      setError('Failed to load voice configuration');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadConfig();
  }, [loadConfig]);

  const saveConfig = async (updates: Partial<VoiceConfig>) => {
    try {
      setSaving(true);
      const resp = await api.request<VoiceConfig>('/api/voice/config', {
        method: 'PUT',
        body: JSON.stringify(updates),
      });
      setConfig(resp);
      setError(null);
    } catch (err) {
      setError('Failed to save configuration');
    } finally {
      setSaving(false);
    }
  };

  const handleSliderChange = (field: keyof VoiceConfig, value: number) => {
    if (!config) return;
    const updated = { ...config, [field]: value };
    setConfig(updated);
  };

  const handleSave = () => {
    if (!config) return;
    saveConfig(config);
  };

  if (loading) return <div className="voice-settings__loading">Loading voice settings...</div>;

  if (!config)
    return (
      <div className="voice-settings__error">
        {error || 'Unable to load settings'}
        <button onClick={loadConfig}>Retry</button>
      </div>
    );

  return (
    <div className={`voice-settings ${className}`} data-testid="voice-settings">
      <h3>Voice Configuration</h3>

      {error && <div className="voice-settings__error">{error}</div>}

      <div className="voice-settings__group">
        <label>
          Confidence Threshold:{' '}
          <strong>{Math.round(config.confidence_threshold * 100)}%</strong>
        </label>
        <input
          type="range"
          min={70}
          max={100}
          value={Math.round(config.confidence_threshold * 100)}
          onChange={(e) =>
            handleSliderChange('confidence_threshold', parseInt(e.target.value) / 100)
          }
          data-testid="confidence-slider"
        />
        <span className="voice-settings__hint">
          Minimum confidence required to accept transcription
        </span>
      </div>

      <div className="voice-settings__group">
        <label>
          Auto-Accept Threshold:{' '}
          <strong>{Math.round(config.auto_accept_threshold * 100)}%</strong>
        </label>
        <input
          type="range"
          min={70}
          max={100}
          value={Math.round(config.auto_accept_threshold * 100)}
          onChange={(e) =>
            handleSliderChange('auto_accept_threshold', parseInt(e.target.value) / 100)
          }
          data-testid="auto-accept-slider"
        />
        <span className="voice-settings__hint">
          Auto-accept transcription above this confidence
        </span>
      </div>

      <div className="voice-settings__group">
        <label>
          Re-Speak Threshold:{' '}
          <strong>{Math.round(config.re_speak_threshold * 100)}%</strong>
        </label>
        <input
          type="range"
          min={50}
          max={90}
          value={Math.round(config.re_speak_threshold * 100)}
          onChange={(e) =>
            handleSliderChange('re_speak_threshold', parseInt(e.target.value) / 100)
          }
          data-testid="re-speak-slider"
        />
        <span className="voice-settings__hint">
          Prompt re-speak below this confidence
        </span>
      </div>

      <div className="voice-settings__group">
        <label>
          Silence Detection (dB):{' '}
          <strong>{config.silence_db_threshold} dB</strong>
        </label>
        <input
          type="range"
          min={1}
          max={20}
          step={0.5}
          value={config.silence_db_threshold}
          onChange={(e) =>
            handleSliderChange('silence_db_threshold', parseFloat(e.target.value))
          }
          data-testid="silence-db-slider"
        />
        <span className="voice-settings__hint">
          Sound below this level is considered silence
        </span>
      </div>

      <div className="voice-settings__group">
        <label>
          Silence Duration:{' '}
          <strong>{config.silence_duration}s</strong>
        </label>
        <input
          type="range"
          min={0.5}
          max={5}
          step={0.5}
          value={config.silence_duration}
          onChange={(e) =>
            handleSliderChange('silence_duration', parseFloat(e.target.value))
          }
          data-testid="silence-duration-slider"
        />
        <span className="voice-settings__hint">
          Auto-submit after this much silence
        </span>
      </div>

      <div className="voice-settings__group">
        <label>
          Max Recording:{' '}
          <strong>{config.max_recording_seconds}s</strong>
        </label>
        <input
          type="range"
          min={5}
          max={120}
          step={5}
          value={config.max_recording_seconds}
          onChange={(e) =>
            handleSliderChange('max_recording_seconds', parseInt(e.target.value))
          }
          data-testid="max-recording-slider"
        />
      </div>

      <button
        className="voice-settings__save"
        onClick={handleSave}
        disabled={saving}
        data-testid="voice-save-btn"
      >
        {saving ? 'Saving...' : 'Save Settings'}
      </button>
    </div>
  );
}
