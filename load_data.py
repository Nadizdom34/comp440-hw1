"""
The compact MovieLens set, read into pandas DataFrames.

    uv run python load_data.py      # prints the counts

Four readers, one per file:

    ratings = load_ratings()    # userId, movieId, rating, timestamp
    tags = load_tags()          # userId, movieId, tag, timestamp
    movies = load_movies()      # movieId, title, genres
    links = load_links()        # movieId, imdbId, tmdbId

or all four at once:

    ratings, tags, movies, links = load_all()

HW0's loader handed you plain Python records as well as DataFrames, so that a DataFrame was
one way of holding the data rather than the data itself. There are no records here: five
million ratings is too many rows to hold as five million objects, so pandas is the only way
in this time.

Two things this loader does that pandas would not do on its own, both of which change the
answers:

  * `keep_default_na=False` on every read. Pandas turns the strings "NA", "null", "None",
    "N/A" and a dozen others into missing values by default. Some rows in `tags.csv.gz` are
    literally those words, applied to a movie by a person on purpose, and the default reader
    deletes them.
  * `imdbId` and `tmdbId` are read as strings. IMDb ids have leading zeros that carry
    meaning ("0114709" is not 114709), and reading them as numbers throws the zeros away.

Files, all in `data/`: `ratings.csv.gz`, `tags.csv.gz`, `movies.csv`, `links.csv`. Pandas
unzips the gzipped ones as it reads; there is no unzip step and nothing is written to disk.
`data/README.md` says how the set was built, and `data/LICENSE.txt` is the license it ships
under.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parent
DATA = REPO / "data"
TEMPLATE = "shilad/comp440-hw1"   # your work goes in your own repo, never in this one


def warn_if_template() -> None:
    """Your work belongs in your own repo. Warn if `origin` is still the assignment template."""
    r = subprocess.run(["git", "remote", "get-url", "origin"], cwd=REPO, capture_output=True, text=True)
    if r.stdout.strip().removesuffix(".git").endswith(TEMPLATE):
        print(f"Warning: `origin` is the assignment template ({TEMPLATE}). Work in your own repo.")


def load_ratings() -> pd.DataFrame:
    """ratings.csv.gz: one rating per row. Columns userId, movieId, rating, timestamp.

    `rating` is 0.5 to 5.0 in half-star steps; `timestamp` is unix seconds."""
    return pd.read_csv(DATA / "ratings.csv.gz", keep_default_na=False)


def load_tags() -> pd.DataFrame:
    """tags.csv.gz: one tag application per row. Columns userId, movieId, tag, timestamp.

    One person can apply many tags to one movie, and can tag a movie they never rated.
    `keep_default_na=False` keeps the six tag rows whose text is "NA"."""
    return pd.read_csv(DATA / "tags.csv.gz", keep_default_na=False)


def load_movies() -> pd.DataFrame:
    """movies.csv: one movie per row. Columns movieId, title, genres.

    The year is inside the title, in parentheses: "Toy Story (1995)". `genres` is one string
    with the genres joined by "|", or "(no genres listed)"."""
    return pd.read_csv(DATA / "movies.csv", keep_default_na=False)


def load_links() -> pd.DataFrame:
    """links.csv: one row per movie. Columns movieId, imdbId, tmdbId.

    Both ids are read as strings, because imdbId has leading zeros that are part of the id."""
    return pd.read_csv(DATA / "links.csv", keep_default_na=False,
                       dtype={"imdbId": str, "tmdbId": str})


def load_all() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """All four frames: ratings, tags, movies, links."""
    warn_if_template()
    return load_ratings(), load_tags(), load_movies(), load_links()


def counts_line(ratings: pd.DataFrame, tags: pd.DataFrame, movies: pd.DataFrame) -> str:
    """The one-line summary run_all.py and the setup skill print."""
    return (f"{len(ratings):,} ratings, {len(tags):,} tag applications, "
            f"{len(movies):,} movies, {ratings['userId'].nunique():,} users")


if __name__ == "__main__":
    ratings, tags, movies, links = load_all()
    print(counts_line(ratings, tags, movies))
