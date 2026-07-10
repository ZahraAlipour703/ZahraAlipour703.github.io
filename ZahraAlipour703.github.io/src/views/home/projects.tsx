import { Inview } from "@/components/animation/springs/in-view";
import { DetectionFrame } from "@/components/ui/detection-frame";
import { SectionHeading } from "@/components/ui/section-heading";
import { Tag } from "@/components/ui/tag";
import { projects, siteMeta } from "@/data/mocks/home";

export const Projects = () => {
  return (
    <section id="projects" className="px-[1.5rem] py-[var(--spacing-section)] sm:px-[3rem]">
      <div className="mx-auto flex max-w-[75rem] flex-col gap-[3.5rem]">
        <SectionHeading
          eyebrow="projects"
          title="Featured Projects"
          subtitle="Computer vision & vision-language model work, from real-time detection to semantic search."
        />

        <div className="grid gap-[1.5rem] md:grid-cols-2 xl:grid-cols-3">
          {projects.map((project, i) => (
            <Inview
              key={project.id}
              tag="div"
              mode="once"
              from={{ opacity: 0, transform: "translate3d(0,24px,0)" }}
              to={{ opacity: 1, transform: "translate3d(0,0,0)" }}
              delayIn={(i % 3) * 90}
              config={{ tension: 180, friction: 26 }}
              className="h-full"
            >
              <DetectionFrame tag={project.id} className="h-full">
                <article className="flex h-full flex-col gap-[1em] border border-border bg-surface p-[1.5rem]">
                  <h3 className="text-[1.15rem] leading-[1.3] font-medium text-foreground">
                    {project.title}
                  </h3>
                  <p className="flex-1 text-[0.92rem] leading-[1.6] text-muted">
                    {project.description}
                  </p>
                  <div className="flex flex-wrap gap-[0.5em]">
                    {project.tags.map((tag) => (
                      <Tag key={tag}>{tag}</Tag>
                    ))}
                  </div>
                  <a
                    href={project.href ?? siteMeta.github}
                    target="_blank"
                    rel="noreferrer"
                    className="font-mono text-[0.78rem] uppercase tracking-[0.08em] text-accent hover:text-foreground"
                  >
                    View Code →
                  </a>
                </article>
              </DetectionFrame>
            </Inview>
          ))}
        </div>

        <a
          href={`${siteMeta.github}?tab=repositories`}
          target="_blank"
          rel="noreferrer"
          className="self-center font-mono text-[0.85rem] uppercase tracking-[0.1em] text-accent hover:text-foreground"
        >
          View All Projects on GitHub →
        </a>
      </div>
    </section>
  );
};
