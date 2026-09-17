# COMP 440, HW1: Tags, Movies, and Users

**Fall 2026 · Individual · 6% of the course grade**
**Due Thu Oct 1, 8:00am Central**

Launched Thu Sep 17. Aim to finish Parts 0–2 in the first week. Questions go to
`#comp440-f26`; tell me there by Mon Sep 21 if anything does not work.

## Goals

* To work on data large enough to force you to be cautious and thoughtful.
* To turn a vague question into a definition you can implement and justify.
* To report a result with its context: coverage, sample size, etc.
* To evaluate an evaluator: use a ground truth and judge where it is wrong.
* To direct Claude across a two-week analysis and keep the judgments yours.

## Overview

Two questions about MovieLens tags and ratings:

1. **What tags best describe a movie?**
2. **What tags best describe a user?** Most people never tag, so this has to be inferred.

These are the questions of Sen, Vig and Riedl (2009). Neither has a right answer. They
are graded by a judge you run yourself: Claude, rating every tag against a paragraph you write
(Part 2, step 5).

The repo ships a compact subset of MovieLens 32M: about 5 million ratings and 1.2 million tags
on the 4,000 most-rated movies. `load_data.py` reads it, and `data/make_compact.py` is the
script that built it, which Part 1 asks you to read. Nothing in `data/` is yours to edit.

## How this works

In past years, most of the effort here went into pandas wrangling. Your assistant can now
produce a plausible-looking analysis in minutes. **Your job is to interpret results, guide
algorithms and overall strategy, and make judgement calls.**

You do all of this through Claude. It walks you through each part and fills `WRITEUP.md` as you
go; where a slot is in your own words, tell Claude the words or write them into the file
yourself, and Claude never composes them.

This repo's `CLAUDE.md` configures Claude to act like a capable intern who does the mechanical
work but leaves every decision to you. Read it; it describes how professionals direct these
tools. Claude makes every commit and pushes, once you say yes; you never type git.

### What you submit

| File | What it is |
|---|---|
| `part1_data.py` … `part3_users.py` | one per part; the docstring says what it must print; you and Claude write them |
| `run_all.py` | runs everything and lists what is still blank; do not edit it |
| `WRITEUP.md` | your answers, in your words, written down by Claude or by you; every choice with what you rejected and why. Claude may format tables and figures |
| `judge/criterion.md` | your paragraph saying what "best describes" means for a movie; **yours** |
| `judge/criterion_users.md` | the same for a person, written in Part 3; **yours** |
| `results_viewer.py` | the page comparing the four rankings for your ten movies and the least-rated ones; ships as a rough first draft that you improve |
| `judge/users.csv` and your user viewer | Part 3's; **yours**, and AI encouraged |
| `TRANSCRIPT.md` | log of your Claude Code sessions; written by Claude at each part checkpoint and before you submit |

Claude writes `TRANSCRIPT.md` at each part checkpoint and before you submit, and commits it
with your work. Do your assignment sessions in this repo's directory; sessions run elsewhere, or
on claude.ai, are not captured. Never edit it by hand. If the script that writes it fails on your
machine, tell me and go on: there is no penalty, and "Talk to me if..." below says why.

## The task

### Part 0 — Set up and formulate hypotheses

Fork this repo and clone your fork. In the clone, start `claude` and type `/setup`. Claude
does the rest and asks your name.

Then, before any analysis runs, give Claude your three predictions: a movie's three most-used
tags; how many people in 100 ever tag and whether one person can take over a movie's tag list.
One or two sentences each, including a justification, and Claude writes them into `WRITEUP.md`.

Do Part 0 before any analysis.

### Part 1 — Whose data is this?

**Read `data/README.md`** and tell Claude one interesting thing you found, for `WRITEUP.md`.

**You first.** Before opening `data/make_compact.py`, give Claude your rule for cutting 32
million ratings to 5 million, and why. Then read the script and tell Claude how its rule differs
from yours.

**Then Claude.** Have it report how much data there is, how ratings and tags are spread across
people and movies, and the most-used tags counted two ways: times added, and people who added.

**Check two of Claude's numbers yourself**, by a different route, and give Claude the route you
took and whether it matched. The `WRITEUP.md` slot names one good target.

### Part 2 — What tags best describe a movie?

**1. Pick a movie** with at least 500 ratings and 30 tags. Before you see any counts, have Claude
print its ten most-used tags in random order, and give Claude your order of them for the step 4
slot. Then have Claude list all its tags by how many times each was added. How do these tags fall
short of "best describing the movie"? Tell Claude the most misleading entry and why.

Then make a MovieLens account at movielens.org, rate the movie you picked, and add one tag to it.
Tell Claude what you noticed about how the site collects ratings and tags: what it suggested,
what it asked you for, and what it did with your tag.

**2. Study the movie tagging.** Who added the tags, and when? Ask Claude for one figure, when the
tags and the ratings arrived, and give Claude a sentence before you see it and one after. Then ask
for two tables: who added each tag, and how the people who added each top tag rated the movie.
Tell Claude two interesting details you learned.

