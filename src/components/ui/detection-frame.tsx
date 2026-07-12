"use client";

// Signature element: four corner brackets, like an object-detection bounding
// box drawn around a card or image. Springs open on hover via the animation
// system (no CSS transitions/keyframes — hard rule #1).

import { Hover } from "@/components/animation/springs/hover";
import { ReactNode, useRef } from "react";

export interface DetectionFrameProps {
  children: ReactNode;
  /** Label rendered above the top-left corner, e.g. a class name */
  tag?: string;
  className?: string;
}

const corners = [
  { pos: "top-0 left-0", border: "border-t-2 border-l-2", from: "translate3d(-6px,-6px,0)" },
  { pos: "top-0 right-0", border: "border-t-2 border-r-2", from: "translate3d(6px,-6px,0)" },
  { pos: "bottom-0 left-0", border: "border-b-2 border-l-2", from: "translate3d(-6px,6px,0)" },
  { pos: "bottom-0 right-0", border: "border-b-2 border-r-2", from: "translate3d(6px,6px,0)" },
] as const;

export const DetectionFrame = ({
  children,
  tag,
  className = "",
}: DetectionFrameProps) => {
  const containerRef = useRef<HTMLDivElement>(null);

  return (
    <div ref={containerRef} className={`relative ${className}`}>
      {children}
      {corners.map((corner) => (
        <Hover
          key={corner.pos}
          tag="span"
          trigger={containerRef}
          from={{ opacity: 0, transform: corner.from }}
          to={{ opacity: 1, transform: "translate3d(0,0,0)" }}
          config={{ tension: 320, friction: 24 }}
          className={`pointer-events-none absolute h-[1.1rem] w-[1.1rem] border-accent ${corner.pos} ${corner.border}`}
        />
      ))}
      {tag && (
        <Hover
          tag="span"
          trigger={containerRef}
          from={{ opacity: 0 }}
          to={{ opacity: 1 }}
          config={{ tension: 320, friction: 26 }}
          className="pointer-events-none absolute -top-6 left-0 font-mono text-[0.7rem] uppercase tracking-[0.14em] text-accent"
        >
          {tag}
        </Hover>
      )}
    </div>
  );
};
