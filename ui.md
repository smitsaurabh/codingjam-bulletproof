# Resume Tailor — UX Design Doc

**Designer:** Senior Product Designer  
**Status:** Draft v0.1  
**Last updated:** 2026-10-30  

---

## 1. The design bet

We are betting that a unified, high-density split workspace—inputs pinned on the left, live tailored output on the right—eliminates context switching and turns what is normally a stressful chore into a rapid, surgical workflow. By placing the inputs and tailored bullets side-by-side on desktop, the user can visually trace how their experience was adapted to the job posting without ever scrolling away from their source context.

## 2. The defining interaction

User finishes pasting their resume bullets and the target job description, then clicks the prominent "Tailor Bullets" button. The button enters a subtle energetic pulse ("Extracting keywords & tailoring..."). Within ~2.5 seconds, the right-hand panel hydrates with polished bullet cards, each labeled with the specific job requirement it addresses (e.g., `Distributed Systems`, `Executive Presentation`). When the user clicks "Copy" on any card, the button immediately ticks into an emerald green checkmark with a crisp micro-label ("Copied!"). Total time: < 3 seconds. It feels like: sliding freshly pressed cards out of a precision printing press.

## 3. Screen inventory

v1 contains **exactly one screen**:

- **Tailor Studio (Main Workspace)** — Single-screen dual-pane workbench containing the input controls on the left and the generated tailored bullets on the right.

## 4. Screen-by-screen specs

### Tailor Studio (Main Workspace)

**Purpose:** Provide an end-to-end input, generation, comparison, and one-click clipboard extraction workflow in a single view.

**Layout (Left-to-Right Desktop / Top-to-Bottom Mobile):**

1. **Top Header Bar:**
   - App title (`Resume Tailor`) with a compact tag (`Ruthless Focus`).
   - "Try Sample" text button on the right to instantly populate realistic demo text.
   - Clear All button (resets workspace).
2. **Left Pane — Input Workbench:**
   - Section 1: **Existing Resume Experience** text area (auto-expanding or fixed height with internal scroll, placeholder containing 3 sample bullets, character counter).
   - Section 2: **Target Job Posting** text area (placeholder with job description snippet, character counter).
   - Primary Action Bar: Full-width high-contrast button labeled `Tailor Bullets ⚡` with a subtle keyboard shortcut hint (`Cmd + Enter` / `Ctrl + Enter`).
3. **Right Pane — Tailored Output Inspector:**
   - Results Header: Count badge (e.g., `5 Tailored Bullets`), quick quality badge (`Role-Aligned`), and a global `Copy All` button.
   - Bullet Cards Stack: Vertical list of clean cards. Each card has:
     - Header chip: Identified job skill/keyword match tag (e.g., `Team Leadership`, `Cloud Infrastructure`).
     - Content block: Polished bullet text with strong action verbs and metric emphasis.
     - Action footer: Individual `Copy Bullet` button positioned at the bottom-right of the card.

**Key interactions:**
- Click "Try Sample" → Inputs populate instantly with realistic senior engineering resume bullets and a target staff engineer job description.
- Click "Tailor Bullets" (or `Cmd+Enter`) → Form disables, loader activates on button and result panel skeleton appears, API request initiates.
- Click "Copy" on a bullet card → Bullet text copies to system clipboard, button morphs to emerald badge `Copied!`, reverts after 1.8 seconds.
- Click "Copy All" → Formats all bullets with standard markdown bullet dashes, copies to clipboard, toast confirms `All 5 bullets copied!`.

**States:**
- **Default / Empty:** Right panel shows an intentional placeholder illustration/stencil with a clear prompt: "Paste your resume bullets and job posting to see tailored high-impact bullets appear here."
- **Loading:** Left inputs become read-only; primary CTA shows an animated spinner and text "Tailoring with Gemini..."; right panel displays three pulsing skeleton card placeholders.
- **Error:** If generation fails (e.g., network disconnect or empty API key), a concise inline alert banner appears above the inputs with a retry button: "Could not generate tailored bullets. Please check connection and try again." Inputs are never erased.
- **Edge / "Too Much Text":** Character counter turns amber when input exceeds 6,000 characters; user receives a subtle soft warning note: "Tip: For fastest and most accurate bullets, include only the experience section and key job responsibilities."

