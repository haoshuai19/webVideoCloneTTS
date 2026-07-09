import { useState, useCallback, useRef } from 'react';
import { synthesize, getTaskStatus, type TaskStatusResponse } from '../services/api';

type SynthesisStatus = 'idle' | 'synthesizing' | 'completed' | 'failed' | 'playing';

interface UseSynthesisReturn {
  status: SynthesisStatus;
  audioUrl: string | null;
  taskStatus: string;
  waveform: number[] | null;
  error: string | null;
  synthesize: (
    text: string,
    voiceId: string,
    speed: number,
    pitch: number,
    volume: number,
    format: string,
    sampleRate: number
  ) => Promise<void>;
  reset: () => void;
}

function generateFakeWaveform(length: number = 64): number[] {
  const waveform: number[] = [];
  for (let i = 0; i < length; i++) {
    const base = Math.sin(i * 0.3) * 0.5 + 0.5;
    const noise = Math.random() * 0.3;
    waveform.push(Math.min(1, Math.max(0.05, base + noise)));
  }
  return waveform;
}

export function useSynthesis(): UseSynthesisReturn {
  const [status, setStatus] = useState<SynthesisStatus>('idle');
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [taskStatus, setTaskStatus] = useState<string>('');
  const [waveform, setWaveform] = useState<number[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const clearPolling = useCallback(() => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
      pollingRef.current = null;
    }
  }, []);

  const pollTaskStatus = useCallback(async (taskId: string) => {
    clearPolling();

    pollingRef.current = setInterval(async () => {
      try {
        const result: TaskStatusResponse = await getTaskStatus(taskId);
        setTaskStatus(result.status);

        if (result.status === 'completed') {
          clearPolling();
          setAudioUrl(result.audioUrl || null);
          setWaveform(result.waveform || generateFakeWaveform());
          setStatus('completed');
        } else if (result.status === 'failed') {
          clearPolling();
          setError(result.error || 'Synthesis failed');
          setStatus('failed');
        }
      } catch (err) {
        clearPolling();
        setError(err instanceof Error ? err.message : 'Failed to check task status');
        setStatus('failed');
      }
    }, 1000);
  }, [clearPolling]);

  const handleSynthesize = useCallback(
    async (
      text: string,
      voiceId: string,
      speed: number,
      pitch: number,
      volume: number,
      format: string,
      sampleRate: number
    ) => {
      clearPolling();
      setStatus('synthesizing');
      setTaskStatus('pending');
      setError(null);
      setAudioUrl(null);
      setWaveform(null);

      try {
        const response = await synthesize({
          text,
          voiceId,
          speed,
          pitch,
          volume,
          format,
          sampleRate,
        });

        await pollTaskStatus(response.taskId);
      } catch (err) {
        clearPolling();
        setError(err instanceof Error ? err.message : 'Synthesis request failed');
        setStatus('failed');
      }
    },
    [clearPolling, pollTaskStatus]
  );

  const reset = useCallback(() => {
    clearPolling();
    setStatus('idle');
    setAudioUrl(null);
    setTaskStatus('');
    setWaveform(null);
    setError(null);
  }, [clearPolling]);

  return {
    status,
    audioUrl,
    taskStatus,
    waveform,
    error,
    synthesize: handleSynthesize,
    reset,
  };
}
