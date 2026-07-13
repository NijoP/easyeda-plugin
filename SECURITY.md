# Security Policy

## Scope

PCB Flow is a local, file-based engineering workspace. It runs on your machine, drives a
browser session you own (EasyEDA) and local tooling (KiCad), and stores no credentials of its
own. There is no hosted service and no telemetry.

The most relevant risks are therefore:
- **AI-driven automation** running code against your live EDA session.
- **Secrets accidentally committed** into a board's `projects/` folder.

## Reporting a vulnerability

Please **do not** open a public issue for security problems. Instead, report privately via
[GitHub Security Advisories](https://github.com/NijoP/pcbflow/security/advisories/new). Include
a description, reproduction steps, and impact. We aim to acknowledge within a few days.

## Handling secrets

- Never commit tokens, API keys, or passwords. `.gitignore` excludes `.env`, `*.pat`, and
  `*credentials*`; keep secrets in environment variables.
- Board work lives in `projects/`; review a project folder before pushing it publicly.
- The reliability logs under `**/.logs/` are gitignored — but scrub them before sharing.

## Safe automation

- The AI defers every safety-critical decision (power sizing, DRC sign-off, and the fab order)
  to you, and stops for approval before drawing copper. Keep that review discipline.
- Run automation only against EDA windows and projects you own.
