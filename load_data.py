"""
Download and load the MovieLens 10M dataset.

Run once to fetch the data (~65 MB zipped):

    uv run python load_data.py

Or import from your analysis code:

    from load_data import load_ratings, load_movies
"""

from pathlib import Path
import urllib.request
import zipfile

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent
DATA_DIR = REPO_ROOT / "data"
ML_DIR = DATA_DIR / "ml-10M100K"
ZIP_URL = "https://files.grouplens.org/datasets/movielens/ml-10m.zip"


def download_if_missing():
    if ML_DIR.exists():
        return
    DATA_DIR.mkdir(exist_ok=True)
    zip_path = DATA_DIR / "ml-10m.zip"
    if not zip_path.exists():
        print(f"Downloading {ZIP_URL} (~65 MB)...")
        urllib.request.urlretrieve(ZIP_URL, zip_path)
    print("Unzipping...")
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(DATA_DIR)


def load_ratings() -> pd.DataFrame:
    """userId, movieId, rating (0.5-5.0 half-stars), timestamp (unix seconds)."""
    download_if_missing()
    return pd.read_csv(
        ML_DIR / "ratings.dat",
        sep="::",
        engine="python",
        names=["userId", "movieId", "rating", "timestamp"],
    )


def load_movies() -> pd.DataFrame:
    """movieId, title (with year), genres (pipe-separated)."""
    download_if_missing()
    return pd.read_csv(
        ML_DIR / "movies.dat",
        sep="::",
        engine="python",
        names=["movieId", "title", "genres"],
        encoding="latin-1",
    )


def load_tags() -> pd.DataFrame:
    """userId, movieId, tag (free text), timestamp. Extra credit only."""
    download_if_missing()
    return pd.read_csv(
        ML_DIR / "tags.dat",
        sep="::",
        engine="python",
        names=["userId", "movieId", "tag", "timestamp"],
        encoding="latin-1",
    )


if __name__ == "__main__":
    ratings = load_ratings()
    movies = load_movies()
    print(f"OK: {len(ratings):,} ratings, {ratings['userId'].nunique():,} users, "
          f"{len(movies):,} movies in catalog.")
