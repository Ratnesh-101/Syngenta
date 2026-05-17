import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import Header from '../../components/Header';
import { getWeightsHistory, type WeightsSnapshot } from '../../api/manager';

const SIGNAL_LABELS: Record<string, string> = {
  pest_alert_severity: 'Pest Alert',
  inventory_shortage_level: 'Inventory Shortage',
  days_since_last_visit: 'Days Since Visit',
  weather_risk_score: 'Weather Risk',
  complaint_open: 'Open Complaint',
  crop_stage_sensitivity: 'Crop Stage',
  revenue_potential: 'Revenue Potential',
  competitor_activity: 'Competitor Activity',
};

function fmt(val: number) {
  return (val * 100).toFixed(1) + '%';
}

function DeltaBadge({ value }: { value: number }) {
  const positive = value > 0;
  const label = (positive ? '+' : '') + (value * 100).toFixed(1) + '%';
  return (
    <span
      className={`inline-flex items-center gap-0.5 text-xs font-semibold px-1.5 py-0.5 rounded-md ${
        positive
          ? 'bg-forest-50 text-forest-700'
          : 'bg-clay-50 text-clay-600'
      }`}
    >
      {positive ? '▲' : '▼'} {label}
    </span>
  );
}

function SnapshotCard({ snap, index }: { snap: WeightsSnapshot; index: number }) {
  const [expanded, setExpanded] = useState(index === 0);
  const date = new Date(snap.created_at).toLocaleString('en-IN', {
    day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit',
  });
  const hasDelta = snap.delta && Object.keys(snap.delta).length > 0;
  const isManual = snap.trigger === 'manual_recalibration';

  return (
    <div className="card overflow-hidden">
      {/* Card header */}
      <button
        onClick={() => setExpanded((p) => !p)}
        className="w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-forest-50 transition-colors"
      >
        <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 text-xs font-bold ${
          isManual ? 'bg-harvest-100 text-harvest-700' : 'bg-forest-100 text-forest-700'
        }`}>
          #{snap.id}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-sm font-semibold text-forest-900">
              {isManual ? 'Manual recalibration' : `Outcome #${snap.outcome_id} logged`}
            </span>
            {hasDelta && (
              <span className="text-xs text-sage-500">
                {Object.keys(snap.delta!).length} signal{Object.keys(snap.delta!).length > 1 ? 's' : ''} shifted
              </span>
            )}
          </div>
          <p className="text-xs text-sage-500 mt-0.5">{date}</p>
        </div>
        <svg
          className={`w-4 h-4 text-sage-400 shrink-0 transition-transform ${expanded ? 'rotate-180' : ''}`}
          fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Expanded body */}
      {expanded && (
        <div className="border-t border-forest-50 px-4 py-3 space-y-3">
          {/* Delta highlights */}
          {hasDelta && (
            <div>
              <p className="text-xs font-semibold text-sage-500 uppercase tracking-wide mb-2">What changed</p>
              <div className="space-y-1.5">
                {Object.entries(snap.delta!).map(([key, val]) => (
                  <div key={key} className="flex items-center justify-between">
                    <span className="text-xs text-forest-800">{SIGNAL_LABELS[key] ?? key}</span>
                    <DeltaBadge value={val} />
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Full weights */}
          <div>
            <p className="text-xs font-semibold text-sage-500 uppercase tracking-wide mb-2">All weights at this point</p>
            <div className="space-y-2">
              {Object.entries(snap.weights)
                .sort(([, a], [, b]) => b - a)
                .map(([key, val]) => {
                  const deltaVal = snap.delta?.[key];
                  return (
                    <div key={key}>
                      <div className="flex items-center justify-between mb-0.5">
                        <span className="text-xs text-forest-700">{SIGNAL_LABELS[key] ?? key}</span>
                        <div className="flex items-center gap-2">
                          {deltaVal !== undefined && <DeltaBadge value={deltaVal} />}
                          <span className="text-xs font-semibold text-forest-900">{fmt(val)}</span>
                        </div>
                      </div>
                      <div className="h-1.5 bg-sage-100 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-forest-600 rounded-full transition-all"
                          style={{ width: `${(val * 100).toFixed(1)}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function WeightsHistory() {
  const [snapshots, setSnapshots] = useState<WeightsSnapshot[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    getWeightsHistory(20)
      .then(setSnapshots)
      .catch(() => setError('Failed to load weights history.'))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-screen bg-forest-50">
      <Header title="Learning Trail" showBack />
      <div className="max-w-2xl mx-auto px-4 py-6 space-y-4">
        {/* Page intro */}
        <div className="card px-4 py-3">
          <p className="text-sm text-forest-800 font-semibold">How the model learns</p>
          <p className="text-xs text-sage-500 mt-0.5">
            Each time an outcome is logged, signal weights are recalculated. This trail shows every adjustment — which signals gained importance, which lost it, and what triggered the change.
          </p>
        </div>

        {/* Link back to overview */}
        <div className="flex justify-end">
          <Link to="/manager" className="text-xs text-forest-600 font-semibold hover:underline">
            ← Back to Overview
          </Link>
        </div>

        {loading && (
          <div className="flex justify-center py-12">
            <div className="w-7 h-7 border-2 border-forest-700 border-t-transparent rounded-full animate-spin" />
          </div>
        )}

        {error && (
          <div className="card px-4 py-3 text-sm text-clay-600">{error}</div>
        )}

        {!loading && !error && snapshots.length === 0 && (
          <div className="card px-4 py-6 text-center text-sm text-sage-500">
            No weight snapshots yet. Log some outcomes to see the model learn.
          </div>
        )}

        {snapshots.map((snap, i) => (
          <SnapshotCard key={snap.id} snap={snap} index={i} />
        ))}
      </div>
    </div>
  );
}