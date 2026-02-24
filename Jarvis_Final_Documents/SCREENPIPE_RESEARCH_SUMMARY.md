# SCREENPIPE – COMPARISON & RESEARCH NOTES

**Date:** February 23, 2026  
**Context:** user asked for research on Screenpipe, which appears similar to Jarvis.

---

## What Screenpipe Is
- A local, open‑source desktop app that continuously records screen & audio.
- Indexes everything with AI (OCR, transcription) and allows natural‑language search.
- Runs on Windows/macOS/Linux (Rust + Tauri front‑end).
- Offers automation via a browser extension and CLI (formerly a CLI that is now discontinued).
- Privacy‑centric: data never leaves the machine unless user opts into paid cloud features.
- Provides a plugin system called "pipes" for extensibility; uses Claude/LLMs locally.

## Why It’s Relevant
Screenpipe and Jarvis share core themes:
- Local AI processing with privacy guarantee.
- Screen/audio capture + vision/ASR.
- Searchable memory of user actions.
- Desktop automation as part of the experience.

## Lessons for Jarvis
1. **Event‑driven capture:** Screenpipe’s docs mention "event‑driven capture, accessibility‑first text overlay" – we can use similar triggers instead of brute‑force screenshots.
2. **Plugin architecture:** Their "pipes" may inspire our workflow learner/automation modules; consider modular design.
3. **Local‑only model:** reinforces our decision to lazy‑download models and keep everything on‑device.
4. **Browser automation extension:** confirms that embedding automation into a WebView/extension is a common pattern.
5. **Resource footprint specs:** 0.5‑3 GB RAM, 10 % CPU – useful benchmarks for our own performance budgeting.

## Differences
- Screenpipe focuses on continuous recording and retrieval; Jarvis focuses on real‑time command execution and step-by-step feedback.
- Screenpipe’s automation is a side feature; Jarvis’s is the core.
- Their threat model includes a browser extension risk; ours is broader around full desktop control.

## Integration Ideas
- Adopt event‑driven capture for tasks that involve monitoring an app state (trigger OCR when a window title changes).
- Build our workflow engine as a "pipe" concept: each recorded execution becomes a reusable module.
- Use their resource numbers as sanity checks when designing the installer and runtime requirements.
- Investigate their Rust/Tauri code for patterns in cross‑platform automation; might borrow ideas for our Electron backend.

---

This summary will be kept with other research documents for reference during development.