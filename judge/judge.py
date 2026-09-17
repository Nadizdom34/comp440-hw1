"""
The judge: two prompts and a loop. Do not edit it; `--force` rates again over an old file.

    uv run python judge/judge.py judge/movies.csv   ->  judge/ratings_movies.csv
    uv run python judge/judge.py judge/users.csv    ->  judge/ratings_users.csv

`judge/system.md` says how to answer and is the same for everyone. The other prompt is your
criterion, a blank line, one item, then the tags to rate. Claude sees that pair once per
item, five at a time.

**Which criterion is read is decided by the name of the items file.** A file named
`users.csv` is rated against `judge/criterion_users.md`, your paragraph about people. A file
named anything else is rated against `judge/criterion.md`, your paragraph about movies. So
Part 3's file has to be called `judge/users.csv`. The run says which criterion it read
before it asks for anything.
"""
import argparse, json, os, re, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import pandas as pd

JUDGE, REPO = Path(__file__).resolve().parent, Path(__file__).resolve().parents[1]
MODEL, WORKERS = "claude-sonnet-5", 5   # everyone's judge; how many sessions run at once
# One session per item: no tools, no settings, no memory of this repo. That is what makes
# the judge's answer worth comparing yours against.
CLAUDE = ["claude", "-p", "--setting-sources", "", "--tools", "", "--output-format", "json",
          "--no-session-persistence"]   # a judge session is not part of your record
# A child that inherits these three reports itself as the session that started this script.
DROP = ("CLAUDECODE", "CLAUDE_CODE_SESSION_ID", "CLAUDE_CODE_ENTRYPOINT")
# Each criterion file exactly as the template ships it. While a file still says this, it is
# not yours and nothing runs. The whole text is compared, not just its opening: "A tag best
# describes a movie when it tells you" is a natural way for a student to start their own
# paragraph, and an opening-words test refuses it.
SHIPPED = {
    "criterion.md": """A tag best describes a movie when it tells you something true and particular about the movie
itself. The test is two-sided: someone who has seen the movie should recognise it from the
tag, and someone who has not should learn something real about it from the tag. A tag that
fits a thousand other movies equally well describes this one poorly, even when it is accurate.
Opinions about quality are not descriptions, so "overrated", "boring" and "masterpiece" rate
low however strongly they are meant. Neither is a note somebody left for themselves, so "to
watch", "seen it", "own it on dvd" and "netflix queue" rate low. Rate a tag 5 when it is one
of the first things you would say about the movie, 3 when it is true but would not make your
short list, and 1 when it is wrong, empty, or about the person who wrote it rather than the
film.""",
    "criterion_users.md": """A tag best describes a person when it tells you — and the rest of this file is a placeholder.
Replace all of it with your own paragraph about what makes a tag describe a person's taste.
It is yours, it is graded, and the movie paragraph in `judge/criterion.md` will not do: that
one is about films, and it rates tags on people badly.""",
}


def is_shipped(text: str, shipped: str) -> bool:
    """Is this file still the one the template shipped? Whitespace and case are ignored, so
    a reflowed or re-wrapped copy of the shipped paragraph is still the shipped paragraph."""
    return " ".join(text.split()).lower() == " ".join(shipped.split()).lower()

def my_movies() -> list[dict]:
    """Your ten movies, described as `judge/movies.csv` describes its hundred: ids from its
    `WRITEUP.md` slot, and each one's vocabulary tags in alphabetical order."""
    slot = (REPO / "WRITEUP.md").read_text(encoding="utf-8").split("**My ten movies")[-1]
    mine = [int(n) for n in re.findall(r"^\s*(\d+)", slot.split("\n**")[0], re.M)]
    if not mine:
        print('No movieIds found in the "My ten movies" slot of WRITEUP.md, so only the '
              "movies in the items file are being rated. That slot is read one movie to a "
              "line, the movieId first, with no bullets and no numbering: `296, Pulp "
              "Fiction (1994)`.")
        return []
    words = {t.strip() for t in (JUDGE / "vocabulary.txt").read_text().splitlines()}
    raw = pd.read_csv(REPO / "data" / "tags.csv.gz", keep_default_na=False)
    on_it = (raw.assign(tag=raw["tag"].str.strip().str.lower())
             .query("movieId in @mine and tag in @words")
             .groupby("movieId")["tag"].apply(lambda s: "|".join(sorted(set(s)))))
    films = pd.read_csv(REPO / "data" / "movies.csv", keep_default_na=False).set_index("movieId")
    said = films["title"] + ", " + films["genres"].str.replace("|", ", ", regex=False)
    return [{"id": i, "description": said[i], "tags": on_it[i]}
            for i in mine if i in on_it.index and i in said.index]

