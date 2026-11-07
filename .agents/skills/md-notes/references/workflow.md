# Note Construction Workflow

Use this workflow for a new chapter or a substantial rewrite. Small corrections can go directly to the relevant invariant.

## 1. Establish scope and authority

Record:

- course and note profile;
- textbook title, edition, author, and page range;
- latest lecture file and slide range;
- solution manual or additional references;
- starred, optional, or explicitly excluded sections;
- destination path and filename.

When slides and textbook disagree, follow the project profile's source hierarchy and flag factual conflicts. A newer slide deck supersedes an older deck for a lecture-based note, but does not silently override a textbook theorem.

## 2. Inspect the source before outlining

1. Determine whether the PDF is text-based or scanned.
2. For text-based notes, extract headings and search for formula/example anchors.
3. For scans, render pages at readable resolution and navigate by page image.
4. For PPTX/PDF slides, inspect the slides themselves when equations are fragmented or figures carry the explanation.
5. Make a section-to-page map so missing content is detectable.

Do not produce a chapter from the table of contents or prior summaries alone.

## 3. Build a content map

For every in-scope section record:

- definitions and assumptions;
- equations and their source numbers;
- derivations that must remain step-by-step;
- examples and exercise solutions;
- tables, figures, and experimental values;
- footnotes and supplementary/starred material;
- convention warnings and likely errors.

Then choose the local structure:

- textbook chapter: map → sections → four-part summary;
- lecture note: one-page overview → numbered lecture sections → error/quiz/assignment appendix.

Before drafting, check that every source section has a destination in the outline.

## 4. Draft with source fidelity

- Write one section at a time and keep the source open at the corresponding pages.
- Preserve logical connectives: "therefore", "if and only if", range of validity, and boundary conditions.
- Show algebra, integrations, approximations, and cancellations that a student would need to reproduce.
- For examples, state assumptions, perform the calculation, and check units or limits.
- Convert prose blocks into tables only when the items share comparable fields.
- Use code blocks for conceptual flow diagrams, not as a substitute for equations.
- Cite equation numbers from the source; label independently added derivations separately.
- Use consistent notation. Add an explicit note when two sections or books use the same symbol differently.

## 5. Handle figures deliberately

Include a figure only when it carries information that the text cannot convey efficiently.

- For slide-based notes, crop complete diagrams with labels and captions.
- For textbook-based notes, follow the project profile: some note libraries intentionally omit textbook figures.
- Verify that every crop contains the whole diagram, axes, labels, and source caption where useful.
- Store images in the same Obsidian attachment convention as adjacent notes.
- Check all relative links from the note's actual directory.

Never add a pack of decorative page screenshots. A smaller set of legible, explanatory figures is better.

## 6. Freeze the summary

For textbook chapters, derive the summary from the finished text:

1. formula quick reference;
2. concept flow;
3. common errors;
4. Chinese-English terminology.

For lecture notes, adapt the appendix fields recorded in the project profile. Do not add a section the local template forbids.

The summary must agree with the body: no alternate sign convention, stale equation number, or formula absent from the derivation.

## 7. Validate before handoff

Run the bundled static validator, then inspect:

- frontmatter and filename;
- section order and completeness;
- equations in tables and blockquotes;
- repeated or missing tags;
- all image targets;
- placeholders such as `TODO`;
- final summary against the body;
- final file location and absence of an unintended duplicate.

For render-sensitive notes, use the `md-to-pdf` skill to build a preview and inspect representative pages. Verify that MathJax actually rendered the formulas rather than only confirming balanced delimiters.

## 8. Report the result

State:

- destination file(s);
- source version and exact coverage;
- any source ambiguity or error corrected;
- figure count if figures were added;
- validation actually performed.

Do not claim that a full chapter is complete if some sections were only summarized or not read.
