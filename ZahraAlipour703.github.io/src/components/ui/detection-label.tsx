// Signature element: section eyebrows styled like an object-detection class
// label (class name + confidence score), since the subject's own work is
// building detectors. Kept quiet — mono type, small, one accent dot.

export interface DetectionLabelProps {
  /** The detection "class" name, e.g. "about", "research" */
  label: string;
  /** Optional confidence-style score, 0–1. Omit for a plain label. */
  confidence?: number;
  className?: string;
}

export const DetectionLabel = ({
  label,
  confidence,
  className = "",
}: DetectionLabelProps) => {
  return (
    <span
      className={`inline-flex items-center gap-[0.5em] font-mono text-[0.8rem] uppercase tracking-[0.18em] text-accent ${className}`}
    >
      <span className="h-[0.4em] w-[0.4em] rounded-full bg-accent" aria-hidden="true" />
      {label}
      {confidence !== undefined && (
        <span className="text-muted">{confidence.toFixed(2)}</span>
      )}
    </span>
  );
};
