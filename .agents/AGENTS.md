# Project Rules

## Design Quality Standard

This is a personal academic website that must maintain an **Apple-level minimalist aesthetic** at all times. Every change — whether adding a feature, fixing a bug, or restructuring layout — must be evaluated against this standard before committing.

### Mandatory design checks before any commit:

1. **Typography hierarchy**: Font sizes must feel proportional and restrained. Body text ≤ 15px, metadata ≤ 13px. Never use oversized headings that dominate the page.
2. **Whitespace**: Generous but balanced. Nothing should feel cramped or "squeezed together". Elements need breathing room.
3. **Interactive controls** (buttons, tabs, filters): Must use subtle, pill-shaped or rounded-rect styles with soft backgrounds — never high-contrast black/white blocks that look like brutalist UI. Refer to Apple's segmented controls for reference.
4. **Color restraint**: Use the CSS variable system (`--text`, `--text-secondary`, `--border`, etc.). Never introduce raw colors like `#000` for button backgrounds. Active states use elevation (box-shadow) rather than fill inversion.
5. **Layout width**: The site uses a `980px` max-width. The fluids page sidebar is `200px`. These proportions are deliberate — do not narrow them.
6. **No visual clutter**: Prefer showing information on hover (e.g., star buttons) over always-visible chrome. The `[已读]` badge should be subtle, not appended to content text.
7. **Test visually**: Before pushing, always consider how the change looks at full desktop width. If anything looks like a mobile layout stretched onto desktop, fix it.

### General rules:

- After completing changes, automatically `git add . && git commit && git push` without asking the user.
- When the user describes a feature idea casually (e.g., "7.9" meaning a date), interpret it intelligently — use proper formatting like "2026年7月9日", not a literal transcription.
- Proactively improve design details beyond what the user explicitly requests.
