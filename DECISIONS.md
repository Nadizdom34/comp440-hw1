# Decision Log

Name(s):

## Part 0 — Predictions (fill in and COMMIT before any analysis)

Answer in a sentence each. You are graded on engaging with the ones you get wrong, not on
being right.

1. Which will have a higher robust average rating: the most-*rated* movies, or movies
   overall? Why do you think so?

   >

2. Roughly what fraction of all possible (user, movie) rating cells do you think are filled?

   >

3. Name a movie you expect to be among the most "controversial" (high disagreement). Why?

   >

4. When ratings are normalized (user bias removed, then item bias removed), do you expect a
   pair of same-genre blockbusters to look *more* or *less* similar than before? Why?

   >

5. In Part 6, how much better (test RMSE) do you expect the similarity-based recommender to
   be than the simple user+item baseline: a lot, a little, or none? Why?

   >

## Decisions

One row per judgment call. Add rows as you go — at minimum: damping K (Part 2), Movie A
(Part 4), Movie B and C predictions (Part 4), your Part 5 fix, and the Part 6 split / k /
shrinkage / cutoff. "Why" must be your own reasoning, not a restatement of the assistant's.

| Part | Decision | What I chose | Alternative I considered | Why I chose mine |
|---|---|---|---|---|
| 2 | damping K for item means | | | |
| 4 | Movie A | | | |
| 4 | Movie B (predicted more similar) | | | |
| 4 | Movie C (predicted less similar) | | | |
| 5 | fix for the artifact | | | |
| 6 | train/test split + seed | | | |
| 6 | k (neighbors) | | | |
| 6 | similarity shrinkage | | | |
| 6 | min ratings for model items | | | |

## Predictions revisited (fill in at the end)

Which Part 0 predictions were wrong, and what did you learn from each miss?

>
