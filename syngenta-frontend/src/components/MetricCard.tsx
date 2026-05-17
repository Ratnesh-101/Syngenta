interface Props {
  label: string;
  value: string | number;
  sub?: string;
  icon?: React.ReactNode;
  accent?: 'green' | 'harvest' | 'clay' | 'sage';
}

const accentStyles = {
  green:   'bg-forest-50 border-forest-100 text-forest-700',
  harvest: 'bg-harvest-50 border-harvest-100 text-harvest-700',
  clay:    'bg-clay-50 border-clay-100 text-clay-700',
  sage:    'bg-sage-50 border-sage-100 text-sage-700',
};

export default function MetricCard({ label, value, sub, icon, accent = 'green' }: Props) {
  return (
    <div className={`card p-4 border ${accentStyles[accent]}`}>
      <div className="flex items-start justify-between gap-2">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider opacity-70 mb-1">{label}</p>
          <p className="text-2xl font-bold font-display leading-none">{value}</p>
          {sub && <p className="text-xs mt-1 opacity-60">{sub}</p>}
        </div>
        {icon && (
          <div className="opacity-40">{icon}</div>
        )}
      </div>
    </div>
  );
}
