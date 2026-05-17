import { client, MOCK_MODE, mockDelay } from './client';
import { MOCK_PRIORITIES, MOCK_BRIEFS } from './mockData';
import type { PriorityGrower, GrowerBrief } from '../types';

export async function getTodayPriorities(): Promise<PriorityGrower[]> {
  if (MOCK_MODE) return mockDelay(MOCK_PRIORITIES);
  const { data } = await client.get<PriorityGrower[]>('/visits/today');
  return data;
}

export async function getGrowerBrief(entity_id: string): Promise<GrowerBrief> {
  if (MOCK_MODE) {
    await mockDelay(null);
    const brief = MOCK_BRIEFS[entity_id];
    if (!brief) throw new Error('Grower not found');
    return brief;
  }
  const { data } = await client.get<GrowerBrief>(`/visits/${entity_id}/brief`);
  return data;
}

export async function getGrowerExplain(entity_id: string): Promise<{ explanation: string }> {
  if (MOCK_MODE) {
    return mockDelay({ explanation: 'This grower ranks highly due to a combination of purchase history, crop stress signals, and time since last visit.' });
  }
  const { data } = await client.get<{ explanation: string }>(`/visits/${entity_id}/explain`);
  return data;
}
