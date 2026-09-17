# The judge

The judge is Claude, reading a paragraph you wrote and rating the tags on each item against
it. For movies that paragraph is `judge/criterion.md`, and its answer is what Part 2 scores
your own `score(movie, tag)` against. For people it is `judge/criterion_users.md`, which you
write in Part 3.

It is two prompts and a loop.

* **The system prompt**, `judge/system.md`, says how to answer. It is the same for
  everybody in the class.
* **The user prompt** is built fresh for each movie: your criterion, a blank line, the
  movie, then the tags to rate, one per line.
* **The loop**, `judge/judge.py`, sends that pair to Claude once per movie, five at a time,
  and writes down what comes back.

So the only thing that differs between two students' judges is the paragraph each of them
wrote. That is what makes one person's number comparable with another's, and it is why the
two criterion files are the only things in this directory you edit.

## The files

| file | what it is |
| --- | --- |
| `criterion.md` | **Yours.** One paragraph saying what "best describes" means for a movie, in your words: tell Claude and it writes the file, or write it yourself. It is graded, and nothing runs until you have replaced the one the template shipped. |
| `criterion_users.md` | **Yours**, and Part 3's. The same paragraph for a person. It ships as a placeholder, and the judge refuses `users.csv` until you have replaced it. |
| `system.md` | How the judge is told to answer. A dozen lines, and the same for everyone. |
| `judge.py` | The loop. About a hundred lines of code, meant to be read top to bottom. |
| `movies.csv` | The 100 movies the judge is asked about: `id, description, tags`. |
| `vocabulary.txt` | The 300 tags, one per line, lowercase. The judge rates tags from this list and no others. |
| `vocabulary_build.md` | How that list was built, and the top 30 with their counts. Read it before you write your criterion. |
| `ratings_movies.csv` | **Written by the run.** One row per movie and tag: `id, tag, rating`. |
| `ratings_movies.log` | **Written by the run.** The two lines the run printed. |
| `users.csv`, `ratings_users.csv`, `ratings_users.log` | Part 3's. You write the first; the run writes the other two. |

`movies.csv` has one row per movie. `description` is the title, its year and its genres.
`tags` is the vocabulary tags that appear on that movie, joined with `|` and sorted
alphabetically rather than by popularity, because the order of that list must not tell the
judge which tag is common. For the same reason the file carries no counts.

The hundred span the famous and the obscure: all 4,000 movies in the compact set were split
into five equal groups by rating count and 20 were drawn from each, under seed 440. Every
one of them carries at least 5 vocabulary tags, so the judge always has something to rank.

## How to run it

From the repo root:

    uv run python judge/judge.py judge/movies.csv

It takes a couple of minutes and spends a little of your Claude allowance. Running it a
second time costs that allowance again, so it refuses when `ratings_movies.csv` is already
there. If a run really did fail, `--force` makes it go again.

Part 3 runs the same script over a file of people that you write:

    uv run python judge/judge.py judge/users.csv

Same three columns, `id, description, tags`, and the answer lands in
`judge/ratings_users.csv`. What goes in the description column for a person is your design,
and it is a graded decision.

**Part 3 reads a different criterion, and the file's name is what picks it.** A file named
`users.csv` is rated against `judge/criterion_users.md`. A file named anything else is rated
against `judge/criterion.md`, the movie paragraph. There is no flag for this, so Part 3's file
has to be called `judge/users.csv`; a file called `judge/my_users.csv` would be rated against
the movie paragraph instead. The run prints which criterion it read before it asks for
anything, so you can see which one it picked.

The judge refuses `users.csv` while `criterion_users.md` is still the placeholder the template
ships. Write the people paragraph yourself, or tell Claude and it writes down what you said.
The movie paragraph is about films, and asking it to rate tags on people gives you a column of
1s and 2s.

## What happens when you run it

1. **It checks the items file is there.** A misspelled path stops the run with one line,
   before anything else happens.
2. **It checks your criterion**: `criterion_users.md` when the items file is named
   `users.csv`, and `criterion.md` for every other name. While that file still says what the
   template's copy said, word for word, the run stops: the criterion is graded and is yours to
   write. Only the whole paragraph counts as unchanged, so your own paragraph is yours even if
   it happens to open with the same few words.
3. **It reads the items file.** For `movies.csv` it also reads your ten movies out of the
   "My ten movies" slot in `WRITEUP.md` and describes them by the same rule. If that slot has
   no lines starting with a movieId, it says so and rates the file's own items only.
4. **It says which criterion it read, and what it is about to ask for**: how many items, and
   how many tag ratings. Part 3 asks you to keep an eye on that number.
5. **It asks.** One `claude -p` session per item, with no tools, no settings, no memory of
   this repo and no session file left behind, reading its prompt on standard input. The session sees your criterion, the one
   item and its tags, and nothing else: no counts and none of your scores. That is what makes
   its answer independent of yours.
6. **It reads the answers back.** One `tag, rating` line per tag, with the rating 1 to 5, and
   nothing else on the line.
7. **It asks once more** about any item that came back with fewer ratings than it had tags. A
   session can stop half way down its list and still exit as though it had finished. The
   first answer for a tag is the one kept, so a second ask can only fill holes.
8. **It writes the file and prints two lines**: items rated, tag ratings and how many items
   came back short, then the cost and the seconds. The same two lines go into
   `ratings_movies.log`.

## What the answer is for

`ratings_movies.csv` is read by `agreement.py`, which gives everyone the same number, and by
`results_viewer.py`, which shows you the disagreements one movie at a time. Those two are
the way to look at it.

Claude will not open `ratings_movies.csv` any other way, and will not tell you which
disagreements are worth reviewing or whose fault one is. Those are the sentences you are
graded on. It may tell you whether the run finished.
