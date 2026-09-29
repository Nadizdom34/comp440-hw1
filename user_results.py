"""User viewer, Part 3.

Builds one self-contained HTML page, `user_results.html`, from your score(user, tag) in
`part3_users.py`. First a table of your own top ten tags, then the same for nine other users
picked at random with a fixed seed, so the same nine come back every run.

For each user and each of their top ten tags, a dropdown shows where the tag came from:
- a user on the own-tags path (5 or more distinct tags of their own): each time they applied
  the tag, with the movie and the date;
- a user on the ratings path: each movie they rated 3 or higher that has the tag in its top 5,
  with their rating and the date they rated it. Your own dates are the newest date in the
  data, because that is the timestamp `add_me` gives your ratings.

    uv run python user_results.py        # writes user_results.html
"""
import datetime
import html

import numpy as np
import pandas as pd

from load_data import REPO, load_all
from part2_tags import clean_tag, tag_labels
from part3_users import KEEP_AT, ME, OWN_MIN, add_me, read_my_ratings, score, top_n

SEED = 440     # which nine other users are shown: any fixed number, so a rerun shows the same
OTHERS = 9     # how many users besides you
TOP = 10       # how many tags per user
OUT = REPO / "user_results.html"
CSS = """body { font-family: Helvetica, Arial, sans-serif; margin: 20px; }
table { border-collapse: collapse; margin-bottom: 12px; }
th, td { border: 1px solid #999999; padding: 4px 8px; text-align: left; vertical-align: top; }"""


def as_date(stamp):
    return datetime.datetime.fromtimestamp(int(stamp), datetime.UTC).strftime("%Y-%m-%d")


def table_html(headers, rows):
    head = "".join("<th>%s</th>" % html.escape(h) for h in headers)
    body = "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % html.escape(str(c)) for c in row)
                   for row in rows)
    return "<table><tr>%s</tr>%s</table>" % (head, body)


def build():
    ratings, tags, movies, _ = load_all()
    ratings = add_me(ratings, read_my_ratings()[0])
    scores = score(ratings, tags, movies)
    labels = tag_labels(tags)
    titles = movies.set_index("movieId")["title"]

    cleaned = tags.assign(tag=clean_tag(tags["tag"]))
    distinct = cleaned.groupby("userId")["tag"].nunique()
    taggers = set(distinct[distinct >= OWN_MIN].index)
    movie_top = top_n(cleaned, "movieId")

    others = sorted(set(ratings["userId"]) - {ME})
    picked = sorted(np.random.default_rng(SEED).choice(others, OTHERS, replace=False).tolist())

    users = []
    for user in [ME] + picked:
        mine = scores[scores["userId"] == user].sort_values(["score", "tag"], ascending=[False, True])
        rated = ratings[ratings["userId"] == user]
        own_path = user in taggers
        rows = []
        for tag, value in zip(mine["tag"].head(TOP), mine["score"].head(TOP)):
            if own_path:
                apps = cleaned[(cleaned["userId"] == user) & (cleaned["tag"] == tag)]
                evidence = (["Movie", "Date tagged"],
                            [(titles.get(m, m), as_date(t)) for m, t in zip(apps["movieId"], apps["timestamp"])])
            else:
                has = set(movie_top.loc[movie_top["tag"] == tag, "movieId"])
                kept = rated[(rated["rating"] >= KEEP_AT) & rated["movieId"].isin(has)]
                evidence = (["Movie", "Their rating", "Date rated"],
                            [(titles.get(m, m), r, as_date(t))
                             for m, r, t in zip(kept["movieId"], kept["rating"], kept["timestamp"])])
            rows.append((tag, labels.get(tag, tag), value, evidence))
        users.append({"id": user, "path": "own tags" if own_path else "ratings",
                      "ratings": len(rated), "tags": int(distinct.get(user, 0)), "rows": rows})
    return users


def user_html(user, heading):
    body = ["<h2>%s</h2>" % html.escape(heading),
            "<p>%d ratings, %d distinct tags of their own; scored on the %s path.</p>"
            % (user["ratings"], user["tags"], user["path"])]
    if not user["rows"]:
        return "\n".join(body + ["<p>no scored tags</p>"])
    rows = "".join(
        "<tr><td>%d</td><td>%s</td><td>%g</td><td><details><summary>show (%d)</summary>%s"
        "</details></td></tr>" % (i, html.escape(label), value, len(ev[1]), table_html(*ev))
        for i, (tag, label, value, ev) in enumerate(user["rows"], 1))
    body.append("<table><tr><th>Rank</th><th>Tag</th><th>Score</th><th>Where it came from</th>"
                "</tr>%s</table>" % rows)
    return "\n".join(body)


def main():
    users = build()
    body = ["<h1>User viewer</h1>",
            "<p>Top %d tags per user by score(user, tag), ties alphabetical for display. "
            "The %d other users are picked at random with seed %d.</p>" % (TOP, OTHERS, SEED),
            user_html(users[0], "My top tags (userId %d)" % ME)]
    body += [user_html(u, "User %d" % u["id"]) for u in users[1:]]
    OUT.write_text('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
                   '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
                   "<title>User Viewer</title>\n<style>\n%s\n</style>\n</head>\n<body>\n%s\n"
                   "</body>\n</html>\n" % (CSS, "\n".join(body)), encoding="utf-8")
    print("wrote", OUT, "for users", ", ".join(str(u["id"]) for u in users))


if __name__ == "__main__":
    main()
