---
name: setup
description: First-time setup for HW1, run once after cloning the fork. Adds the upstream remote, installs dependencies, checks the data loads, records the student's name and date, and commits. Run it again if anything breaks or to check a setup is complete.
---

Do these in order and show what you ran. Skip what is already done. If something fails, say
in plain words what it means and what to change, and stop there.

1. Add the `upstream` remote if it is missing:
   `git remote add upstream "${HW1_UPSTREAM:-https://github.com/shilad/comp440-hw1}"`
   It is there in case a fix to the template has to go out mid-assignment. `HW1_UPSTREAM` is
   normally unset, and then the address shown above is the one used.
2. `uv sync`, then `uv run python run_all.py`. It prints the counts, three "unimplemented"
   lines, and a list of what is still missing. The list is long on the first day; that is what
   it is for.
3. Ask their name, and fill `**Name:**` and `**Date:**` at the top of `WRITEUP.md`. Those two
   are yours to compose; every other slot in that file you fill from their own words.
4. Commit as `Name and date`.

Then say setup is done and Part 0 is current: three predictions, in their own words, with a
reason for each, committed before any analysis.
