import { siteMeta } from "@/data/mocks/home";

const footerLinks = [
  { label: "GitHub", href: siteMeta.github },
  { label: "LinkedIn", href: `https://${siteMeta.linkedin.replace(/^https?:\/\//, "")}` },
  { label: "Scholar", href: siteMeta.scholar },
  { label: "Email", href: `mailto:${siteMeta.email}` },
];

export const Footer = () => {
  return (
    <footer className="border-t border-border px-[1.5rem] py-[2.5rem] sm:px-[3rem]">
      <div className="mx-auto flex max-w-[75rem] flex-col items-center gap-[1rem] text-center sm:flex-row sm:justify-between sm:text-left">
        <div className="flex flex-col gap-[0.2em]">
          <p className="text-[0.9rem] text-muted">
            © {new Date().getFullYear()} {siteMeta.name}. All rights reserved.
          </p>
          <p className="font-mono text-[0.78rem] text-muted">
            Computer Vision Engineer · AI Researcher
          </p>
        </div>
        <ul className="flex gap-[1.5em] font-mono text-[0.8rem] uppercase tracking-[0.08em] text-muted">
          {footerLinks.map((link) => (
            <li key={link.label}>
              <a href={link.href} target="_blank" rel="noreferrer" className="hover:text-accent">
                {link.label}
              </a>
            </li>
          ))}
        </ul>
      </div>
    </footer>
  );
};
