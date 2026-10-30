# Resume Tailor — Product Design Doc

**Author:** Staff Product Manager  
**Status:** Draft v0.1  
**Last updated:** 2026-10-30  
**One-liner:** Transform generic resume experience bullets into high-impact, role-matched achievements in seconds.

---

## 1. The user & the moment

Who is this for, and what are they doing/feeling **right before** they open the app?

- **Who:** An active job seeker applying to knowledge-work and tech roles who has a solid base resume but dreads tailoring it for every single job posting.
- **When:** It is 10:45 PM on a Tuesday. They have application tab #14 open on LinkedIn or Greenhouse. They know their generic bullets will get screened out by recruiters or ATS, but they do not have the energy to spend 45 minutes rewriting bullets from scratch.
- **Why now:** Recruiters triage resumes in 6 seconds, and generic "responsible for X" bullets get filtered out immediately. Manual customization creates application fatigue, leading to low submission volume or low interview conversion.

## 2. The contract (I/O)

The most important section. What does the user give, and what do they get back?

- **Input:** Two plain text boxes:
  1. Base resume text (specifically their existing experience bullet points).
  2. Job posting text (the target job description, responsibilities, and requirements).
- **Output:** A structured collection of tailored, high-impact bullet points mapped to target job requirements, presented alongside original bullets with one-click copy actions.
- **The loop:** Paste resume text → Paste target job description → Tap "Tailor Bullets" → Review upgraded bullets with matched keywords → Copy individual bullets or "Copy All" directly into their application document.

## 3. The magical moment

The single sentence the user would say to a friend after using this for the first time:

> "This actually articulated my own work ten times better than I could, and it directly nailed every requirement in the job post without making anything up."

## 4. Scope: what we ARE building (v1)

A focused, single-screen utility delivering rapid resume tailoring:

- Dual plain-text input panel with clear placeholder prompts and character count indicators.
- One-click "Tailor Bullets" action triggering AI transformation via Gemini structured output.
- Clean results panel displaying upgraded bullets with highlighted target-job keyword alignments.
- One-click copy button per tailored bullet plus a universal "Copy All" button with instant visual feedback.
- Pre-populated "Try Sample" toggle button so users can test the magic in 5 seconds without hunting for files.

## 5. Scope: what we are NOT building

The cuts define the product and ensure a clean, reliable, focused build:

- **No PDF / DOCX file upload or parsing** — File parsers add brittle formatting failures, slow upload states, and heavy dependencies; text paste is instant and fail-proof.
- **No full resume document builder or layout styling** — The user already has their resume document open; we solve the hardest part (writing the bullets), not font formatting.
- **No cover letter generation** — A separate product modality that encourages fluff and dilutes the core tailoring engine.
- **No user accounts, sign-in, or database storage** — Zero friction to get started; the tool is an instant client utility with zero data persistence liability.
- **No interview prep or chat-based coaching** — Chat turns a 30-second workflow into an unfocused conversation.
- **No Word / PDF file export** — Clipboard copy preserves user flexibility and prevents layout corruption in external editors.

## 6. The signature detail

**The Before & After Impact Lens:** Each generated bullet isn't just displayed in isolation; it shows a subtle tag of the primary job skill it addresses (e.g., `Distributed Systems`, `Stakeholder Alignment`, `Revenue Growth`) and uses a clean, tactile "Copy" interaction that confirms with a swift green micro-animation (`Copied!`). It feels like a precision surgical tool, not an AI playground.

## 7. Success: how we know it worked

Pick ONE primary signal:

- **Primary:** ≥ 65% of sessions with valid inputs result in at least one bullet point copied to clipboard within 60 seconds of generation.
- **Secondary (optional, max 2):**
  - Median end-to-end generation latency under 3.5 seconds.
  - ≥ 25% of users click "Try Sample" or run a second tailoring run in the same session.
- **What we're NOT measuring:** Total page views, bounce rate, session length (shorter session with a copy is a win).

## 8. Open questions

- [ ] What is the optimal token/character ceiling for input job postings to guarantee sub-4s latency?
- [ ] Should the model return a fixed number of bullets (e.g., top 5) or preserve the exact count of input bullets?
- [ ] How should the engine handle cases where the resume has minimal or zero relevant skills matching the job description?

## 9. Handoff

- **For UX:** The layout must support seamless comparison and effortless one-click copying without vertical scroll thrashing between inputs and results.
- **For Eng:** Structured JSON generation latency via Gemini with p95 < 3.5s is the critical technical threshold that keeps the tool feeling instantaneous.
