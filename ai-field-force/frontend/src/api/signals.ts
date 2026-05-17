import { client, MOCK_MODE, mockDelay } from './client';
import { MOCK_ANOMALIES } from './mockData';
import { adaptAnomalies } from './adapters';
import type { Anomaly } from '../types';

export async function getAnomalies(): Promise<Anomaly[]> {
  if (MOCK_MODE) return mockDelay(MOCK_ANOMALIES);
  try {
    const { data } = await client.get('/signals/anomalies');
    return adaptAnomalies(data);
  } catch (err: unknown) {
    // 403 for not-linked accounts → empty list, friendly UI
    if (err && typeof err === 'object' && 'response' in err) {
      const r = (err as { response?: { status?: number } }).response;
      if (r?.status === 403) return [];
    }
    throw err;
  }
}