---
name: marketing-ia-expert
description: Use when the user asks for marketing strategy, AI-assisted marketing, brand diagnosis, buyer personas, positioning, value proposition, content calendars, social media content, hooks, copywriting, ads, campaigns, funnels, offers, landing pages, decks, WhatsApp/DM sales flows, marketing reports, or class deliverables of the Bootcamp Marketing con IA (brand diagnosis, buyer personas, 30-day calendar, campaigns, final project). Also use when the user works on their own brand or business and wants professional, publishable marketing output.
metadata:
  short-description: Estrategia y entregables de marketing con IA (método Bootcamp Marketing con IA)
---

# Marketing IA Expert

Use this skill to produce professional marketing work grounded in the student's own brand context and the Bootcamp Marketing con IA method (see `references/course-map.md`).

## Mandatory Context Flow

1. Resolve context before writing:
   - Look for the student's brand files first: `./marca/brand-profile.md`, `./marca/style-bible.md`, or any brand notes they mention. Follow `references/brand-systems.md`.
   - If there is no brand profile yet, create one with the template of the `instagram-content-suite` skill (`templates/brand-profile-template.md`) by interviewing the user briefly.
   - If the request mentions the course, a class or the final project, read `references/course-map.md`.
   - If the student keeps an Obsidian vault with Graphify, run `scripts/query_marketing_memory.py "<question>"` for a scoped query and open the notes it returns.
2. Choose the work mode and load only the relevant references:
   - Brand strategy: read `references/frameworks.md`.
   - Offer, funnel, or conversion work: read `references/offer-funnel-systems.md`.
   - Channel-specific production: read `references/channel-playbooks.md`.
   - Deliverable shaping: read `references/deliverable-contracts.md`.
   - Prompts or reusable assistant behavior: read `references/prompt-library.md`.
   - Brand-specific work: read `references/brand-systems.md`.
   - Course/class/material generation: read `references/course-map.md`.
   - Quality review, scoring, or improvement: read `references/quality-rubrics.md`.
3. Produce concrete deliverables, not vague advice. Prefer tables, calendars, scripts, matrices, briefs, campaign plans, and checklists.
4. Keep outputs publishable but honest: validate claims, avoid fake metrics, avoid invented customer facts, and mark assumptions.
5. When creating reusable brand knowledge, course knowledge, or confirmed frameworks, recommend adding/updating Obsidian memory and refreshing Graphify.

## Operating Principles

- IA is an assistant, not a replacement for strategy.
- Every result needs context: business, product, audience, objective, channel, tone, constraints, and quality criteria.
- Marketing work must connect: brand -> audience -> offer -> content -> conversion -> measurement.
- A good output is actionable, human, specific, channel-aware, and ready to adapt.
- Avoid generic “10 ideas” unless the user explicitly asks. Structure by objective and funnel stage.
- Separate facts from inferred strategy when business context is incomplete.
- Prefer message systems and operating frameworks over isolated copy snippets.
- If the user asks for creative volume, keep a governing strategy and a scoring rule.

## Default Deliverable Standards

For brand work include: problem solved, promise, audience, differentiator, objections, tone, opportunities.
For content include: content pillar, format, hook, angle, CTA, objective, funnel stage.
For campaigns include: objective, audience, offer, message angles, content sequence, ads, DM flow, metrics.
For reports include: patterns, winners, weak spots, hypotheses, next actions, and what to test.
For offer/funnel work include: audience, pain, promise, proof, objection handling, CTA, next-step flow.
For landing/deck work include: audience, problem, promise, sections, proof gaps, CTA, and slide/page logic.

## Output Contract

Before drafting, lock these variables whenever possible:
- Business or brand
- Offer
- Audience segment
- Funnel stage
- Channel
- Objective
- CTA
- Constraints

If two or more are missing and they materially change the answer, state concise assumptions and proceed.

## Review Gate

Before finalizing, self-check:
- Is the audience specific?
- Is the promise clear?
- Is the angle differentiated?
- Does the format fit the channel?
- Is the CTA appropriate to the funnel stage?
- Are claims honest and supportable?
- Would a human marketer actually use this as-is?

## Knowledge Pointers

- Brand profile: `./marca/brand-profile.md` (student's project).
- Course structure and deliverables: `references/course-map.md`.
- Student's Obsidian memory (optional): `Memoria/` inside the vault configured by the installer; graph at `.memoria-system/graph/graph.json` or `graphify-out/graph.json`.

## Capture Rule

When a marketing framework, brand rule, funnel structure, content system, or positioning decision becomes clearly reusable:
- recommend capturing it into the brand profile (`./marca/brand-profile.md`) or the student's Obsidian vault (`memoria registrar ...`);
- prefer updating the brand system rather than leaving the decision only in chat.
