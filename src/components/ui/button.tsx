import { AnchorHTMLAttributes, ReactNode } from "react";

export interface ButtonProps extends AnchorHTMLAttributes<HTMLAnchorElement> {
  children: ReactNode;
  variant?: "primary" | "secondary";
}

export const Button = ({
  children,
  variant = "primary",
  className = "",
  ...props
}: ButtonProps) => {
  const base =
    "inline-flex items-center gap-[0.5em] rounded-card px-[1.5em] py-[0.9em] font-mono text-[0.85rem] uppercase tracking-[0.1em]";
  const variants = {
    primary: "bg-accent text-background hover:bg-foreground",
    secondary:
      "border border-border-strong text-foreground hover:border-accent hover:text-accent",
  };

  return (
    <a className={`${base} ${variants[variant]} ${className}`} {...props}>
      {children}
    </a>
  );
};