## 5. The user journey

User lands on the page for the first time. The screen is clean, fast, and free of clutter or sign-up walls. They immediately notice two large text boxes on the left and an expectant preview stencil on the right. Curious, they click "Try Sample" in the header; both boxes fill with realistic text, and the primary "Tailor Bullets" button lights up.

They click "Tailor Bullets". The button activates with a smooth progress pulse. Within 2.5 seconds, the right panel renders five tailored bullets. The user scans the first bullet: where the original bullet read "Worked on backend microservices for user notifications", the tailored bullet reads "Architected high-throughput notification microservice supporting 2M+ daily events, cutting delivery latency by 35% using Go and Kafka". They tap "Copy". A green `Copied!` pill flashes. They paste it straight into their job application.

In their second session the next day, they skip the sample, paste their own resume bullets from Google Docs, paste a job posting from Greenhouse, hit `Cmd+Enter`, click "Copy All", and close the tab in under 30 seconds.

## 6. Component & visual notes

- **Typography:** Inter or system sans-serif (`-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto`) for crisp, legible UI copy; monospace numbers for character counters.
- **Color:** Sophisticated, dark/neutral slate background (`#0f172a` canvas, `#1e293b` surfaces), crisp white text for high readability, electric indigo (`#6366f1`) for primary actions, and vivid emerald (`#10b981`) for successful clipboard actions.
- **Motion:** Micro-interactions only. 150ms ease-out transitions on button hover, gentle 1.5s skeleton shimmer during generation, 200ms pop for the `Copied!` state. Zero bouncy spring animations or distracting decorative motion.
- **The Signature Visual:** The "Keyword Alignment Chip" at the top-left of each tailored bullet card. Rendered in semi-transparent slate with a tiny dot indicator, it proves to the user at a glance why this bullet was written this way.
- **Microcopy Voice:** Direct, confident, and professional. Examples: "Tailor Bullets", "Target Job Requirements", "Copied to clipboard", "Try Sample Data". Never cute or apologetic.

## 7. Accessibility & inclusion

- **Screen Readers:** Explicit `<label>` associations for both text areas; aria-live announcements (`aria-live="polite"`) when tailored bullets finish generating and when clipboard copy succeeds.
- **Keyboard Navigation:** Full tab order flow: Resume Input → Job Posting Input → Tailor Button → Copy All → Individual Bullet Copy Buttons. `Cmd/Ctrl + Enter` triggers generation from within any text field.
- **Color Contrast:** All text meets WCAG AA standards (minimum 4.5:1 contrast against surface backgrounds). The green `Copied!` confirmation includes both icon and text, not relying solely on color.
- **Low Connectivity:** Generation states handle timeout gracefully (10-second timeout with explicit retry button without clearing inputs).

## 8. What we are NOT designing

- **No Multi-step Wizard / Tab Navigation** — Both inputs and outputs stay on one screen; no next/back stepping.
- **No Settings Modal or Custom Theme Picker** — One refined, dark-mode-first aesthetic that looks sharp out of the box.
- **No In-place Rich Text Editing / WYSIWYG** — The output is for copying into the user's resume editor, not for formatting in our UI.
- **No History or Saved Resumes Drawer** — Device-local ephemeral session; no database or saved state cluttering the UI.
- **No Drag-and-Drop File Upload Zone** — Direct paste only; eliminates complex file handling and parsing error dialogs.

## 9. Open design questions

- [ ] On smaller mobile screens (< 768px), should clicking "Tailor" automatically smooth-scroll down to the results panel?
- [ ] Should individual bullet cards allow a quick "Regenerate single bullet" icon button in v1, or keep the interface strictly read-and-copy?

## 10. Handoff to engineering

> The transition from loading state to hydrated cards must avoid Cumulative Layout Shift (CLS) by utilizing pre-sized skeleton cards matching the generated card dimensions. The clipboard copy action must use the native `navigator.clipboard.writeText` API with fallback to `document.execCommand('copy')` to guarantee zero-latency copy response across all browsers.
