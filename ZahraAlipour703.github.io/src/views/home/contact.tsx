import { Inview } from "@/components/animation/springs/in-view";
import { DetectionFrame } from "@/components/ui/detection-frame";
import { SectionHeading } from "@/components/ui/section-heading";
import { contactChannels } from "@/data/mocks/home";

export const Contact = () => {
  return (
    <section
      id="contact"
      className="border-t border-border bg-surface px-[1.5rem] py-[var(--spacing-section)] sm:px-[3rem]"
    >
      <div className="mx-auto flex max-w-[75rem] flex-col gap-[3.5rem]">
        <SectionHeading
          eyebrow="contact"
          title="Get In Touch"
          subtitle="I'm always open to discussing research opportunities, collaborations, or potential positions in Computer Vision and Deep Learning."
        />

        <div className="grid gap-[1.25rem] sm:grid-cols-2 lg:grid-cols-4">
          {contactChannels.map((channel, i) => (
            <Inview
              key={channel.id}
              tag="div"
              mode="once"
              from={{ opacity: 0, transform: "translate3d(0,20px,0)" }}
              to={{ opacity: 1, transform: "translate3d(0,0,0)" }}
              delayIn={i * 90}
              config={{ tension: 180, friction: 26 }}
            >
              <DetectionFrame tag={channel.label.toLowerCase()}>
                <div className="flex flex-col gap-[0.5em] border border-border-strong bg-surface-raised p-[1.5rem]">
                  <span className="font-mono text-[0.72rem] uppercase tracking-[0.14em] text-accent">
                    {channel.label}
                  </span>
                  {channel.href ? (
                    <a
                      href={channel.href}
                      target={channel.href.startsWith("http") ? "_blank" : undefined}
                      rel={channel.href.startsWith("http") ? "noreferrer" : undefined}
                      className="text-[1rem] text-foreground hover:text-accent"
                    >
                      {channel.value}
                    </a>
                  ) : (
                    <p className="text-[1rem] text-foreground">{channel.value}</p>
                  )}
                </div>
              </DetectionFrame>
            </Inview>
          ))}
        </div>
      </div>
    </section>
  );
};
