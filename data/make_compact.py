#!/usr/bin/env python3
"""Build a compact, denser subset of the MovieLens 32M dataset.

This is the script that built the four data files in this directory. It ships so
that Part 1 can ask you to read it. You do not run it and you do not edit it:
running it needs the full MovieLens 32M download, about 250 MB unzipped, which
this repo does not include. The rule it applies, the seed and the resulting
counts are all written out in `data/README.md`.

Sampling design (applied in this order):

1. Movies: keep the top --movies movies by rating count in the full
   ratings.csv. Ties are broken by movieId ascending.
2. Ratings: keep only ratings on those movies; drop everything else.
3. Eligible users: users with at least --min-user-ratings ratings on the
   kept movies.
4. Included users: every eligible user who applied at least one tag to a
   kept movie ("taggers"), then a uniform random sample of the remaining
   eligible users (drawn with --seed) chosen so that the number of kept
   ratings is as close as possible to --target-ratings without exceeding
   110% of it. If the taggers alone already exceed 110% of the target, a
   uniform random sample of the taggers is taken instead and no
   non-taggers are added; the script reports which branch was taken.
5. Tags: keep tags.csv rows whose movie is among the kept movies and
   whose user is included.
6. movies.csv and links.csv: keep rows for the kept movies only.

Output files use the same names, columns and header lines as the
originals. The run is deterministic: the same source, target, seed,
movie count and minimum-ratings threshold always produce the same files.

Requires python3 with pandas and numpy.
"""

import argparse
import os
import resource
import sys
import time

import numpy as np
import pandas as pd

LICENSE_SENTENCE = (
    "The user may redistribute the data set, including transformations, "
    "so long as it is distributed under these same license conditions."
)

RATING_DTYPES = {
    "userId": "int32",
    "movieId": "int32",
    "rating": "float32",
    "timestamp": "int64",
}


def read_ratings(path):
    return pd.read_csv(
        path,
        usecols=["userId", "movieId", "rating", "timestamp"],
        dtype=RATING_DTYPES,
    )


def read_tags(path):
    # keep_default_na=False matters: 17 tag strings in ml-32m are the
    # literal text "NA" or "null", which pandas would otherwise turn into
    # missing values and write back out as empty fields.
    return pd.read_csv(
        path,
        usecols=["userId", "movieId", "tag", "timestamp"],
        dtype={"userId": "int32", "movieId": "int32", "tag": "string",
               "timestamp": "int64"},
        keep_default_na=False,
        na_values=[],
    )


def read_text_table(path):
    # movies.csv titles and links.csv ids must stay verbatim; imdbId has
    # significant leading zeros and 124 tmdbId values are empty.
    return pd.read_csv(path, dtype=str, keep_default_na=False, na_values=[])


def count_stats(series):
    a = series.to_numpy()
    return {
        "min": float(a.min()),
        "median": float(np.median(a)),
        "mean": float(a.mean()),
        "p90": float(np.percentile(a, 90)),
        "p99": float(np.percentile(a, 99)),
    }


def describe(ratings, tags, n_movies_csv):
    """Measurements computed the same way for the full and compact sets."""
    users = int(ratings.userId.nunique())
    movies = int(ratings.movieId.nunique())
    tagged_movies = pd.Index(tags.movieId.unique())
    per_user = ratings.groupby("userId", observed=True).size()
    per_movie = ratings.groupby("movieId", observed=True).size()
    scale = np.sort(ratings.rating.unique())
    return {
        "ratings": int(len(ratings)),
        "users": users,
        "movies_in_ratings": movies,
        "movies_in_movies_csv": int(n_movies_csv),
        "tag_applications": int(len(tags)),
        "tagging_users": int(tags.userId.nunique()),
        "tagged_movies": int(len(tagged_movies)),
        "user": count_stats(per_user),
        "movie": count_stats(per_movie),
        "share_ratings_on_tagged_movies": float(
            ratings.movieId.isin(tagged_movies).mean()),
        "share_movies_with_a_tag": float(len(tagged_movies) / n_movies_csv),
        "density": float(len(ratings) / (users * movies)),
        "rating_min": float(scale.min()),
        "rating_max": float(scale.max()),
        "rating_levels": int(len(scale)),
    }


