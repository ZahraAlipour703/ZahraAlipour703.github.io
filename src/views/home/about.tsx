import { Inview } from "@/components/animation/springs/in-view";
import { DetectionFrame } from "@/components/ui/detection-frame";
import { SectionHeading } from "@/components/ui/section-heading";
import { aboutHighlights, aboutParagraphs } from "@/data/mocks/home";

export const About = () => {
  return (
    <section id="about" className="px-[1.5rem] py-[var(--spacing-section)] sm:px-[3rem]">
      <div className="mx-auto flex max-w-[75rem] flex-col gap-[3.5rem]">
        <SectionHeading eyebrow="about" title="About Me" />

        <div className="grid gap-[3rem] lg:grid-cols-[1.3fr_1fr]">
          <Inview
            tag="div"
            mode="once"
            from={{ opacity: 0, transform: "translate3d(0,20px,0)" }}
            to={{ opacity: 1, transform: "translate3d(0,0,0)" }}
            config={{ tension: 180, friction: 26 }}
            className="flex flex-col gap-[1.4em]"
          >
            {aboutParagraphs.map((paragraph, i) => (
              <p key={i} className="text-[1.02rem] leading-[1.75] text-muted">
                {paragraph}
              </p>
            ))}
          </Inview>

          <div className="flex flex-col gap-[1.2rem]">
            {aboutHighlights.map((item, i) => (
              <Inview
                key={item.id}
                tag="div"
                mode="once"
                from={{ opacity: 0, transform: "translate3d(0,20px,0)" }}
                to={{ opacity: 1, transform: "translate3d(0,0,0)" }}
                delayIn={i * 120}
                config={{ tension: 180, friction: 26 }}
              >
                <DetectionFrame tag={item.label.toLowerCase()}>
                  <div className="flex flex-col gap-[0.4em] border border-border bg-surface p-[1.5rem]">
                    <span className="font-mono text-[0.72rem] uppercase tracking-[0.14em] text-accent">
                      {item.label}
                    </span>
                    <p className="text-[1.05rem] text-foreground">{item.detail}</p>
                    <p className="text-[0.9rem] text-muted">{item.sub}</p>
                  </div>
                </DetectionFrame>
              </Inview>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};
