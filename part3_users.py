"""
Part 3: what tags best describe a user?

    uv run python part3_users.py

The handout's Part 3 is the spec. One piece is written for you, the piece that has to agree
with `WRITEUP.md` line for line: reading the 20 ratings out of your "My 20 ratings" slot and
adding you to the ratings table as a user of your own. Everything after that is yours.

You are added under userId 999999. Real userIds in `data/ratings.csv.gz` stop at 200,935, so
that number cannot be a real person's, and it is easy to pick out of a printout.

What this script must print, under the labels shown:

    == (1) my ratings ==
        How many ratings were read out of your slot, how many lines it could not read a
        rating from, and how many rows the ratings table has with yours in it. Twenty
        ratings is what the handout asks for; the script reports what it found and leaves
        the count to you.

    == (2) score(user, tag) ==
        Your `score(user, tag)` over the users you are looking at, your own row included.
        Write it in this file as

            score(ratings_df, tags_df, movies_df) -> DataFrame[userId, tag, score]

        one row per user-tag pair, higher score meaning the tag describes the user better.
        Print your own ten best tags, and the number of rows and distinct users it returned.
        What the score is, and why you started there, is yours and goes in `WRITEUP.md`.
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

from load_data import load_all
from part2_tags import clean_tag, tag_labels

REPO = Path(__file__).resolve().parent
WRITEUP = REPO / "WRITEUP.md"

ME = 999999                 # your userId: above every real one, so it collides with nobody
SLOT = "My 20 ratings"      # the WRITEUP.md slot your ratings are read from


def read_my_ratings(writeup: Path = WRITEUP) -> tuple[pd.DataFrame, int]:
    """Your ratings from the "My 20 ratings" slot in WRITEUP.md, as movieId and rating.

    The same rule the judge uses for "My ten movies": every line in that slot starts with a
    movieId. The rating is the last number on the line, so the title between them is for
    people and may hold anything, the year included. Bare lines only: a bulleted or a
    numbered list reads as no ratings at all, or reads the list numbers as movieIds.

        296, Pulp Fiction (1994), 4.5

    A line whose last number is not a rating between 0.5 and 5.0 is left out and counted,
    because the year in a title is a number too: `296, Pulp Fiction (1994)` with the rating
    forgotten would otherwise be read as a rating of 1994. So is the `XXXX` an unfilled slot
    holds, which is why this is safe to run before you have written anything.

    Returns the ratings and how many lines were left out."""
    rows, skipped, inside = [], 0, False
    for line in writeup.read_text(encoding="utf-8").splitlines():
        if line.startswith("**"):            # a bold label opens the next slot
            inside = SLOT in line
            continue
        if not inside or not re.match(r"\s*\d", line):
            continue
        numbers = re.findall(r"\d+(?:\.\d+)?", line)
        rating = float(numbers[-1]) if len(numbers) > 1 else 0.0
        if not 0.5 <= rating <= 5.0:
            skipped += 1
            continue
        rows.append({"movieId": int(numbers[0].split(".")[0]), "rating": rating})
    return pd.DataFrame(rows, columns=["movieId", "rating"]), skipped


def add_me(ratings: pd.DataFrame, mine: pd.DataFrame) -> pd.DataFrame:
    """Your ratings appended to everybody else's, under userId ME.

    The timestamp is the newest one in the data: you rated these after everyone else did."""
    if mine.empty:
        return ratings
    mine = mine.assign(userId=ME, timestamp=int(ratings["timestamp"].max()))
    return pd.concat([ratings, mine[ratings.columns]], ignore_index=True)


# ------------------------------------------------------------------- yours to write ---

SEED = 440          # the seed for breaking ties at 5th place: arbitrary, but the same every run
KEEP_AT = 3.0       # a rated movie counts only when its rating is at least this
TOP = 5             # "top 5", for a movie's tags and for a user's own tags
OWN_MIN = 5         # a user needs this many distinct tags of their own for the own-tags path
# The ratings path: how many kept movies have the tag in their top 5 -> score. Capped at 5.
BY_MOVIES = {1: 3.0, 2: 3.5, 3: 4.0, 4: 4.5}
CAP = 5.0
OWN_TOP, OWN_OTHER = 5.0, 3.0   # the own-tags path: in the user's own top 5, and not
IRRELEVANT = 2.0                # the ratings path: in no kept movie's top 5 (not written as rows)


def top_n(df: pd.DataFrame, by: str, n: int = TOP) -> pd.DataFrame:
    """The n most-applied cleaned tags within each `by` group. Ties at the cutoff are broken
    by a seeded shuffle, so the pick means nothing and a rerun gives the same answer."""
    counts = df.groupby([by, "tag"]).size().reset_index(name="n")
    counts["shuffle"] = np.random.default_rng(SEED).random(len(counts))
    counts = counts.sort_values([by, "n", "shuffle"], ascending=[True, False, True])
    return counts.groupby(by).head(n)[[by, "tag"]]


def score(ratings: pd.DataFrame, tags: pd.DataFrame, movies: pd.DataFrame):
    """The student's score(user, tag), as written in the WRITEUP.md slot.

    Tags are cleaned by the Part 2 rule (`clean_tag`: ignore case and every space).
    - A user with at least OWN_MIN distinct tags of their own: 5 for a tag in their own top
      5 (by applications), 3 for every other tag they applied.
    - Everyone else: keep the movies they rated KEEP_AT or higher, take each movie's top 5
      tags (by applications, from everyone's tags), and count how many kept movies have the
      tag in their top 5: 1 -> 3, 2 -> 3.5, 3 -> 4, 4 -> 4.5, 5 or more -> 5.
      A tag in no kept movie's top 5 scores IRRELEVANT (2) and is left out of the rows.
    Vectorized: one merge of the kept ratings against the movies' top-5 lists."""
    tags = tags.assign(tag=clean_tag(tags["tag"]))
    distinct = tags.groupby("userId")["tag"].nunique()
    taggers = set(distinct[distinct >= OWN_MIN].index)

    own = tags[tags["userId"].isin(taggers)].drop_duplicates(["userId", "tag"])
    own_top = top_n(tags[tags["userId"].isin(taggers)], "userId").assign(top=True)
    own = own[["userId", "tag"]].merge(own_top, on=["userId", "tag"], how="left")
    own["score"] = np.where(own["top"].fillna(False).astype(bool), OWN_TOP, OWN_OTHER)

    kept = ratings[(ratings["rating"] >= KEEP_AT) & ~ratings["userId"].isin(taggers)]
    hits = kept[["userId", "movieId"]].merge(top_n(tags, "movieId"), on="movieId")
    by_rated = hits.groupby(["userId", "tag"]).size().reset_index(name="movies")
    by_rated["score"] = by_rated["movies"].map(BY_MOVIES).fillna(CAP)

    return pd.concat([own[["userId", "tag", "score"]], by_rated[["userId", "tag", "score"]]],
                     ignore_index=True)


def part3_users(ratings, tags, movies, links):
    print("== (1) my ratings ==")
    mine, skipped = read_my_ratings()
    print(f'{len(mine)} rating(s) read from the "{SLOT}" slot in WRITEUP.md.')
    if not len(mine):
        print(f'Nothing was read out of the "{SLOT}" slot. It is read one rating to a line, '
              f"with no bullets and no numbering: the movieId first, then the title, then "
              f"your rating, as in `296, Pulp Fiction (1994), 4.5`.")
    if skipped:
        print(f"{skipped} line(s) in that slot had no rating between 0.5 and 5.0 at the "
              f"end and were left out.")
    ratings = add_me(ratings, mine)
    if len(mine):
        print(f"{len(ratings):,} ratings with yours in, as userId {ME}.")
    else:
        print(f"{len(ratings):,} ratings, none of them yours yet.")

    print("== (2) score(user, tag) ==")
    scores = score(ratings, tags, movies)
    labels = tag_labels(tags)
    me = scores[scores["userId"] == ME].sort_values(["score", "tag"], ascending=[False, True])
    print(f"my ten best tags (userId {ME}), by score, ties alphabetical for display:")
    print(me.head(10).assign(label=lambda d: d["tag"].map(labels))[["tag", "label", "score"]]
          .to_string(index=False))
    print(f"{len(scores):,} rows over {scores['userId'].nunique():,} distinct users")


if __name__ == "__main__":
    ratings, tags, movies, links = load_all()
    part3_users(ratings, tags, movies, links)
