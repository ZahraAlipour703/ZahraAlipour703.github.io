"use client";

import { easings } from "@react-spring/web";
import TextEngine from "spring-text-engine";

import { DetectionLabel } from "@/components/ui/detection-label";

export interface SectionHeadingProps {
  eyebrow: string;
  title: string;
  subtitle?: string;
  align?: "left" | "center";
}

export const SectionHeading = ({
  eyebrow,
  title,
  subtitle,
  align = "left",
}: SectionHeadingProps) => {
  const alignment = align === "center" ? "items-center text-center" : "items-start text-left";

  return (
    <div className={`flex flex-col gap-[1.2em] ${alignment}`}>
      <DetectionLabel label={eyebrow} />
      <TextEngine
        tag="h2"
        mode="once"
        lineIn={{ y: "0%", opacity: 1 }}
        lineOut={{ y: "100%", opacity: 0 }}
        lineStagger={80}
        lineConfig={{ duration: 800, easing: easings.easeOutCubic }}
        overflow
        className="max-w-[24ch] text-[2.4rem] leading-[1.1] font-medium text-foreground sm:text-[3.2rem]"
      >
        {title}
      </TextEngine>
      {subtitle && (
        <p className="max-w-[52ch] text-[1.05rem] leading-[1.6] text-muted">
          {subtitle}
        </p>
      )}
    </div>
  );
};
