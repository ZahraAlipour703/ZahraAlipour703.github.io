import { Inview } from "@/components/animation/springs/in-view";
import { DetectionFrame } from "@/components/ui/detection-frame";
import { SectionHeading } from "@/components/ui/section-heading";
import { researchInterests } from "@/data/mocks/home";

export const Research = () => {
  return (
    <section
      id="research"
      className="border-t border-border bg-surface px-[1.5rem] py-[var(--spacing-section)] sm:px-[3rem]"
    >
      <div className="mx-auto flex max-w-[75rem] flex-col gap-[3.5rem]">
        <SectionHeading eyebrow="research" title="Research Interests" />

        <div className="grid gap-[1.5rem] sm:grid-cols-2">
          {researchInterests.map((item, i) => (
            <Inview
              key={item.id}
              tag="div"
              mode="once"
              from={{ opacity: 0, transform: "translate3d(0,24px,0)" }}
              to={{ opacity: 1, transform: "translate3d(0,0,0)" }}
              delayIn={i * 100}
              config={{ tension: 180, friction: 26 }}
            >
              <DetectionFrame tag={item.class}>
                <article className="flex h-full flex-col gap-[0.8em] border border-border-strong bg-surface-raised p-[1.75rem]">
                  <span className="font-mono text-[0.72rem] uppercase tracking-[0.14em] text-accent">
                    class:{item.class} · {item.confidence.toFixed(2)}
                  </span>
                  <h3 className="text-[1.25rem] leading-[1.3] font-medium text-foreground">
                    {item.title}
                  </h3>
                  <p className="text-[0.98rem] leading-[1.65] text-muted">
                    {item.description}
                  </p>
                </article>
              </DetectionFrame>
            </Inview>
          ))}
        </div>
      </div>
    </section>
  );
};
