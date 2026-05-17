import { client } from './client';
import type { OutcomeRecord, SyncResponse } from '../types';

const QUEUE_KEY = 'pending_outcomes';

// ─── Online single record ─────────────────────────────────────────────────────

export async function recordOutcome(outcome: OutcomeRecord): Promise<void> {
  await client.post('/outcomes/record', outcome);
}

// ─── Bulk sync ────────────────────────────────────────────────────────────────

export async function syncOutcomes(
  device_id: string,
  device_name: string,
  device_platform: string,
  outcomes: OutcomeRecord[]
): Promise<SyncResponse> {
  const { data } = await client.post<SyncResponse>('/outcomes/sync', {
    device_id,
    device_name,
    device_platform,
    outcomes,
  });
  return data;
}

// ─── Local queue helpers ──────────────────────────────────────────────────────

export interface QueuedOutcome extends OutcomeRecord {
  synced: boolean;
  entity_name?: string;
  failed?: boolean;
}

export function getQueue(): QueuedOutcome[] {
  try {
    const raw = localStorage.getItem(QUEUE_KEY);
    if (!raw) return [];
    return JSON.parse(raw) as QueuedOutcome[];
  } catch {
    return [];
  }
}

export function saveQueue(queue: QueuedOutcome[]): void {
  localStorage.setItem(QUEUE_KEY, JSON.stringify(queue));
}

export function addToQueue(outcome: OutcomeRecord, entity_name?: string): void {
  const queue = getQueue();
  queue.push({ ...outcome, synced: false, entity_name });
  saveQueue(queue);
}

export function getPendingCount(): number {
  return getQueue().filter((o) => !o.synced).length;
}

export function markSynced(client_outcome_ids: string[]): void {
  const queue = getQueue().map((o) =>
    client_outcome_ids.includes(o.client_outcome_id) ? { ...o, synced: true } : o
  );
  saveQueue(queue);
}

export function markFailed(client_outcome_ids: string[]): void {
  const queue = getQueue().map((o) =>
    client_outcome_ids.includes(o.client_outcome_id) ? { ...o, failed: true } : o
  );
  saveQueue(queue);
}

export function clearSynced(): void {
  const queue = getQueue().filter((o) => !o.synced);
  saveQueue(queue);
}