def judge_item(item: dict, system: str, criterion: str, model: str) -> dict:
    """Rate one item, and ask a second time if fewer tags came back than were sent. A
    session can stop half way down its list and still exit as though it had finished."""
    tags = [t for t in str(item["tags"]).split("|") if t]
    user = criterion + "\n\n" + str(item["description"]) + "\n" + "\n".join(tags)
    env = {k: v for k, v in os.environ.items() if k not in DROP}
    ratings, cost = {}, 0.0
    for attempt in (1, 2):
        done = subprocess.run(CLAUDE + ["--model", model, "--system-prompt", system],
                              input=user, capture_output=True, text=True, env=env)
        reply = json.loads(done.stdout) if done.stdout.startswith("{") else {}
        cost += float(reply.get("total_cost_usd") or 0.0)
        for line in [x.strip() for x in (reply.get("result") or "").splitlines()]:
            # A tag can itself contain a comma, so a line splits at its LAST comma.
            tag, _, rating = line.rpartition(",")
            if tag.strip() and rating.strip().isdigit() and 1 <= int(rating) <= 5:
                ratings.setdefault(tag.strip(), int(rating))  # a first answer wins
        if len(ratings) >= len(tags):
            break
    return {"id": item["id"], "ratings": ratings, "cost": cost,
            "short": len(ratings) < len(tags)}

def main() -> None:
    parser = argparse.ArgumentParser(description="Rate every tag on every item in a file.")
    parser.add_argument("items", help="judge/movies.csv, or the judge/users.csv you wrote")
    parser.add_argument("--force", action="store_true", help="rate again over the last run")
    parser.add_argument("--model", default=MODEL, help=f"default {MODEL}")
    args = parser.parse_args()
    items_file = Path(args.items)
    if not items_file.exists():
        sys.exit(f"{args.items} is not here. Part 2 rates judge/movies.csv; Part 3 rates the "
                 f"judge/users.csv you write.")
    out = JUDGE / f"ratings_{items_file.stem}.csv"
    if out.exists() and not args.force:
        sys.exit(f"judge/{out.name} is here already. Pass --force to rate again.")
    # The items file's NAME picks the criterion, and the line printed below says which one it
    # picked, so a file under some other name is never rated against the movie paragraph
    # without saying so.
    name = "criterion_users.md" if items_file.name == "users.csv" else "criterion.md"
    if not (JUDGE / name).exists(): sys.exit(f"judge/{name} is not here; write it first.")
    criterion = (JUDGE / name).read_text(encoding="utf-8").strip()
    if is_shipped(criterion, SHIPPED[name]):
        sys.exit(f"judge/{name} is still the one the template shipped; write your own.")
    system = (JUDGE / "system.md").read_text(encoding="utf-8")
    items = pd.read_csv(items_file, keep_default_na=False).to_dict("records")
    if items_file.name == "movies.csv":         # the hundred, plus your ten if not in them
        items += [m for m in my_movies() if m["id"] not in {i["id"] for i in items}]
    if not items:
        sys.exit(f"{args.items} has no rows, so there is nothing to rate.")
    asked = sum(len([t for t in str(i["tags"]).split("|") if t]) for i in items)
    print(f"{items_file.name} is rated against judge/{name}.")
    print(f"{len(items)} items, {asked:,} tag ratings, on {args.model}, {WORKERS} at a time.")
    began = time.time()
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        rated = list(pool.map(lambda i: judge_item(i, system, criterion, args.model), items))
    rows = [{"id": a["id"], "tag": t, "rating": r}
            for a in rated for t, r in sorted(a["ratings"].items())]
    if not rows: sys.exit("nothing came back, so no ratings file was written.")
    pd.DataFrame(rows).to_csv(out, index=False)
    report = (f"{len(rated)} items rated on {args.model}, {len(rows):,} tag ratings; "
              f"{sum(1 for a in rated if a['short'])} came back short."
              f"\n${sum(a['cost'] for a in rated):.2f}, {round(time.time()-began)} seconds.")
    print(report)
    out.with_suffix(".log").write_text(report + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()
