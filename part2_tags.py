"""
Part 2: what tags best describe a movie?

    uv run python part2_tags.py

Steps 1 to 4 of the handout's Part 2 live here, plus the scores and the rankings that steps 5
and 6 need. The judge itself runs through `/judge`, and its answer is read through
`agreement.py` and `results_viewer.py`. What this script must print, under the labels shown,
and what it must write:

    == (1) the obvious answer ==
        Your chosen movie's title, its rating count and its tag-application count, then
        every tag applied to it with how many times it was applied, most-applied first.
        Pick a movie with at least 500 ratings and 30 tag applications. The most misleading
        entry in that list is your sentence in `WRITEUP.md`, not this script's.

    == (2) up close ==
        The numbers behind the one required figure and the two tables, so that everything
        shown here has printed output a reader can check it against. Write, to `figures/`:

            figures/part2_when.png          when the tags arrived: tag applications over
                                            time, with the movie's ratings over time behind
                                            them.

        The figure has labeled axes and a caption naming the question it answers. Claude
        may draw and label it; the sentence in `WRITEUP.md` about what it shows is yours.

        Then two tables, each printed under its own label:

            who added each tag              the movie's heaviest taggers, how many tag
                                            applications each made, and what share of the
                                            movie's applications that is.
            how the taggers rated it        for each of the movie's top tags, how the
                                            people who applied it rated the movie, beside
                                            how everyone else rated it.

        Claude prints the tables and says what the columns are. What they show is your two
        interesting details in `WRITEUP.md`, not this script's.

    == (3) my definition ==
        Your `score` over the whole set. Write it in this file as

            score(tags_df, ratings_df, movies_df) -> DataFrame[movieId, tag, score]

        one row per movie-tag pair, higher score meaning the tag describes the movie better.
        Print its top 15 rows for your chosen movie, and the number of rows and distinct
        movies it returned over the whole set. Families you could use, none of them
        preferred: distinct users who applied the tag; a rarity weight, the count times how
        few movies carry the tag; a damped version of either; something of your own. Whatever
        you choose, `WRITEUP.md` gets what you chose, what you rejected, and why.

    == (4) cleaning ==
        Whatever cleaning your `score()` does, and its size: how many raw tag strings went
        in, how many distinct tags came out, and the five mergers that absorbed the most
        applications. If you clean nothing, print that and say why in `WRITEUP.md`.
        Merging `Sci-Fi`, `sci-fi` and `scifi` is a decision, and so is not merging them.

    == (5) scores.csv ==
        `scores.csv` in the repo root, columns `movieId,tag,score`, holding a score for every
        movie and tag the judge will be asked about. That is two sets put together:

            every movie and tag in `judge/movies.csv`, which has one row per movie and a
            `tags` column of tags joined by `|`;
            plus, for each of the ten movies in your "My ten movies" slot, every tag from
            `judge/vocabulary.txt` that appears on it, matched after stripping and
            lowercasing, which is the same rule `judge/movies.csv` used.

        The second set matters because the judge adds your ten movies to its list, and
        `agreement.py` compares exactly what the two files share: a tag you never scored is
        dropped without a number. Print how many were asked for and how many you wrote.

    == (6) the four rankings ==
        For each of the ten movies in your "My ten movies" slot, four rankings of the same tags,
        printed one after another and never in one table:

            the counts: the ten most-used tags, by how many times each was applied;
            your own order, from the `WRITEUP.md` slot you filled before seeing any data;
            the judge's order, from `judge/ratings_movies.csv`;
            your `score()`'s order.

        Print each list under its own heading, best first. `results_viewer.py` builds the same
        four lists as a page you can read. Which tag is the artifact, and what the
        disagreements mean, is your paragraph in `WRITEUP.md`.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from load_data import REPO, load_all

MY_MOVIE = 8531   # White Chicks (2004), the student's claim for Part 2


def clean_tag(raw):
    """The student's rule for what counts as one tag: ignore case and ignore every space,
    so `Cross Dressing`, `cross  dressing ` and `crossdressing` are one tag."""
    return raw.str.lower().str.replace(r"\s+", "", regex=True)


def tag_labels(tags_df):
    """A readable name for each cleaned tag: its most-applied raw spelling (ties go to the
    alphabetically first). Display only; the key is what is counted."""
    counts = tags_df.assign(key=clean_tag(tags_df["tag"])).groupby(["key", "tag"]).size()
    counts = counts.reset_index(name="n").sort_values(["key", "n", "tag"], ascending=[True, False, True])
    return counts.drop_duplicates("key").set_index("key")["tag"]


def score(tags_df, ratings_df, movies_df):
    """The student's score(movie, tag): how many distinct users applied the tag to the movie,
    after cleaning. A user who applied it twice counts once."""
    cleaned = tags_df.assign(tag=clean_tag(tags_df["tag"]))
    return (cleaned.groupby(["movieId", "tag"])["userId"].nunique()
            .reset_index(name="score"))


def when_figure(by_year, title):
    """figures/part2_when.png: ratings per year above, tag applications per year below.

    Two panels on one shared time axis, since the two counts are on different scales."""
    fig, (top, bottom) = plt.subplots(2, 1, sharex=True, figsize=(9, 6))
    for ax, col, color in [(top, "ratings", "#eb6834"), (bottom, "tag applications", "#2a78d6")]:
        ax.bar(by_year.index, by_year[col], color=color, width=0.8)
        ax.set_ylabel(f"{col} per year")
        ax.set_title(f"{col.capitalize()} of {title}", loc="left", fontsize=10)
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", color="#e5e5e5", linewidth=0.8)
        ax.set_axisbelow(True)
        ax.yaxis.get_major_locator().set_params(integer=True)
    bottom.set_xlabel("calendar year of the rating or tag application")
    bottom.set_xticks(by_year.index)
    bottom.tick_params(axis="x", rotation=90)
    fig.suptitle(f"When did the ratings and the tags on {title} arrive?", fontsize=12)
    fig.tight_layout()
    out = REPO / "figures" / "part2_when.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"wrote {out.relative_to(REPO)}")


def part2_tags(ratings, tags, movies, links):
    print("== (1) the obvious answer ==")
    title = movies.set_index("movieId").loc[MY_MOVIE, "title"]
    mine = tags[tags["movieId"] == MY_MOVIE]
    print(f"{title}: {(ratings['movieId'] == MY_MOVIE).sum():,} ratings, {len(mine):,} tag applications")
    # Raw tag strings, exactly as typed: no lowercasing, no trimming.
    print(mine["tag"].value_counts().to_string())

    print("== (2) up close ==")
    rated = ratings[ratings["movieId"] == MY_MOVIE]
    years = lambda ts: pd.to_datetime(ts, unit="s").dt.year
    by_year = pd.DataFrame({
        "ratings": years(rated["timestamp"]).value_counts(),
        "tag applications": years(mine["timestamp"]).value_counts(),
    }).fillna(0).astype(int).sort_index()
    by_year = by_year.reindex(range(by_year.index.min(), by_year.index.max() + 1), fill_value=0)
    print("-- ratings and tag applications per calendar year --")
    print(by_year.to_string())
    when_figure(by_year, title)

    print("-- who added each tag --")
    who = mine.groupby("userId").agg(applications=("tag", "size"), distinct_tags=("tag", "nunique"))
    who["share of movie's applications"] = (who["applications"] / len(mine)).map("{:.1%}".format)
    print(f"{len(who)} users tagged this movie; every one of them, most applications first")
    print(who.sort_values("applications", ascending=False).to_string())

    print("-- how the taggers rated it --")
    top10 = mine["tag"].value_counts().head(10).index
    stars = rated.set_index("userId")["rating"]
    rows = []
    for tag in top10:
        appliers = mine.loc[mine["tag"] == tag, "userId"].unique()
        theirs = stars[stars.index.isin(appliers)]
        rest = stars[~stars.index.isin(appliers)]
        rows.append({"tag": tag, "appliers": len(appliers), "appliers who rated it": len(theirs),
                     "their mean rating": theirs.mean(), "everyone else, n": len(rest),
                     "everyone else, mean": rest.mean()})
    print("raw tag strings; the ten most-applied, most applied first")
    print(pd.DataFrame(rows).set_index("tag").round(2).to_string())

    print("== (3) my definition ==")
    scores = score(tags, ratings, movies)
    labels = tag_labels(tags)
    top = scores[scores["movieId"] == MY_MOVIE].sort_values(["score", "tag"], ascending=[False, True]).head(15)
    top = top.assign(label=top["tag"].map(labels))
    print(f"top 15 for {title} (tag is the cleaned key, label its most-applied raw spelling)")
    print(top[["tag", "label", "score"]].to_string(index=False))
    print(f"{len(scores):,} movie-tag rows over {scores['movieId'].nunique():,} movies")

    print("== (4) cleaning ==")
    key = clean_tag(tags["tag"])
    print(f"{tags['tag'].nunique():,} raw tag strings in, {key.nunique():,} distinct tags out")
    groups = tags.assign(key=key).groupby("key").agg(
        raw_spellings=("tag", "nunique"), applications=("tag", "size"))
    merged = groups[groups["raw_spellings"] > 1].sort_values("applications", ascending=False).head(5)
    print("-- the five mergers that absorbed the most applications --")
    for k, row in merged.iterrows():
        spellings = tags.loc[key == k, "tag"].value_counts()
        print(f"{k}: {row['applications']:,} applications from {row['raw_spellings']} raw spellings, "
              f"e.g. " + ", ".join(repr(s) for s in spellings.index[:4]))

    print("== (5) scores.csv ==")

    print("== (6) the four rankings ==")


if __name__ == "__main__":
    ratings, tags, movies, links = load_all()
    part2_tags(ratings, tags, movies, links)
