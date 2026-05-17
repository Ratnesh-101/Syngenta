interface Props {
  score: number;
}

function scoreLabel(score: number): { label: string; color: string; ring: string; bg: string } {
  if (score >= 75) return {
    label: 'Healthy',
    color: 'text-forest-700',
    ring: 'stroke-forest-500',
    bg: 'bg-forest-50',
  };
  if (score >= 50) return {
    label: 'Moderate',
    color: 'text-harvest-700',
    ring: 'stroke-harvest-500',
    bg: 'bg-harvest-50',
  };
  return {
    label: 'At Risk',
    color: 'text-clay-700',
    ring: 'stroke-clay-500',
    bg: 'bg-clay-50',
  };
}

export default function HealthScoreCard({ score }: Props) {
  const { label, color, ring, bg } = scoreLabel(score);
  const circumference = 2 * Math.PI * 40; // r=40
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className={`card p-6 ${bg}`}>
      <div className="flex items-center gap-6">
        {/* Radial gauge */}
        <div className="relative shrink-0">
          <svg width="96" height="96" viewBox="0 0 96 96" className="-rotate-90">
            <circle cx="48" cy="48" r="40" fill="none" stroke="currentColor" strokeWidth="8" className="text-white opacity-60" />
            <circle
              cx="48"
              cy="48"
              r="40"
              fill="none"
              strokeWidth="8"
              strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={offset}
              className={ring}
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className={`text-3xl font-bold font-display leading-none ${color}`}>{score}</span>
            <span className="text-[10px] text-sage-400 font-semibold uppercase tracking-wide mt-0.5">/ 100</span>
          </div>
        </div>

        {/* Labels */}
        <div>
          <p className="text-xs font-semibold text-sage-500 uppercase tracking-wider mb-1">Territory Health</p>
          <p className={`text-2xl font-bold font-display ${color}`}>{label}</p>
          <p className="text-xs text-sage-500 mt-1">
            {score >= 75
              ? 'Field operations running well.'
              : score >= 50
              ? 'Some growers need attention.'
              : 'Multiple high-priority issues detected.'}
          </p>
        </div>
      </div>
    </div>
  );
}