def choose_users(counts, target, cap, rng, base=0):
    """Pick a prefix of a random permutation of `counts` (a Series of
    per-user rating counts) so that base + the selected total is as close
    as possible to `target` without exceeding `cap`. Returns the chosen
    user ids and the resulting total."""
    order = rng.permutation(len(counts))
    ids = counts.index.to_numpy()[order]
    cum = base + np.concatenate([[0], np.cumsum(counts.to_numpy()[order])])
    allowed = np.nonzero(cum <= cap)[0]
    k = int(allowed[np.argmin(np.abs(cum[allowed] - target))])
    return ids[:k], int(cum[k])


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--source", required=True,
                   help="path to the unzipped ml-32m directory")
    p.add_argument("--out", required=True, help="output directory")
    p.add_argument("--target-ratings", type=int, default=5_000_000)
    p.add_argument("--seed", type=int, default=440)
    p.add_argument("--movies", type=int, default=4000,
                   help="number of most-rated movies to keep")
    p.add_argument("--min-user-ratings", type=int, default=20,
                   help="minimum ratings on the kept movies for a user to be eligible")
    args = p.parse_args(argv)

    src, out = args.source, args.out
    target = args.target_ratings
    cap = int(round(target * 1.10))
    os.makedirs(out, exist_ok=True)
    t0 = time.time()

    print(f"reading {src}/ratings.csv ...", flush=True)
    ratings = read_ratings(os.path.join(src, "ratings.csv"))
    tags = read_tags(os.path.join(src, "tags.csv"))
    movies_txt = read_text_table(os.path.join(src, "movies.csv"))
    links_txt = read_text_table(os.path.join(src, "links.csv"))
    print(f"  {len(ratings):,} ratings, {len(tags):,} tag applications "
          f"({time.time() - t0:.1f}s)", flush=True)

    full = describe(ratings, tags, len(movies_txt))

    # 1. top-N movies by rating count, ties by movieId ascending
    per_movie = (ratings.groupby("movieId", observed=True).size()
                 .rename("n").reset_index()
                 .sort_values(["n", "movieId"], ascending=[False, True],
                              kind="mergesort"))
    kept_movies = per_movie.head(args.movies)
    keep_ids = pd.Index(np.sort(kept_movies.movieId.to_numpy()))
    nth_movie_ratings = int(kept_movies.n.iloc[-1])
    top_movie_ratings = int(kept_movies.n.iloc[0])

    # 2. ratings on those movies only
    r_top = ratings[ratings.movieId.isin(keep_ids)]
    t_top = tags[tags.movieId.isin(keep_ids)]

    # 3. eligible users
    per_user = r_top.groupby("userId", observed=True).size()
    eligible = per_user[per_user >= args.min_user_ratings]

    # 4. taggers first, then a random sample of the rest
    tagger_ids = pd.Index(t_top.userId.unique())
    is_tagger = eligible.index.isin(tagger_ids)
    tagger_counts = eligible[is_tagger]
    other_counts = eligible[~is_tagger]
    tagger_total = int(tagger_counts.sum())
    rng = np.random.default_rng(args.seed)

    if tagger_total > cap:
        chosen, kept_total = choose_users(tagger_counts, target, cap, rng)
        included = pd.Index(np.sort(chosen))
        n_taggers_included, n_others_included = len(chosen), 0
        branch = ("taggers alone exceed 110% of the target, so a uniform "
                  "random sample of taggers was taken and no non-taggers "
                  "were added")
    else:
        chosen, kept_total = choose_users(other_counts, target, cap, rng,
                                          base=tagger_total)
        included = pd.Index(np.sort(np.concatenate(
            [tagger_counts.index.to_numpy(), chosen])))
        n_taggers_included, n_others_included = len(tagger_counts), len(chosen)
        branch = ("all eligible taggers were included, then a uniform random "
                  f"sample of {len(chosen):,} non-tagging eligible users was added")

    # 5-6. assemble the output tables
    out_ratings = r_top[r_top.userId.isin(included)]
    out_tags = t_top[t_top.userId.isin(included)]
    keep_str = set(keep_ids.astype(str))
    out_movies = movies_txt[movies_txt.movieId.isin(keep_str)]
    out_links = links_txt[links_txt.movieId.isin(keep_str)]
    assert len(out_ratings) == kept_total, (len(out_ratings), kept_total)

    for frame, name in ((out_ratings, "ratings.csv"), (out_tags, "tags.csv"),
                        (out_movies, "movies.csv"), (out_links, "links.csv")):
        # the ml-32m files use CRLF line endings; match them exactly
        frame.to_csv(os.path.join(out, name), index=False, lineterminator="\r\n")
        print(f"wrote {name}: {len(frame):,} rows", flush=True)

    compact = describe(out_ratings, out_tags, len(out_movies))
    build_seconds = time.time() - t0
    peak_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0

    # verification
    checks = []
    checks.append(("every tags.csv userId appears in ratings.csv",
                   bool(out_tags.userId.isin(pd.Index(out_ratings.userId.unique())).all())))
    movie_ids = set(out_movies.movieId)
    checks.append(("every ratings.csv movieId appears in movies.csv",
                   set(out_ratings.movieId.astype(str).unique()) <= movie_ids))
    checks.append(("every tags.csv movieId appears in movies.csv",
                   set(out_tags.movieId.astype(str).unique()) <= movie_ids))
    checks.append(("rating scale unchanged (0.5 to 5.0, 10 levels)",
                   compact["rating_min"] == full["rating_min"]
                   and compact["rating_max"] == full["rating_max"]
                   and compact["rating_levels"] == full["rating_levels"]))
    checks.append(("no duplicate (userId, movieId) rows in ratings.csv",
                   not out_ratings.duplicated(["userId", "movieId"]).any()))
    checks.append(("links.csv and movies.csv cover the same movies",
                   set(out_links.movieId) == movie_ids))

    # report
    def row(label, a, b):
        return f"| {label} | {a} | {b} |"

    def num(x):
        return f"{x:,}" if isinstance(x, int) else f"{x:.4f}"

    lines = []
    lines.append(f"| measurement | full ml-32m | compact (N={args.movies:,}) |")
    lines.append("| --- | --- | --- |")
    for key, label in (("ratings", "ratings"), ("users", "users"),
                       ("movies_in_ratings", "movies in ratings.csv"),
                       ("movies_in_movies_csv", "movies in movies.csv"),
                       ("tag_applications", "tag applications"),
                       ("tagging_users", "tagging users"),
                       ("tagged_movies", "tagged movies")):
        lines.append(row(label, num(full[key]), num(compact[key])))
    for grp, gl in (("user", "ratings per user"), ("movie", "ratings per movie")):
        for st in ("min", "median", "mean", "p90", "p99"):
            lines.append(row(f"{gl}: {st}", f"{full[grp][st]:,.1f}",
                             f"{compact[grp][st]:,.1f}"))
    for key, label in (("share_ratings_on_tagged_movies",
                        "share of ratings on tagged movies"),
                       ("share_movies_with_a_tag",
                        "share of movies with at least one tag"),
                       ("density", "density (ratings / users x movies)")):
        lines.append(row(label, f"{full[key]:.6f}", f"{compact[key]:.6f}"))
    table = "\n".join(lines)

    print()
    print(table)
    print()
    print(f"sampling branch: {branch}")
    print(f"density ratio compact / full: "
          f"{compact['density'] / full['density']:.1f}x")
    print(f"taggers included: {n_taggers_included:,}; "
          f"non-taggers included: {n_others_included:,}")
    print(f"share of all tag applications retained: "
          f"{compact['tag_applications'] / full['tag_applications']:.4f}")
    print(f"least-rated kept movie has {nth_movie_ratings:,} ratings; "
          f"most-rated has {top_movie_ratings:,}")
    print(f"build time: {build_seconds:.1f}s; peak RSS: {peak_mb:,.0f} MB")
    print()
    for label, ok in checks:
        print(f"[{'PASS' if ok else 'FAIL'}] {label}")
    failed = [c for c, ok in checks if not ok]

    readme = f"""# Compact MovieLens subset

Built from MovieLens 32M (ml-32m) by `make_compact.py`.

## Sampling rule

1. Keep the top {args.movies:,} movies by rating count in the full
   `ratings.csv`, ties broken by movieId ascending. The most-rated kept movie
   has {top_movie_ratings:,} ratings; the least-rated kept movie has
   {nth_movie_ratings:,}.
2. Keep only ratings on those movies.
3. A user is eligible if they have at least {args.min_user_ratings} ratings on
   those movies.
4. Include every eligible user who applied at least one tag to one of those
   movies, then add a uniform random sample of the remaining eligible users so
   that the kept rating count lands as close as possible to
   {target:,} without exceeding {cap:,} (110% of the target).
5. Keep `tags.csv` rows whose movie is among the kept movies and whose user is
   included.
6. Keep `movies.csv` and `links.csv` rows for the kept movies only.

Branch taken in this build: {branch}.
Included users: {n_taggers_included:,} taggers and {n_others_included:,}
non-taggers.

Random seed: {args.seed}. The build is deterministic; rerunning with the same
source and flags reproduces these files byte for byte.

## Counts

| file | rows |
| --- | --- |
| ratings.csv | {len(out_ratings):,} |
| tags.csv | {len(out_tags):,} |
| movies.csv | {len(out_movies):,} |
| links.csv | {len(out_links):,} |

Distinct users: {compact['users']:,}. Distinct movies in ratings:
{compact['movies_in_ratings']:,}. Tagging users: {compact['tagging_users']:,}.
Tagged movies: {compact['tagged_movies']:,}.

Density (ratings / (users x movies)): {compact['density']:.6f}, against
{full['density']:.6f} for the full dataset, a factor of
{compact['density'] / full['density']:.1f}.

## Comparison with the full dataset

{table}

## License

This subset is a transformation of MovieLens 32M and is distributed under the
same conditions. From the ml-32m `README.txt`:

> {LICENSE_SENTENCE}

Cite: F. Maxwell Harper and Joseph A. Konstan. 2015. The MovieLens Datasets:
History and Context. ACM Transactions on Interactive Intelligent Systems
(TiiS) 5, 4: 19:1-19:19. https://doi.org/10.1145/2827872
"""
    with open(os.path.join(out, "README.md"), "w") as fh:
        fh.write(readme)
    print(f"\nwrote {os.path.join(out, 'README.md')}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
