import { client, MOCK_MODE, mockDelay } from './client';
import { MOCK_PRIORITIES, MOCK_BRIEFS } from './mockData';
import { adaptPriorityGrower, adaptGrowerBrief } from './adapters';
import type { PriorityGrower, GrowerBrief } from '../types';

export async function getTodayPriorities(): Promise<PriorityGrower[]> {
  if (MOCK_MODE) return mockDelay(MOCK_PRIORITIES);
  try {
    const { data } = await client.get<unknown[]>('/visits/today');
    return data.map((g) => adaptPriorityGrower(g as Parameters<typeof adaptPriorityGrower>[0]));
  } catch (err: unknown) {
    // 403 = rep account not linked to a Syngenta rep_id. Return empty list so
    // the UI shows the friendly empty state instead of erroring.
    if (isAxios403(err)) return [];
    throw err;
  }
}

export async function getGrowerBrief(entity_id: string): Promise<GrowerBrief> {
  if (MOCK_MODE) {
    await mockDelay(null);
    const brief = MOCK_BRIEFS[entity_id];
    if (!brief) throw new Error('Grower not found');
    return brief;
  }
  const { data } = await client.get(`/visits/${entity_id}/brief`);
  return adaptGrowerBrief(data);
}

export async function getGrowerExplain(entity_id: string): Promise<{ explanation: string }> {
  if (MOCK_MODE) {
    return mockDelay({ explanation: 'This grower ranks highly due to a combination of purchase history, crop stress signals, and time since last visit.' });
  }
  const { data } = await client.get<{ explanation: string }>(`/visits/${entity_id}/explain`);
  return data;
}

function isAxios403(err: unknown): boolean {
  if (err && typeof err === 'object' && 'response' in err) {
    const r = (err as { response?: { status?: number } }).response;
    return r?.status === 403;
  }
  return false;
}