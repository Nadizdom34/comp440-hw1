---
name: judge
description: Run the judge, which rates the tags on each item against the criterion the student wrote -- judge/criterion.md for movies, judge/criterion_users.md for people. Everything about it is in judge/README.md.
---

The judge is Claude reading the student's own criterion, and its answer is what Part 2 is
scored against. Part 3 runs the same script over `judge/users.csv`, and on that file the judge
reads `judge/criterion_users.md` instead.

Read `judge/README.md` and do what it says. That page is the whole of it: the two prompts,
the files, what the script does when it runs, how to run it, what it writes, and what you
may and may not say about the result.
