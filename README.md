# COMP 440 — Uncovering Rating Patterns (with Claude)

In this assignment you will analyze the MovieLens 10M dataset — 10 million movie ratings from
real users — and build your way from raw data to a working, honestly-evaluated recommender
system. You will do this **with an AI coding assistant** (Claude Code), and that changes what
the assignment is about.

In past years, most of the effort here went into pandas wrangling. That work is now cheap:
your assistant can produce a complete, plausible-looking analysis in minutes. What it *cannot*
reliably do is make good judgment calls, catch its own statistical mistakes, or decide what a
result means. **That is your job, and it is what you will be graded on.** This repo's
`CLAUDE.md` configures Claude to act like a capable analyst-intern who does the mechanical
work but brings every decision to you. Read it — it is not a restriction, it is a description
of how professionals direct these tools.

You may work with a partner; if you do, put both names in your writeup and submit one repo.

## Learning objectives

By the end of this assignment you will be able to:

1. **Characterize real-world ratings data using robust descriptive statistics** — compute and
   visualize distributions on long-tailed, sparse data, and explain why raw means fail at
   small sample sizes and how damping/shrinkage fixes them.
2. **Decompose ratings into user bias, item bias, and interaction**, and use cosine similarity
   over co-rated vectors to uncover taste structure — including how normalization changes,
   even reverses, conclusions.
3. **Build and honestly evaluate a simple recommender** — an item-item kNN predictor evaluated
   on held-out data against the baselines it must beat.
4. **Direct and critically verify AI-assisted analysis** — make and defend judgment calls,
   predict results before running, detect statistically misleading output, and document your
   decisions.

## What you submit

Your repo (submit the URL), containing:

| File | What it is | Written by |
|---|---|---|
| your analysis code | scripts/notebook that produce every result | you + Claude (freely) |
| `WRITEUP.md` | answers, tables, figures, interpretation for every part | **you** (Claude may format tables/figures; the interpretation must be yours) |
| `DECISIONS.md` | your decision log: every judgment call, the alternative you rejected, and why | **you, in your own words** |
| `REFLECTION.md` | a short reflection on working with the AI | **you, in your own words** |
| `TRANSCRIPT.md` | log of your Claude Code sessions | auto-generated (see below) |

Commit as you complete each part. Your commit history is part of your submission — Part 0
must be committed before any analysis commits.

### Transcript capture

`TRANSCRIPT.md` is maintained automatically: a hook in `.claude/settings.json` runs
`dump_transcript.py` at the end of every Claude turn (approve the hook when Claude Code asks
on first launch). It records what you typed and what Claude said, with tool calls summarized
to one line; tool output and model reasoning are omitted. Just commit it along with your work.

Notes:
- **Do your assignment sessions in this repo's directory** — sessions run elsewhere (or on
  claude.ai) aren't captured.
- If the hook isn't running (you declined it, or you're pulling in a partner's sessions from
  another machine), run `uv run python dump_transcript.py` manually before committing — it
  merges without overwriting sessions already in the file. The `/export` command in Claude
  Code is a last-resort manual fallback.
- Never edit `TRANSCRIPT.md` by hand. It is regenerated.
- We don't read every line — we grade your writeup, decisions, and reflection. The transcript
  is what your `REFLECTION.md` cites and what we spot-check. Keep sessions on-task; the log
  is part of your submission.

## Setup

Requires Python ≥ 3.13 and [`uv`](https://docs.astral.sh/uv/).

```bash
uv sync
uv run python load_data.py   # downloads ML-10M (~65 MB) into data/ and sanity-checks it
```

Note: ML-10M ratings are on a **0.5–5.0 half-star scale** (the older 1M set used integers).

---

## Part 0 — Predictions (commit this BEFORE any analysis)

Fill in the prediction block at the top of `DECISIONS.md` and commit it. No analysis code may
be committed before this commit. You will not be graded on whether your predictions are
*right* — you will be graded on engaging with the ones that turn out wrong.

## Part 1 — Data orientation (delegate it, then verify)

Have Claude load the dataset and produce: a description of each column in both files, the
number of ratings/users/movies, the overall mean rating, how often each rating value is used,
the sparsity of the user×item matrix, and histograms of ratings-per-user and
ratings-per-item.

Your graded work, in `WRITEUP.md`:
- **Verify two of Claude's claims independently** (e.g., recompute sparsity by hand from the
  counts; spot-check a movieId→title lookup against the raw file). Show your verification.
- **State one pattern in the figures that Claude did not mention.**

## Part 2 — Robust statistics

Report the five most-rated movies, and the five highest- and lowest-rated movies using a
**damped (robust) mean** — a raw mean would let a movie rated 5.0 by three friends beat
*The Godfather*. You choose the damping constant K. Log the decision: what K, what else you
considered, why. Show one example where damping visibly changes the ranking.

## Part 3 — Normalizing ratings

