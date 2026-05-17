import { client, MOCK_MODE, mockDelay } from './client';
import {
  MOCK_OVERVIEW,
  MOCK_REPS,
  MOCK_REP_DETAILS,
  MOCK_TOP_PRIORITIES,
} from './mockData';
import {
  adaptManagerOverview,
  adaptRepMetrics,
  adaptRepDetails,
  adaptTopPriority,
} from './adapters';
import type { ManagerOverview, RepMetrics, RepDetails, TopPriority } from '../types';

export async function getManagerOverview(): Promise<ManagerOverview> {
  if (MOCK_MODE) return mockDelay(MOCK_OVERVIEW);
  const { data } = await client.get('/manager/overview');
  return adaptManagerOverview(data);
}

export async function getManagerReps(): Promise<RepMetrics[]> {
  if (MOCK_MODE) return mockDelay(MOCK_REPS);
  const { data } = await client.get<unknown[]>('/manager/reps');
  return data.map((r) => adaptRepMetrics(r as Parameters<typeof adaptRepMetrics>[0]));
}

export async function getRepDetails(rep_id: string): Promise<RepDetails> {
  if (MOCK_MODE) {
    await mockDelay(null);
    const detail = MOCK_REP_DETAILS[rep_id];
    if (!detail) throw new Error('Rep not found');
    return detail;
  }

  const [detailsRes, metricsRes] = await Promise.all([
    client.get(`/manager/reps/${rep_id}/details`),
    client.get<unknown[]>('/manager/reps').catch(() => ({ data: [] as unknown[] })),
  ]);

  const matching = (metricsRes.data as unknown[])
    .map((r) => adaptRepMetrics(r as Parameters<typeof adaptRepMetrics>[0]))
    .find((r) => r.rep_id === rep_id);

  return adaptRepDetails(detailsRes.data, matching);
}

export async function getTopPriorities(limit = 10): Promise<TopPriority[]> {
  if (MOCK_MODE) return mockDelay(MOCK_TOP_PRIORITIES.slice(0, limit));
  const { data } = await client.get<unknown[]>(`/manager/priorities/top?limit=${limit}`);
  return data.map((t) => adaptTopPriority(t as Parameters<typeof adaptTopPriority>[0]));
}

// ─── Weights ──────────────────────────────────────────────────────────────────

export interface WeightsSnapshot {
  id: number;
  rep_id: string;
  trigger: string;
  outcome_id: number | null;
  weights: Record<string, number>;
  delta: Record<string, number> | null;
  created_at: string;
}

export async function getWeightsHistory(limit = 20): Promise<WeightsSnapshot[]> {
  const { data } = await client.get<WeightsSnapshot[]>(`/weights/history?limit=${limit}`);
  return data;
}