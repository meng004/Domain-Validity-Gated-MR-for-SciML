# Academic Pipeline Progress and Quality Update

> Date: 2026-06-05  
> Source checked: `paper/ist-submission/main.tex`  
> PDF checked: `paper/ist-submission/main.pdf`  
> Mode: academic-pipeline progress + quality assessment  
> Figure policy: generated figures remain excluded. They are not inserted into the current manuscript.

## 1. One-Sentence Verdict

The paper has moved from a well-framed research plan toward a real method paper, but it is not yet ready for integrity check, peer-review simulation, or submission.

The main improvement is concrete: the Method section now contains worked examples that show how candidate relations become executable MR assets. The main blocker is also concrete: the manuscript still lacks verified references, executable MR artifacts, SUT setup records, run logs, and experiment ledgers.

## 2. Current Pipeline Position

| Pipeline stage | Current status | Judgment |
|---|---|---|
| Stage 1. Research | Mostly adequate for continued writing | The research position is coherent: SciML validation, OOD transformations, domain-validity-gated MR identification, and MeshGraphNets cylinder-flow SUTs. |
| Stage 2. Write | In progress, improved | The manuscript now has an IST-style structure, research questions, method, empirical design, and worked examples. It still needs stronger related work and artifact-level detail. |
| Stage 2.5. Integrity | Not ready | Several references still need metadata verification, and empirical claims are intentionally blocked because real logs and ledgers do not yet exist. |
| Stage 3. Review | Too early | A formal review now would mainly repeat known blockers rather than produce new insight. |
| Stage 4. Revise/finalize | Not applicable | The paper is not yet at revision or packaging stage. |

Pipeline decision: continue Stage 2 writing, but aim the next pass at Stage 2.5 preparation.

## 3. Evidence From the Current Manuscript

| Item | Current evidence |
|---|---|
| Manuscript format | IST submission folder exists and `main.pdf` is available. |
| PDF length | 24 pages. |
| Approximate word count | About 5.1k--5.3k stripped-source words, depending on counting method. |
| References | 22 BibTeX entries. |
| Figures | No `includegraphics` or `figure` environment is currently inserted. |
| LaTeX hard errors | No fatal error, LaTeX error, undefined citation, or undefined reference was found in the checked log scan. |
| Remaining TeX warnings | Many overfull/underfull boxes remain, mainly in dense tables and long technical terms. |
| Result claims | Results are explicitly blocked until MR cards, SUT configurations, run logs, and experiment ledgers exist. |
| LLM role | Correctly limited to candidate generation and evidence organization, not final MR validity judgment. |

## 4. Quality Scores

| Dimension | Score | Change since previous check | Diagnosis |
|---|---:|---|---|
| IST fit | 4 / 5 | Stable | The paper fits IST if it stays focused on software testing, validation, and reproducible MR construction. |
| Research question clarity | 4 / 5 | Stable to slightly improved | RQ4 is now better bounded: expert MR design is primary; LLM/generic generation and rollout accuracy are secondary or diagnostic. |
| Novelty positioning | 3.5 / 5 | Slightly improved | The paper no longer sells MT itself. It sells SciML-specific validity-gated MR identification. The closest-work contrast still needs verification. |
| Method specificity | 3.5 / 5 | Improved | Worked examples make the rubric more operational. The next step is to turn these examples into actual card/schema artifacts. |
| Empirical design | 3 / 5 | Stable | SUTs, comparators, metrics, and statistics are planned. Feasibility evidence is still missing. |
| Evidence strength | 1.5 / 5 | Stable | The manuscript is honest, but it has no empirical results yet. |
| Related work | 2.5 / 5 | Stable | The structure is usable, but newer and closest references must be verified before strong claims are made. |
| Writing quality | 3.5 / 5 | Stable to slightly improved | The argument is clearer after the worked examples. Some parts still sound like a protocol. |
| Figure readiness | 1 / 5 | Unchanged | Existing generated figures should remain out of the manuscript. |
| Submission readiness | 2.5 / 5 | Slightly improved | Template and structure are in place, but evidence and integrity gates remain open. |

Overall quality: promising, but not review-ready.

## 5. What Has Improved

### 5.1 The method is less abstract

The worked examples are the most important improvement. They show that the rubric is not just a list of questions. It can change the status of a candidate relation:

- node permutation becomes a retained representation MR;
- mirror-y symmetry becomes a conditional physical-symmetry MR;
- discrete divergence becomes a qualified continuity-constraint MR whose verdict depends on the numerical operator and tolerance evidence.

This supports the paper's core claim: MR identification for SciML is a validity problem, not just a generation problem.

### 5.2 The comparison design is less inflated

The paper now treats expert MR design as the primary comparator. This is reasonable because the proposed method tries to make expert reasoning explicit, reproducible, and executable.

LLM-generated candidates, generic MR-generation methods, residual/UQ diagnostics, and rollout accuracy are no longer described as enemies to defeat. They are positioned as candidate sources, scope contrasts, or diagnostic evidence. This is more credible.

