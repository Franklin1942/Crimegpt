const TONES: Record<string, string> = {
  open: 'bg-blue-100 text-blue-700',
  in_progress: 'bg-amber-100 text-amber-700',
  pending: 'bg-slate-200 text-slate-700',
  closed: 'bg-emerald-100 text-emerald-700',
  low: 'bg-slate-200 text-slate-700',
  medium: 'bg-blue-100 text-blue-700',
  high: 'bg-orange-100 text-orange-700',
  critical: 'bg-red-100 text-red-700',
};

export default function Badge({ value }: { value: string }) {
  const tone = TONES[value] ?? 'bg-slate-200 text-slate-700';
  return (
    <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium capitalize ${tone}`}>
      {value.replace(/_/g, ' ')}
    </span>
  );
}
