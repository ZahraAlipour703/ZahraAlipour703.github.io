"use client";

import { easings } from "@react-spring/web";
import TextEngine from "spring-text-engine";

import { Inview } from "@/components/animation/springs/in-view";
import { DetectionLabel } from "@/components/ui/detection-label";
import { Button } from "@/components/ui/button";
import { siteMeta } from "@/data/mocks/home";

export const Hero = () => {
  return (
    <section
      id="home"
      className="relative flex min-h-lvh flex-col justify-center overflow-hidden px-[1.5rem] pt-[6rem] sm:px-[3rem]"
    >
      {/* Ambient scanline field — signature backdrop, purely decorative */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 opacity-[0.05]"
        style={{
          backgroundImage:
            "repeating-linear-gradient(to bottom, var(--accent) 0px, var(--accent) 1px, transparent 1px, transparent 4px)",
        }}
      />

      <div className="relative flex max-w-[62rem] flex-col gap-[1.4em]">
        <DetectionLabel label="person" confidence={0.99} />

        <TextEngine
          tag="h1"
          mode="once"
          lineIn={{ y: "0%", opacity: 1 }}
          lineOut={{ y: "100%", opacity: 0 }}
          lineStagger={90}
          lineConfig={{ duration: 900, easing: easings.easeOutCubic }}
          overflow
          className="text-[3rem] leading-[1.05] font-medium text-foreground sm:text-[5rem]"
        >
          {siteMeta.name}
        </TextEngine>

        <Inview
          tag="div"
          mode="once"
          from={{ opacity: 0, transform: "translate3d(0,16px,0)" }}
          to={{ opacity: 1, transform: "translate3d(0,0,0)" }}
          delayIn={400}
          config={{ tension: 200, friction: 26 }}
          className="flex flex-col gap-[0.4em]"
        >
          <p className="font-mono text-[1.1rem] text-accent">{siteMeta.role}</p>
          <p className="max-w-[42ch] text-[1.05rem] leading-[1.6] text-muted">
            Specializing in {siteMeta.focus}.
          </p>
        </Inview>

        <Inview
          tag="div"
          mode="once"
          from={{ opacity: 0, transform: "translate3d(0,16px,0)" }}
          to={{ opacity: 1, transform: "translate3d(0,0,0)" }}
          delayIn={600}
          config={{ tension: 200, friction: 26 }}
          className="mt-[0.8em] flex flex-wrap items-center gap-[1em]"
        >
          <Button href="#contact" variant="primary">
            Get In Touch
          </Button>
          <Button href={siteMeta.github} target="_blank" variant="secondary">
            GitHub Portfolio
          </Button>
        </Inview>
      </div>

      <a
        href="#about"
        aria-label="Scroll to About section"
        className="absolute bottom-[2rem] left-1/2 -translate-x-1/2 font-mono text-[0.75rem] uppercase tracking-[0.16em] text-muted hover:text-accent"
      >
        Scroll ↓
      </a>
    </section>
  );
};
