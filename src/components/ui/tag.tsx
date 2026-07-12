export interface TagProps {
  children: string;
}

export const Tag = ({ children }: TagProps) => {
  return (
    <span className="rounded-pill border border-border-strong px-[0.9em] py-[0.35em] font-mono text-[0.72rem] uppercase tracking-[0.08em] text-muted">
      {children}
    </span>
  );
};