### 5.3 Claim discipline is good

The draft repeatedly avoids overclaiming:

- NOETHER is used as an organizing structure, not as proof of physical validity.
- LLMs are not used as final MR judges.
- Results are blocked until evidence exists.
- A violation is not automatically called a program fault.
- Three MeshGraphNets-family SUTs are not generalized to all SciML.

This discipline is a strength and should be kept.

## 6. Main Remaining Problems

### Problem 1. The paper still lacks executable artifacts

The phrase "executable MR asset" is now better explained, but the repository still needs at least one real asset format or schema. Without it, reviewers may read the method as well-written advice rather than a reproducible testing method.

Minimum next evidence:

- one MR card file;
- one candidate ledger;
- one verdict ledger schema;
- one runner configuration example;
- one clear link from paper table fields to artifact fields.

### Problem 2. Related work is not yet integrity-ready

Several entries still require metadata or venue verification. Until this is fixed, the related-work contrast cannot safely carry the paper's novelty claim.

Minimum next evidence:

- reference ledger with DOI/source/status;
- closest-work table;
- downgraded wording for any unverified work;
- deletion or replacement of any unverifiable citation.

### Problem 3. Empirical design is planned but not demonstrated

The planned SUT list and evidence map are useful, but the paper still has no SUT configuration records, no run logs, no executable-case counts, and no relation-level verdict data.

Minimum next evidence:

- SUT inventory with repository URL, commit, checkpoint, data, and runtime status;
- transformation sampling plan;
- MR execution ledger;
- pass/fail/skip/out-of-domain/inconclusive verdict definitions in data form.

### Problem 4. Tables are too dense for submission

The manuscript compiles, but many overfull and underfull warnings come from dense tables and long terms. This is not a scientific blocker, but it will hurt readability and production quality.

Minimum next action:

- simplify the largest tables;
- move bulky schema-like content to appendices if needed;
- reduce long inline technical strings in narrow columns.

### Problem 5. Figures should stay out for now

The figure files are useful as planning drafts, but they are not yet publication-quality. The current paper is better without weak figures than with diagrams that flatten the argument.

Minimum next action:

- redesign only one method figure after artifact schema stabilizes;
- do not insert result figures until real data exists.

## 7. Argument-Chain Check

The argument chain is now mostly coherent:

1. SciML surrogates are useful, but OOD transformed inputs create validation uncertainty.
2. Accuracy-only evaluation is important, but it is single-case evidence and cannot express relation-level validity.
3. MT can test source/follow-up relations without a full oracle.
4. In SciML, candidate MRs are dangerous unless their physical and numerical validity domain is explicit.
5. The paper proposes a domain-validity rubric and a NOETHER-informed way to organize candidate relations.
6. Retained relations become executable MR assets with transformations, mappings, metrics, tolerances, exclusions, and verdicts.
7. Relation-level verdicts can help describe where a SUT is unreliable under OOD transformations.
8. The final empirical claim is still pending real artifacts and logs.

The weakest link is step 6 to step 7. The paper explains the transition, but does not yet show repository-level evidence that the transition has been executed.

## 8. Readiness Gates

| Gate | Status | Why |
|---|---|---|
| Problem framing gate | Pass | The research need is clear and defensible. |
| Journal-fit gate | Pass with caution | IST is plausible if the paper remains a testing/V&V method paper. |
| Method clarity gate | Partial pass | Worked examples help, but executable assets are not yet shown. |
| Related-work gate | Not pass | Closest references need verification. |
| Evidence gate | Not pass | No experiment ledger or SUT results yet. |
| Formatting gate | Partial pass | PDF exists, but tables need cleanup. |
| Figure gate | Not pass | Figures should remain excluded. |
| Submission gate | Not pass | Too early. |

## 9. Recommended Next Task

The next best task depends on whether the next working session is a writing session or an experiment-building session.

If the next session is writing-focused, do this first:

1. Build a reference ledger.
2. Verify closest works.
3. Rewrite the related-work contrast and contribution paragraph using only verified sources.

If the next session is experiment-focused, do this first:

1. Create the executable MR asset schema.
2. Instantiate one MR card for node permutation.
3. Create empty but real candidate/verdict ledger files.
4. Link these artifact fields back to the Method section.

My recommendation is to do the reference ledger next if the immediate goal is manuscript quality, and to do the MR asset schema next if the immediate goal is making the paper empirically real.

## 10. Bottom Line

The paper is moving in the right direction. The current draft is no longer just an idea memo: it has a clear IST-facing problem, a bounded claim, research questions, a method structure, and worked examples.

But the paper is not yet a finished method paper. It needs two kinds of hard evidence before a serious review: verified scholarly positioning and executable research artifacts. Until those exist, the correct pipeline state is:

**Stage 2 writing continues; Stage 2.5 integrity is the next target; Stage 3 review should wait.**
