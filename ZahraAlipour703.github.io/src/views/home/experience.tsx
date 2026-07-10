import { Inview } from "@/components/animation/springs/in-view";
import { SectionHeading } from "@/components/ui/section-heading";
import { experience } from "@/data/mocks/home";

export const Experience = () => {
  return (
    <section id="experience" className="px-[1.5rem] py-[var(--spacing-section)] sm:px-[3rem]">
      <div className="mx-auto flex max-w-[75rem] flex-col gap-[3.5rem]">
        <SectionHeading eyebrow="experience" title="Experience" />

        <ol className="flex flex-col gap-[3rem] border-l border-border pl-[1.75rem]">
          {experience.map((item, i) => (
            <Inview
              key={item.id}
              tag="li"
              mode="once"
              from={{ opacity: 0, transform: "translate3d(0,20px,0)" }}
              to={{ opacity: 1, transform: "translate3d(0,0,0)" }}
              delayIn={i * 120}
              config={{ tension: 180, friction: 26 }}
              className="relative flex flex-col gap-[0.6em]"
            >
              <span
                aria-hidden="true"
                className="absolute top-[0.4em] -left-[2.03rem] h-[0.6rem] w-[0.6rem] rounded-full bg-accent"
              />
              <span className="font-mono text-[0.8rem] uppercase tracking-[0.1em] text-accent">
                {item.date}
              </span>
              <h3 className="text-[1.2rem] font-medium text-foreground">{item.role}</h3>
              <p className="font-mono text-[0.85rem] text-muted">{item.org}</p>
              <ul className="mt-[0.5em] flex flex-col gap-[0.5em]">
                {item.bullets.map((bullet, bi) => (
                  <li key={bi} className="text-[0.95rem] leading-[1.65] text-muted">
                    {bullet}
                  </li>
                ))}
              </ul>
            </Inview>
          ))}
        </ol>
      </div>
    </section>
  );
};
