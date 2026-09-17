"""
How well three ways of ranking a movie's tags agree with your judge, from
`uv run python agreement.py`: your `score()`, popularity (how many times each tag was
applied) and your own order from `WRITEUP.md`, which covers your ten movies only. For each
movie it takes that method's top five tags among the ones the judge rated and counts how
many of the five the judge rated 4 or 5, then averages that over every movie the judge rated.
The three do not draw their five from the same number of tags, so the count of tags
compared is printed beside each number. It writes `agreement.csv` and never
says whether a number is good. There is no `--users` version: your Part 3 score file is
your own design, so pairing it with `judge/ratings_users.csv` is yours to specify too.
"""
import re, sys
from pathlib import Path
import pandas as pd

REPO = Path(__file__).resolve().parent
SCORES, RATED = REPO / "scores.csv", REPO / "judge" / "ratings_movies.csv"
WRITEUP = REPO / "WRITEUP.md"
# A movieId before the colon, then the tags best first: "296: nonlinear, hit men" and
# "Pulp Fiction (296): nonlinear, hit men" both work.
MY_LINE = re.compile(r"^[^:]*?(\d{1,7})\s*\)?\s*:\s*(.+)$")
# What the "My own order" slot has to look like, said once and reused by everything that
# reads it. `results_viewer.py` imports `my_order_lines` rather than parsing the slot a
# second way: two parsers for one slot is two answers for one question.
ORDER_FORMAT = ('The "My own order" slot in WRITEUP.md is read one movie to a line, with no '
                'bullets and no numbering: the movieId, then a colon, then the ten tags best '
                'first, as in "296: nonlinear, hit men, dark comedy".')

def my_order_lines(writeup: Path = None) -> dict[int, list[str]]:
    """movieId -> your tags in the order you wrote them, from the "My own order" slot.

    The one parser for that slot. Tags come back stripped and lowercased, which is the form
    the judge's file and `scores.csv` use, so the three can be compared without a second
    cleaning step."""
    path = Path(writeup or WRITEUP)
    if not path.exists():
        return {}
    slot = path.read_text(encoding="utf-8").split("**My own order")[-1]
    out: dict[int, list[str]] = {}
    for line in slot.split("\n**")[0].splitlines():
        if "**" in line:      # the tail of the label itself, or a bolded answer; never a line
            continue          # of tags, and "...from step 4:**" parses as movie 4 otherwise
        found = MY_LINE.match(line)
        if found:
            tags = [t.strip().lower() for t in found.group(2).split(",") if t.strip()]
            if tags:
                out[int(found.group(1))] = tags
    return out

def my_order() -> pd.DataFrame:
    """Your own order as a score, from the "My own order" slot: first tag, highest score."""
    rows = [{"id": movie, "tag": t, "score": float(len(tags) - place)}
            for movie, tags in my_order_lines().items()
            for place, t in enumerate(tags)]
    return pd.DataFrame(rows, columns=["id", "tag", "score"])

def top_five(method: str, scores: pd.DataFrame, rated: pd.DataFrame) -> pd.DataFrame:
    """One row per movie: of this method's top five tags among the ones the judge rated, how
    many the judge rated 4 or 5. Ties break alphabetically, so the five are reproducible."""
    rows = []
    for movie, group in rated.merge(scores, on=["id", "tag"]).groupby("id", sort=True):
        five = group.sort_values(["score", "tag"], ascending=[False, True]).head(5)
        rows.append({"method": method, "id": movie, "tags_rated": len(group),
                     "top_five_4_or_5": int((five.rating >= 4).sum())})
    return pd.DataFrame(rows)

def main() -> None:
    if not (SCORES.exists() and RATED.exists()):
        sys.exit("scores.csv or judge/ratings_movies.csv is missing; Part 2 writes one "
                 "and the judge writes the other.")
    rated = pd.read_csv(RATED, keep_default_na=False)
    raw = pd.read_csv(REPO / "data" / "tags.csv.gz", keep_default_na=False)
    raw = raw.assign(tag=raw["tag"].str.strip().str.lower())
    mine = my_order()
    if mine.empty:
        print("No movie lines were found in the \"My own order\" slot of WRITEUP.md, so your "
              "own order is not compared below.\n" + ORDER_FORMAT + "\n")
    methods = {"score()": pd.read_csv(SCORES, keep_default_na=False),
               "popularity": raw.groupby(["movieId", "tag"]).size().rename("score").reset_index(),
               "your own order": mine}
    table = pd.concat([top_five(n, s.rename(columns={"movieId": "id"}), rated)
                       for n, s in methods.items() if len(s)], ignore_index=True)
    table.to_csv(REPO / "agreement.csv", index=False)
    print("Of a method's top five tags on a movie, how many the judge rated 4 or 5, "
          "averaged\nover every movie the judge rated.\n")
    for name in methods:
        part = table[table["method"] == name]
        print(f"  {name:<16} {part['top_five_4_or_5'].mean():.2f} of 5, over {len(part)} "
              f"movies, {part['tags_rated'].median():.0f} tags compared on the middle one"
              if len(part) else f"  {name:<16} nothing to compare")
    print("\nwrote agreement.csv: one row per movie and method.")

if __name__ == "__main__":
    main()
