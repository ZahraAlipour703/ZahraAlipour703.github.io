# next16-claude-starter

A **Next.js 16 starter** for animation-heavy marketing & landing sites — built
by [Textura](https://textura.agency) so that AI agents (Claude Code, Cursor)
generate **clean, production-ready code on the first pass**.

Every motion is spring-based (`@react-spring/web`), text animation runs through
`spring-text-engine`, scrolling is smoothed with Lenis, styling is Tailwind
v4, and a rem-based adaptive grid scales the design across every viewport.

---

## ⭐ How to use this starter (with AI)

The real value here isn't the boilerplate — it's the **documentation +
enforcement system** wrapped around it. An [Obsidian vault](./obsidian/README.md)
holds every convention, a set of Claude Code hooks forces agents to read it
before writing and update it after, and a small set of hard rules keeps every
generated component on-style.

### Hooks do the enforcement for you

`.claude/settings.json` ships **three hooks** that turn the workflow on
automatically — you don't have to ask for any of this in your prompt:

| Hook | When it fires | What it does |
|------|---------------|--------------|
| `SessionStart` | new chat / resume | Points the agent at the vault before it does anything |
| `UserPromptSubmit` | every request | Reminds the agent to consult the relevant guide before acting |
| `Stop` | end of every turn | Blocks once to confirm the vault was updated to match the change |

Inspect, edit, or disable them anytime with `/hooks` in Claude Code. ADR:
[`obsidian/meta/decisions-log.md`](./obsidian/meta/decisions-log.md) (ADR-0007).

### How to write a good request

Because the conventions live in the vault, your prompts get to focus on **what**
you want — not **how** to write it. A good request:

- **Says what to build, not how.** *"Add a Testimonials section to the home
  page with a horizontal scroll carousel"* — not *"use react-spring with a
  parallel hook and a `mode="forward"` Inview…"*. The vault tells the agent how.
- **Names the page / view / component clearly.** Routes delegate to
  `src/views/`; reference that file when iterating.
- **Cites a vault note only to *override* a convention** (rare). Most of the
  time the hooks will pull in the right guide on their own.
- **For a brand-new page**, point the agent at the
  [`new-page`](./obsidian/workflows/new-page.md) playbook or fill in
  [`generic-layout-prompt`](./obsidian/workflows/generic-layout-prompt.md).
- **Trust the hard rules.** Spring-based motion only, design tokens, no `any`,
  server components by default, semantic HTML, routes → views. These are
  enforced — you don't have to repeat them in every prompt.

The payoff: animation-heavy pages that ship lint-clean, typed, accessible, and
on-token — without the usual "now make it production-ready" second pass.

### 💸 Cost expectations

This starter is **token-intensive by design**. Every prompt fans out into the
vault (architecture, conventions, the relevant topic note), and the hooks
re-inject context on every turn. That bought-clean code costs tokens.

> **Minimum recommended plan: [Claude Max (5×)](https://www.anthropic.com/pricing).**
> A standard Claude.ai Pro plan will hit usage limits quickly on a real
> session.

---

## Getting started

1. **Clone the template**
   ```bash
   git clone https://github.com/textura/next16-claude-starter.git my-project
   cd my-project
   ```

2. **Detach from this repo's history.** The bundled `.git` folder is hidden;
   on macOS, with the folder open in Finder, press `⇧ + ⌘ + .` (Shift + Cmd + .)
   to reveal hidden files, then drag `.git` to the bin. Or from the terminal:
   ```bash
   rm -rf .git
   ```

3. **Initialise your own GitHub repo.** Create an empty repo on GitHub first
   (no README/`.gitignore` — the template already has them), then:
   ```bash
   git init
   git add .
   git commit -m "chore: initial commit"
   git branch -M main
   git remote add origin <your-new-repo-url>
   git push -u origin main
   ```

4. **Install and run**
   ```bash
   yarn install
   yarn dev      # http://localhost:3000
   ```

| Script | Purpose |
|--------|---------|
| `yarn dev` | Development server |
| `yarn build` | Production build |
| `yarn start` | Serve the production build |
| `yarn lint` | ESLint |

## 🚀 Deploy to Vercel

The fastest path to production — Next.js is Vercel's home framework, so the
defaults Just Work. From the project root:

```bash
npm i -g vercel@latest    # one-time, if you don't have it
vercel                    # links the repo and ships a preview deploy
vercel --prod             # promotes to production
```

Or from the dashboard: open [vercel.com/new](https://vercel.com/new), import
the GitHub repo you created in step 3, accept the defaults — the Next.js
preset auto-configures the build, output, and image optimisation. No
`vercel.json` required.

When you add environment variables (e.g. `NEXT_PUBLIC_SITE_URL`, see
[`obsidian/architecture/environment-variables.md`](./obsidian/architecture/environment-variables.md)),
set them in **Project Settings → Environment Variables** on Vercel, then sync
them locally with:

```bash
vercel env pull .env.local
```

## 📖 Documentation

Full project documentation lives in the **`obsidian/`** Obsidian vault — open
that folder in [Obsidian](https://obsidian.md) for a linked, navigable second
brain covering architecture, the animation system, conventions, and workflows.

Start at [`obsidian/README.md`](./obsidian/README.md).

## For AI agents

> ⚠️ This is **not** the Next.js you may know — APIs and conventions differ
> from older versions. Read `AGENTS.md` and the `obsidian/` vault before
> writing code.

Entry points `AGENTS.md` · `CLAUDE.md` · `.cursorrules` all lead into the
`obsidian/` vault — the single source of truth for this project. Full rules of
engagement: [`obsidian/workflows/ai-agent-guide.md`](./obsidian/workflows/ai-agent-guide.md).
