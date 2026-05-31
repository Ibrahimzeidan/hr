import { scoreTone } from "@/lib/utils";

export function ScoreRing({ score }: { score: number }) {
  const value = Math.round(score);
  return (
    <div className="relative grid h-14 w-14 place-items-center rounded-full bg-muted">
      <div
        className="absolute inset-0 rounded-full"
        style={{ background: `conic-gradient(hsl(var(--primary)) ${value * 3.6}deg, hsl(var(--muted)) 0deg)` }}
      />
      <div className="relative grid h-11 w-11 place-items-center rounded-full bg-card">
        <span className={`text-sm font-semibold ${scoreTone(score)}`}>{value}</span>
      </div>
    </div>
  );
}

