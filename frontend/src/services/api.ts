const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface Voice {
  id: string;
  name: string;
  gender: 'male' | 'female';
  age: 'child' | 'young' | 'middle' | 'old';
  cloned?: boolean;
}

export interface SynthesisParams {
  text: string;
  voiceId: string;
  speed: number;
  pitch: number;
  volume: number;
  format: string;
  sampleRate: number;
}

export interface SynthesisResponse {
  taskId: string;
}

export interface TaskStatusResponse {
  status: 'pending' | 'processing' | 'completed' | 'failed';
  audioUrl?: string;
  waveform?: number[];
  error?: string;
}

async function fetchTyped<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE_URL}${url}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const errorText = await response.text().catch(() => 'Unknown error');
    throw new Error(`API error (${response.status}): ${errorText}`);
  }

  return response.json() as Promise<T>;
}

export async function getVoices(filters?: {
  gender?: 'male' | 'female';
  age?: 'child' | 'young' | 'middle' | 'old';
}): Promise<Voice[]> {
  const params = new URLSearchParams();
  if (filters?.gender) params.set('gender', filters.gender);
  if (filters?.age) params.set('age_group', filters.age);

  const queryString = params.toString();
  return fetchTyped<Voice[]>(`/api/voices${queryString ? `?${queryString}` : ''}`);
}

export async function synthesize(params: SynthesisParams): Promise<SynthesisResponse> {
  // Map camelCase to snake_case for backend
  // Convert UI ranges to backend ranges:
  // - pitch: UI -12..+12 → backend 0.5..2.0 (full range mapping)
  // - volume: UI 0..100% → backend 0.0..2.0
  const pitchMapped = 0.5 + ((params.pitch + 12) / 24) * 1.5; // -12→0.5, 0→1.25, +12→2.0
  const volumeMapped = (params.volume / 100) * 2.0;             // 0→0.0, 50→1.0, 100→2.0

  const body = {
    text: params.text,
    voice_id: params.voiceId,
    speed: params.speed,
    pitch: Math.max(0.5, Math.min(2.0, pitchMapped)),
    volume: Math.max(0.0, Math.min(2.0, volumeMapped)),
    format: params.format,
    sample_rate: params.sampleRate,
  };

  const result = await fetchTyped<{ success: boolean; data: { task_id: string }; error: string | null }>('/api/synthesize', {
    method: 'POST',
    body: JSON.stringify(body),
  });

  return { taskId: result.data.task_id };
}

export async function getTaskStatus(taskId: string): Promise<TaskStatusResponse> {
  const result = await fetchTyped<{ success: boolean; data: { status: string; result_url: string | null; error: string | null } }>
    (`/api/synthesize/${taskId}`);

  return {
    status: result.data.status as TaskStatusResponse['status'],
    audioUrl: result.data.result_url || undefined,
    error: result.data.error || undefined,
  };
}

export async function cloneVoice(file: File, voiceName: string, referenceText: string): Promise<{ taskId: string }> {
  const formData = new FormData();
  formData.append('audio_file', file);
  formData.append('voice_name', voiceName);
  formData.append('reference_text', referenceText);

  const response = await fetch(`${BASE_URL}/api/clone-voice`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorText = await response.text().catch(() => 'Unknown error');
    throw new Error(`Clone API error (${response.status}): ${errorText}`);
  }

  const result = await response.json();
  return { taskId: result.data.task_id };
}
