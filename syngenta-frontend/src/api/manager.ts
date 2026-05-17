import { client, MOCK_MODE, mockDelay } from './client';
import {
  MOCK_OVERVIEW,
  MOCK_REPS,
  MOCK_REP_DETAILS,
  MOCK_TOP_PRIORITIES,
} from './mockData';
import type { ManagerOverview, RepMetrics, RepDetails, TopPriority } from '../types';

export async function getManagerOverview(): Promise<ManagerOverview> {
  if (MOCK_MODE) return mockDelay(MOCK_OVERVIEW);
  const { data } = await client.get<ManagerOverview>('/manager/overview');
  return data;
}

export async function getManagerReps(): Promise<RepMetrics[]> {
  if (MOCK_MODE) return mockDelay(MOCK_REPS);
  const { data } = await client.get<RepMetrics[]>('/manager/reps');
  return data;
}

export async function getRepDetails(rep_id: string): Promise<RepDetails> {
  if (MOCK_MODE) {
    await mockDelay(null);
    const detail = MOCK_REP_DETAILS[rep_id];
    if (!detail) throw new Error('Rep not found');
    return detail;
  }
  const { data } = await client.get<RepDetails>(`/manager/reps/${rep_id}/details`);
  return data;
}

export async function getTopPriorities(limit = 10): Promise<TopPriority[]> {
  if (MOCK_MODE) return mockDelay(MOCK_TOP_PRIORITIES.slice(0, limit));
  const { data } = await client.get<TopPriority[]>(`/manager/priorities/top?limit=${limit}`);
  return data;
}
