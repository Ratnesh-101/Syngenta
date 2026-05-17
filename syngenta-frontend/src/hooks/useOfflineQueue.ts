import { useState, useCallback, useEffect } from 'react';
import {
  getQueue,
  addToQueue,
  getPendingCount,
  markSynced,
  markFailed,
  clearSynced,
  type QueuedOutcome,
} from '../api/outcomes';
import { syncOutcomes } from '../api/outcomes';
import { useDevice } from './useDevice';
import type { OutcomeRecord } from '../types';

export interface SyncToast {
  id: string;
  type: 'success' | 'error' | 'info';
  message: string;
}

export function useOfflineQueue() {
  const { deviceId, deviceName, devicePlatform } = useDevice();
  const [pendingCount, setPendingCount] = useState(0);
  const [syncing, setSyncing] = useState(false);
  const [toasts, setToasts] = useState<SyncToast[]>([]);

  const refreshCount = useCallback(() => {
    setPendingCount(getPendingCount());
  }, []);

  useEffect(() => {
    refreshCount();
  }, [refreshCount]);

  const addToast = useCallback((type: SyncToast['type'], message: string) => {
    const id = crypto.randomUUID();
    setToasts((prev) => [...prev, { id, type, message }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  }, []);

  const dismissToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const enqueue = useCallback(
    (outcome: OutcomeRecord, entity_name?: string) => {
      addToQueue(outcome, entity_name);
      refreshCount();
    },
    [refreshCount]
  );

  const sync = useCallback(async () => {
    const pending = getQueue().filter((o: QueuedOutcome) => !o.synced);
    if (pending.length === 0) return;

    setSyncing(true);
    try {
      const result = await syncOutcomes(deviceId, deviceName, devicePlatform, pending);

      // Mark successes
      const successIds = result.results
        .filter((r) => r.status === 'created' || r.status === 'duplicate')
        .map((r) => r.client_outcome_id);
      if (successIds.length > 0) markSynced(successIds);

      // Mark failures
      const failIds = result.results
        .filter((r) => r.status === 'failed')
        .map((r) => r.client_outcome_id);
      if (failIds.length > 0) markFailed(failIds);

      clearSynced();

      if (result.created_count > 0) {
        addToast('success', `${result.created_count} outcome${result.created_count > 1 ? 's' : ''} synced successfully.`);
      }
      if (result.duplicate_count > 0) {
        addToast('info', `${result.duplicate_count} duplicate${result.duplicate_count > 1 ? 's' : ''} skipped.`);
      }
      if (result.failed_count > 0) {
        addToast('error', `${result.failed_count} outcome${result.failed_count > 1 ? 's' : ''} failed to sync.`);
      }
    } catch {
      addToast('error', 'Sync failed. Check your connection and try again.');
    } finally {
      setSyncing(false);
      refreshCount();
    }
  }, [deviceId, deviceName, devicePlatform, addToast, refreshCount]);

  // Auto-sync on load if there are pending items
  useEffect(() => {
    if (getPendingCount() > 0) {
      sync();
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  return { pendingCount, syncing, toasts, dismissToast, enqueue, sync, refreshCount };
}