**3. Define your own score.** Tell Claude your `score(movie, tag)` and have it write the code and
run it on every movie. Hints: a) clean up minor textual differences in the tags, and b) choose
distinctive rather than popular tags. Give Claude your justification, including which tags you
merged.

**4. Your own ranking.** For nine other movies you know well, ask Claude for the ten most-used
tags of each, in random order. Give Claude your ten movies, and your order of each tag list by how well *you* think the tags describe the movie, without looking at any data. 

**5. The tag judge.** We will use Claude Sonnet as a tag judge. You will write a definition, and
Sonnet will use it to rate the tags on those movies.

Tell Claude your paragraph on what makes a tag one that best describes a movie, or write it into
`judge/criterion.md` yourself, and have Claude run `/judge`.

The judge is two prompts. One is a **system prompt** that says how to answer; it is the same for
everybody in the class. The other is a **user prompt** built fresh for each movie: your paragraph,
a blank line, the movie, then the tags people put on it. The script sends that pair to Claude once
per movie, for the 100 movies it ships with plus your ten, five at a time, on Sonnet with no
reasoning. Because of what the prompt holds, the definition can't be "the tag most people used,"
for example.

One thing the paragraph must not be: your `score()` written out in words. If the judge is
applying your own rule, it agrees with you by construction and the agreement number stops
measuring anything.

Claude rates each tag 1 to 5, in `judge/ratings_movies.csv`. It takes a couple of minutes and
about 5% of your Claude allowance.

Then `agreement.py` gives you one number for each of the three ways you now have of ranking a
movie's tags: your `score()`, popularity, and your own order from step 4. The number is this: of
that method's top five tags on a movie, how many the judge rated 4 or 5, counted over all the
movies. If there's anything you don't understand, ask Claude to explain it or look it up.

The skill is a page of instructions, `judge/README.md`. Read it and any important files it references, then tell Claude, for `WRITEUP.md`, how the skill is built, what it does when
it runs, and why skills matter. 

**6. Inspecting the results.** `results_viewer.py` builds a page, `movie_results.html`, and it
is a **bad** viewer on purpose. Run it and look at the page. What does it show you that is
useful? What gets in your way?

Then study the results, and look hardest at the disagreements: the places where your method and
the Claude judge are furthest apart. Make at least three improvements to the viewer so you can
read those more easily, and have Claude log each one.

Once the page is tuned for you, tell Claude the three most important disagreements you find, for
`WRITEUP.md`, and one other high-level pattern.

### Part 3 — What tags best describe a user?

In this step, you will replicate Part 2, but for people. For each user, which tags best
describe that user?

Most people never tag. So a person's tags have to be worked out from what they rated: for each
tag, how they rated the movies carrying it.

You should go about this similarly to how you proceeded in Part 2. The Part 3 slots in
`WRITEUP.md` say what to record.

1. List 20 movies you have seen with the rating you would give each, and give Claude that
   list: the movieId, the title, and your rating, one per line, no bullets and no numbering.

2. Next, come up with `score(user, tag)` and tell Claude what it is. Start simply. You can
   always improve. Have Claude test it on your own data.

3. Ask Claude for qualitative (small data) and quantitative (big data) tools to help you
   improve the scoring function:
    * Ask for an adjustment or alternate version of the viewer for users and use it to view
      tags for 10 users (including you). The viewer should be optimized for *you*, the
      reviewer, think about the information that is most valuable to you.

    * Decide what the judge needs to see about a person, then write `judge/users.csv` in the
      same three columns the movie file uses, `id, description, tags`, and run the same judge
      on it: `uv run python judge/judge.py judge/users.csv`. What goes in the description column
      is your design and is a graded decision. The judge rates exactly the tags you put in the
      file, so which tags they are is your call too; your `score(user, tag)` is not restricted
      either way. **Part 3 has its own criterion**, and the judge picks it by the name of the
      items file: a file named `judge/users.csv` is rated against `judge/criterion_users.md`,
      and a file named anything else is rated against `judge/criterion.md`, the movie paragraph
      you wrote in Part 2. So name the file `judge/users.csv`. Tell Claude your paragraph for
      people, or write `judge/criterion_users.md` yourself. The movie paragraph is about films,
      and it rates tags on people badly. The script says which criterion it read and how many
      tag ratings it is about to ask for, before it asks for them. **A few hundred tag ratings
      is plenty.** 1,000 is about 5% of your Claude allowance and far more than you need. Be
      strategic about which ones you choose: the ones your score is most confident about, the
      ones near your cut, and your own.

    * Ask for a way to put your `score(user, tag)` and your judge's rating side by side on the
      pairs you judged. Part 2 had `agreement.py` for this; Part 3 does not, so it is a thing
      you specify. Say how you want a disagreement measured, because your score gives ranks and
      the judge gives 1 to 5, and whatever you choose decides which pairs you end up reading.

