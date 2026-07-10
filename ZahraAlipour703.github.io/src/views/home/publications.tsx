import { Inview } from "@/components/animation/springs/in-view";
import { SectionHeading } from "@/components/ui/section-heading";
import { publications } from "@/data/mocks/home";

export const Publications = () => {
  return (
    <section
      id="publications"
      className="border-t border-border bg-surface px-[1.5rem] py-[var(--spacing-section)] sm:px-[3rem]"
    >
      <div className="mx-auto flex max-w-[75rem] flex-col gap-[3.5rem]">
        <SectionHeading eyebrow="publications" title="Publications" />

        <ul className="flex flex-col gap-[1.5rem]">
          {publications.map((pub, i) => (
            <Inview
              key={pub.id}
              tag="li"
              mode="once"
              from={{ opacity: 0, transform: "translate3d(0,16px,0)" }}
              to={{ opacity: 1, transform: "translate3d(0,0,0)" }}
              delayIn={i * 100}
              config={{ tension: 180, friction: 26 }}
              className="flex flex-col gap-[0.6em] border-b border-border pb-[1.5rem] sm:flex-row sm:items-baseline sm:gap-[2rem]"
            >
              <span className="w-[5rem] shrink-0 font-mono text-[0.85rem] text-accent">
                {pub.year}
              </span>
              <div className="flex flex-col gap-[0.4em]">
                <h3 className="text-[1.1rem] leading-[1.4] font-medium text-foreground">
                  {pub.title}
                </h3>
                <p className="font-mono text-[0.85rem] text-muted">{pub.authors}</p>
              </div>
            </Inview>
          ))}
        </ul>
      </div>
    </section>
  );
};
