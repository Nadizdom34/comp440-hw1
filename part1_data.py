"""
Part 1: whose data is this?

    uv run python part1_data.py

Write your own cut rule and your two checks before you run anything here. Doing it in that
order is what Part 1 is asking for. What this script must print, under the labels shown:

    == (a) how much ==
        Rows in each of the four files, distinct users, distinct movies, and the share of
        all 32,000,204 MovieLens ratings this set holds.

    == (b) spread ==
        Ratings per user and ratings per movie: median, minimum and maximum of each. Tag
        applications per user and per movie: the same three. How many of the users who
        rated anything ever applied a tag, as a count and as a share.

    == (c) top tags, two ways ==
        The 20 most-used tags by number of applications, and the 20 most-used tags by number
        of distinct users who applied them. Print the two lists one after the other, with
        both numbers on every row, so you can see where a tag's two ranks differ.

    == (d) two checks ==
        Two claims from (a) to (c) re-derived by a route that does not reuse the code that
        produced them, printed with both numbers side by side and the word MATCH or DIFFER.
        Targets that exist in this data: the share of all 32M ratings the set holds
        (`data/README.md` says 15.6 percent); the number of distinct users who applied a
        tag (14,019); the rating count of the least-rated kept movie (83); the 6 tag
        rows whose text is literally `NA`, which vanish if a reader is built without
        `keep_default_na=False`.

No figures are required in Part 1. `WRITEUP.md` takes one interesting thing from
`data/README.md`, your own cut rule and the rule you rejected, how `data/make_compact.py`'s
rule differs from yours, and your two checks.
"""

import pandas as pd

from load_data import DATA, load_all

ALL_RATINGS = 32_000_204   # every MovieLens 32M rating, from data/README.md


def spread(counts, what):
    """Median, minimum and maximum of one per-user or per-movie count."""
    print(f"{what:<32} median {counts.median():>8,.1f}   min {counts.min():>6,}   max {counts.max():>7,}")


def readme_count(measurement):
    """The 'this subset' column of one row of the counts table in data/README.md."""
    for line in (DATA / "README.md").read_text().splitlines():
        cells = [c.strip() for c in line.strip("|").split("|")]
        if cells[0] == measurement:
            return int(cells[-1].replace(",", ""))
    raise KeyError(measurement)


def check(what, mine, theirs):
    print(f"{what:<32} code {mine:>10,}   check {theirs:>10,}   {'MATCH' if mine == theirs else 'DIFFER'}")


def part1_data(ratings, tags, movies, links):
    print("== (a) how much ==")
    for name, frame in [("ratings", ratings), ("tags", tags), ("movies", movies), ("links", links)]:
        print(f"{name:<8} {len(frame):>10,} rows")
    print(f"distinct users (in ratings)  {ratings['userId'].nunique():>8,}")
    print(f"distinct movies (in ratings) {ratings['movieId'].nunique():>8,}")
    print(f"movies with at least one tag {tags['movieId'].nunique():>8,}")
    print(f"share of all {ALL_RATINGS:,} MovieLens ratings: {len(ratings) / ALL_RATINGS:.1%}")

    print("== (b) spread ==")
    spread(ratings.groupby("userId").size(), "ratings per user")
    spread(ratings.groupby("movieId").size(), "ratings per movie")
    spread(tags.groupby("userId").size(), "tag applications per user")
    spread(tags.groupby("movieId").size(), "tag applications per movie")
    raters = ratings["userId"].unique()
    taggers = tags.loc[tags["userId"].isin(raters), "userId"].nunique()
    print(f"users who rated anything and ever applied a tag: {taggers:,} of {len(raters):,} "
          f"({taggers / len(raters):.1%})")

    print("== (c) top tags, two ways ==")
    # Raw tag strings, exactly as typed: no lowercasing, no trimming.
    by_tag = tags.groupby("tag").agg(applications=("userId", "size"), users=("userId", "nunique"))
    print("-- the 20 most-used tags by applications --")
    print(by_tag.sort_values(["applications", "users"], ascending=False).head(20).to_string())
    print("-- the 20 most-used tags by distinct users --")
    print(by_tag.sort_values(["users", "applications"], ascending=False).head(20).to_string())

    print("== (d) two checks ==")
    # First check, the student's route: the count data/README.md reports.
    check("tag applications", len(tags), readme_count("tag applications"))
    # Second check, the student's route: a plain read_csv with no settings, then groupby.
    t = pd.read_csv(DATA / "tags.csv.gz")
    check("movies with at least one tag", tags["movieId"].nunique(), len(t.groupby("movieId")))


if __name__ == "__main__":
    ratings, tags, movies, links = load_all()
    part1_data(ratings, tags, movies, links)
