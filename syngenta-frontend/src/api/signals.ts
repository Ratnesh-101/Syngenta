import { client, MOCK_MODE, mockDelay } from './client';
import { MOCK_ANOMALIES } from './mockData';
import type { Anomaly } from '../types';

export async function getAnomalies(): Promise<Anomaly[]> {
  if (MOCK_MODE) return mockDelay(MOCK_ANOMALIES);
  const { data } = await client.get<Anomaly[]>('/signals/anomalies');
  return data;
}