Create the two normalized rating columns, using robust means throughout:
- `rating2` = rating − that user's (damped) average
- `rating3` = `rating2` − that item's (damped) average **of rating2** (not of raw ratings!)

In `WRITEUP.md`: verify both columns center near 0, report how the standard deviation changes
across rating → rating2 → rating3, and explain in your own words what variance each step
removed and why a similarity measure would want it removed.

## Part 4 — Co-rating and similarity

1. **Choose a Movie A** that is both *very popular* (≥ 1000 ratings) and *controversial*.
   Show the selection method (hint: standard deviation). **No two students may use the same
   Movie A — claim yours on the class sheet.** Log the decision with at least one rejected
   alternative.
2. Show the 20 movies most often **co-rated** with A (co-rated = number of users who rated
   both). What does this list actually measure? Is it taste similarity?
3. From that list choose a Movie B you predict will be *more* similar to A and a Movie C you
   predict *less* similar (log your reasoning **before** computing). Compute cosine
   similarity between (A,B) and (A,C) over their common raters, on all three rating columns
   (`rating`, `rating2`, `rating3`).
4. Interpret the 6 numbers. If raw and normalized similarities disagree about which pair is
   closer, which do you believe, and why?

## Part 5 — The review (centerpiece)

Have Claude compute, in one vectorized pass, the cosine similarity between A and **every**
other movie, for each of the three rating columns, and show the top 10 for each.

**A first-pass version of this analysis essentially always contains at least one
statistically misleading artifact.** Your job:

1. Find it. (Look hard at the top-10 lists. Would a knowledgeable friend believe them?)
2. Diagnose it as a statistics problem, not a code bug — explain *why* it happens.
3. Evaluate at least two fixes, implement one, and defend your choice in `DECISIONS.md`.
4. Re-run and interpret the corrected lists: what do the three rating types each surface,
   and why do they differ?

Also answer: what is the time complexity of the one-pass approach versus running the Part 4
pairwise method once per movie? Express it in terms of u (users), m (movies), n (ratings),
and b (co-raters), and explain which terms drop out and why.

## Part 6 — Build and evaluate a recommender

You have now built every component of an item-item collaborative filter. Close the loop:

1. Split ratings into train/test (you choose the split and seed — log it).
2. Compute on the **training set only**: the global mean, damped user means, and damped item
   means, and form the baseline predictor `baseline(u,i) = user_avg(u) + item_effect(i)`.
3. Build an item-item kNN predictor: predict each test rating as the baseline plus a
   similarity-weighted average of the user's residuals on the k most-similar items. You
   choose k, the similarity shrinkage, and the minimum-ratings cutoff for items in the model
   — log each.
4. Report test RMSE for: global mean, user mean, item mean, user+item baseline, and the kNN
   model. Report the kNN model's coverage (what fraction of test ratings it could score).
5. The honest question, answered in `WRITEUP.md`: **how much of the predictive power came
   from the baselines, and did the similarity model earn its complexity?**

## Part 7 — Reflection

One page in `REFLECTION.md`: a specific moment where Claude was wrong, misleading, or
overconfident and how you caught it (cite the moment); one judgment call where you overrode
or redirected it; and what you would delegate differently next time. Graded on the quality of
the catch and the candor, not on making the AI look good or bad.

---

## Grading

| Component | Weight |
|---|---|
| Analysis correctness (code runs, numbers are right, figures labeled) | 20% |
| Decision log + interpretation quality (Parts 0–4, 6 writeup) | 35% |
| Part 5 review: finding, diagnosing, and fixing the artifact | 20% |
| Part 6 evaluation and the "did it earn its complexity" discussion | 15% |
| Reflection | 10% |

A submission with flawless code but thin `DECISIONS.md` entries and boilerplate
interpretation caps out around a C. The weights are the point.

## Extra credit

- **Sensitivity sweep:** vary your damping K (or shrinkage λ) across two orders of magnitude
  and show how the Part 2 (or Part 5) rankings change. At what value do conclusions
  stabilize?
- **Empirical complexity:** time the naive pairwise similarity loop against the vectorized
  one-pass version as the number of items grows. Plot both and check the curves against your
  Part 5 complexity analysis.
- **Tags:** ML-10M ships `tags.dat`. Compute movie–movie similarity from tag profiles and
  compare the neighbors of your Movie A under tag similarity vs. rating similarity. What does
  each capture?

## FAQ

**What is a "damped/robust mean"?** Add K imaginary ratings at a prior (e.g., the global
mean) before averaging: `(sum + K·prior) / (count + K)`. Small-sample items get pulled toward
the prior; well-rated items barely move.

**What does "co-rated with Movie A" mean?** The number of users who rated both movies — the
users who would participate in a cosine similarity between them.

**Can Claude write my code?** Yes — all of it, if you direct it well. It cannot choose your
parameters, write your decision log, or do your interpretation. See `CLAUDE.md`.

**Claude refused to pick my K / Movie A for me. Why?** Working as intended. Choosing is the
assignment.
