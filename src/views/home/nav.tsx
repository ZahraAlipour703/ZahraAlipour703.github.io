"use client";

import { useState } from "react";

import { navLinks, siteMeta } from "@/data/mocks/home";

export const Nav = () => {
  const [open, setOpen] = useState(false);

  return (
    <nav
      aria-label="Primary"
      className="fixed top-0 left-0 z-50 w-full border-b border-border bg-background/85 backdrop-blur-sm"
    >
      <div className="mx-auto flex max-w-[90rem] items-center justify-between px-[1.5rem] py-[1.1rem] sm:px-[3rem]">
        <a href="#home" className="font-mono text-[0.95rem] tracking-[0.08em] text-foreground">
          {siteMeta.name}
        </a>

        <ul className="hidden gap-[2em] font-mono text-[0.8rem] uppercase tracking-[0.1em] text-muted md:flex">
          {navLinks.map((link) => (
            <li key={link.href}>
              <a href={link.href} className="hover:text-accent">
                {link.label}
              </a>
            </li>
          ))}
        </ul>

        <button
          type="button"
          aria-label={open ? "Close menu" : "Open menu"}
          aria-expanded={open}
          aria-controls="mobile-menu"
          onClick={() => setOpen((v) => !v)}
          className="flex h-[2.5rem] w-[2.5rem] flex-col items-center justify-center gap-[0.35rem] border border-border-strong md:hidden"
        >
          <span
            className={`h-px w-[1.1rem] bg-foreground ${open ? "translate-y-[0.2rem] rotate-45" : ""}`}
          />
          <span className={`h-px w-[1.1rem] bg-foreground ${open ? "opacity-0" : ""}`} />
          <span
            className={`h-px w-[1.1rem] bg-foreground ${open ? "-translate-y-[0.2rem] -rotate-45" : ""}`}
          />
        </button>
      </div>

      {open && (
        <ul
          id="mobile-menu"
          className="flex flex-col gap-[1em] border-t border-border px-[1.5rem] py-[1.5rem] font-mono text-[0.85rem] uppercase tracking-[0.1em] text-muted md:hidden"
        >
          {navLinks.map((link) => (
            <li key={link.href}>
              <a href={link.href} onClick={() => setOpen(false)} className="hover:text-accent">
                {link.label}
              </a>
            </li>
          ))}
        </ul>
      )}
    </nav>
  );
};