4. Use the tools above to support two improvements **to the scoring function**, and tell Claude
   what you changed and what showed it. Both improvements change `score(user, tag)`; changing
   the viewer or the judge is how you find one, not one of the two. The evidence for an
   improvement is what your judge and your viewer show on the pairs you chose, and everyone's
   judge is their own, so nobody's number is compared with anybody else's.

### Part 4 — Working with Claude

The last section of `WRITEUP.md`, and you give Claude these the way you gave it the rest. Five
things:

1. A moment where Claude was wrong or overconfident, how you caught it, and where it happened.
2. One call where you overrode it, and why.
3. What you would hand to Claude sooner next time.
4. Did Claude name the misleading tag in Part 2 step 1 before you did?
5. For the figure, would asking Claude "what does this show?" have produced your sentence?

Graded on the catch and the candor, not on making Claude look good or bad.

When everything runs, ask Claude to check the submission; it will walk through what is missing.
Then ask Claude to commit and push, and fill in the form:
https://forms.gle/DMHxZsafEr92fTfK6. Tell Claude when you have. It will say
**YOU ARE FINISHED!** Due **Thu Oct 1, 8:00am Central**.

## AI guidelines

**No AI**: every sentence in `WRITEUP.md` that says what something means or why you chose it,
and both judge criteria, `judge/criterion.md` and `judge/criterion_users.md`. Claude never composes, edits or rewords them; it writes down what you
said, word for word. Every number names the script that printed it.

**Never edited by anyone**: `TRANSCRIPT.md`, `agreement.py`, `judge/judge.py`, and in `judge/`
the vocabulary, `system.md` and `movies.csv`, and `data/`, which carries the MovieLens license.
Not yours to change: `load_data.py`. Read any of them you like; that is the point of
`judge/judge.py`, which stays as it shipped. The `judge/users.csv` you write for Part 3 is yours.

**AI encouraged**: all the code, the figure and the tables, the extra credit, and fixing `results_viewer.py`
once you have said what is wrong with it.

## Rubric

I grade your process (through your transcript), your code, and your answers.

| Component | Weight |
|---|---|
| Correctness: `run_all.py` reruns from the shipped data; numbers match the code; the figure labeled | 15 |
| Decisions: predictions with whys, revisited; every choice with a rejected alternative; the figure's two sentences | 30 |
| Part 2: the misleading entry; the definition justified; the judge skill described; the agreement read; the viewer improved; the three disagreements explained | 25 |
| Part 3: your ratings and what your score says about you; the score justified; the user viewer; what you show the judge about a person; the two improvements with their evidence | 20 |
| Working with Claude | 10 |

Inside the Decisions line, the figure's two sentences are worth about 3 points. Inside the
Part 2 line, agreement with the judge is worth about 5, never more; otherwise the assignment
becomes "match the judge." Inside the Part 3 line, agreement with your own judge is worth about
3. The rest of each line is your decisions and your reading of the results.

A submission with flawless code but thin decision entries and boilerplate interpretation caps
out around a C. The weights are the point.

## Extra credit

- **A recommender from tags alone.** Set aside a random 10 percent of ratings under a stated
  seed and predict them from the rest, cutting any tag added after a set-aside rating. Models:
  the overall average; damped averages per user and per movie; both combined; item-to-item
  neighbors from the Sep 17 class; and a tag model matching each movie's tags to the user's tag
  description. Report the error and how many ratings each model could predict, split by how
  many ratings a movie has. Then: how much came from the simple averages, and did either model
  earn its complexity, and for which movies?
- **A different compact set.** Rebuild with another N (`data/make_compact.py --movies`), rerun
  one part, and say what moved. The script ships in `data/`, and running it needs the full
  MovieLens 32M download, which this repo does not include.
- **How much does K matter?** Vary your damping K across two orders of magnitude; where do the
  conclusions stop moving?

## Talk to me if...

**You notice something is odd or confusing.** This assignment is new this year.

**The template changes after launch.** If I have to fix something in it, I will say so in
`#comp440-f26`, and Claude can merge the change into your fork when you ask.

**You would rather not use Claude.** Talk to me by Tue Sep 22; there is no grade effect.

**Claude, or something else, is down.** A reported problem never costs you points; post in
`#comp440-f26` or email me. An outage of more than about half a day extends the deadline by 48
hours.

**Claude refuses to pick your K, your movie, or your definition, or to do the analysis for
you.** Working as intended; choosing is the assignment.

## FAQ

**What is a "damped mean"?** Add K imaginary ratings at the overall average before averaging:
`(sum + K·average) / (count + K)`. Three ratings get pulled toward the average; a thousand barely
move. The same trick works for a tag added three times.

**What if I think the judge is wrong?** Say so in your write-up, with the reason. It is one run
of one model reading a paragraph you wrote. Sometimes the paragraph is what is wrong; say that
too. But "the judge is wrong" needs an argument about that movie.

## A note on the tag genome

The tag genome (Vig, Sen and Riedl, 2012) scores how well about 1,100 tags fit every MovieLens
movie: this assignment's question, answered at scale. We do not use it, because its model was
trained partly on these ratings, so grading against it would be grading your answer against a
bigger version of your own method. Read about it after you submit.
