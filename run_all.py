"""
Run your whole pipeline, start to finish, and say what is still missing.

    uv run python run_all.py

Reads the data once, prints the counts, runs Parts 1 to 3, then checks five things and
prints a report:

  * the figure files each part's docstring promised, and whether they are in `figures/`;
  * the labeled slots in `WRITEUP.md` still holding `XXXX`, listed under the part they sit in;
  * the files a reached part should have produced: Part 2's `scores.csv` and
    `judge/ratings_movies.csv` and `agreement.csv`, Part 3's `judge/users.csv`,
    `judge/ratings_users.csv` and `user_results.py`;
  * whether either judge criterion is still the paragraph the template shipped, which is a
    file you have to write;
  * presence and form only; nothing here says whether an answer is right.

A part counts as reached once you have deleted the "unimplemented" line from its script.
Parts you have not reached are listed as "not started" and are never counted against you, so
this is safe to run from the first day. The exit code is 0 when nothing in a reached part is
missing, and 1 otherwise: that is the submission gate, and it checks presence and form only.
"""

from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
from pathlib import Path

from load_data import counts_line, load_all
from part1_data import part1_data
from part2_tags import part2_tags
from part3_users import part3_users

REPO = Path(__file__).resolve().parent
WRITEUP = REPO / "WRITEUP.md"
FIGURES = REPO / "figures"

# The line every unstarted part script still carries.
SENTINEL = "# delete this line when you start"

# part number -> (script, the figure files that part's docstring promises)
PART_FILES = {
    1: ("part1_data.py", []),
    2: ("part2_tags.py", ["part2_when.png"]),
    3: ("part3_users.py", []),
}

# Other files a reached part is expected to have produced.
PART_OUTPUTS = {
    2: ["scores.csv", "judge/ratings_movies.csv", "agreement.csv"],
    3: ["judge/users.csv", "judge/ratings_users.csv", "user_results.py"],
}

# The two criterion files, and the part each one belongs to. Both are yours to write, and a
# file still holding the template's paragraph is the commonest way to reach the end of a part
# with nothing of your own in it.
CRITERIA = {2: "judge/criterion.md", 3: "judge/criterion_users.md"}

# Slots above the first "## Part" heading (your name and the date).
FRONT = "front matter"

HEADING_RE = re.compile(r"^##\s+(?P<heading>.+?)\s*$")
PART_HEADING_RE = re.compile(r"^Part\s+(?P<n>\d+)\b")


def started(part: int) -> bool:
    """A part is reached once its script no longer carries the "unimplemented" line."""
    text = (REPO / PART_FILES[part][0]).read_text(encoding="utf-8")
    return SENTINEL not in text


def shipped_criteria() -> dict[str, str]:
    """Each criterion file as the template shipped it, read out of `judge/judge.py` so that
    the two can never drift apart. `{}` if that file cannot be read."""
    try:
        spec = importlib.util.spec_from_file_location("_judge", REPO / "judge" / "judge.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return dict(module.SHIPPED)
    except Exception:
        return {}


def still_shipped(name: str) -> bool:
    """Is this criterion file still the paragraph the template shipped?"""
    path = REPO / name
    shipped = shipped_criteria().get(Path(name).name)
    if not (path.exists() and shipped):
        return False
    return " ".join(path.read_text(encoding="utf-8").split()).lower() \
        == " ".join(shipped.split()).lower()


def commits() -> str:
    """The commit subjects, or "" if this is not a git repo. Used only for Part 0."""
    r = subprocess.run(["git", "log", "--format=%s"], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def label_span(lines: list[str], i: int) -> tuple[int, str, str] | None:
    """lines[i] opens a bold label. Returns (last line, label text, the rest of that line).

    Every shape this writeup uses, and they all have to be seen or the slot is invisible:

        **Label:** XXXX                        the answer on the label's own line
        **Label:**                             the answer a line or two below
        <blank>
        XXXX
        **Label** (an aside)**:** XXXX         a parenthetical between two bold runs
        **Label ending in a question?** XXXX   a question needs no colon
        **A label too long for one            a label wrapped over two lines
        line, ending here:** XXXX

    A bold run followed by ordinary prose is a heading or an instruction, not a slot, so a
    label counts only when nothing follows its closing `**` or the text before that `**` ends
    in a colon or a question mark.

    Closing markers are tried left to right, and the first one that passes that test wins. The
    rightmost marker looks equivalent on an unfilled writeup, where every answer is `XXXX`, and
    is wrong on a filled one: in

        **Disagreement 1:** the judge put **491 of 7,017 pairs** at 4 or 5

    the rightmost marker closes `pairs`, and the label swallows the answer. Once you bold
    anything inside an answer, that mistake can run a label past the next real one and hide a
    blank slot from this check."""
    j = i
    while j < len(lines) and j - i < 4:
        start = 2 if j == i else 0
        close = lines[j].find("**", start)
        while close >= 0:
            after = lines[j][close + 2:]
            before = lines[j][:close].rstrip()
            if not after.strip() or before.endswith((":", "?")):
                label = ("\n".join(lines[i:j]) + "\n" + lines[j][:close + 2]).replace("**", " ")
                return j, " ".join(label.split()).rstrip(": "), after
            close = lines[j].find("**", close + 2)
        j += 1
    return None


def blank_slots() -> dict[str, list[str]]:
    """Every labeled slot in WRITEUP.md still holding XXXX, grouped by the section it is in."""
    if not WRITEUP.exists():
        return {}
    section = FRONT
    out: dict[str, list[str]] = {}
    lines = WRITEUP.read_text(encoding="utf-8").splitlines()
    i = 0
    while i < len(lines):
        heading = HEADING_RE.match(lines[i])
        if heading:
            section = heading.group("heading")
            i += 1
            continue
        span = lines[i].startswith("**") and label_span(lines, i)
        if not span:
            i += 1
            continue
        end, label, rest = span
        if rest.strip():
            blank = rest.strip() == "XXXX"
        else:
            blank = False                  # look past blank lines for the answer
            for follow in lines[end + 1:]:
                if not follow.strip():
                    continue
                blank = follow.strip() == "XXXX"
                break
        if blank:
            out.setdefault(section, []).append(label)
        i = end + 1
    return out


def all_labels() -> list[str]:
    """Every labeled slot, filled or not. Used to check this parser against the writeup."""
    lines = WRITEUP.read_text(encoding="utf-8").splitlines() if WRITEUP.exists() else []
    out, i = [], 0
    while i < len(lines):
        span = lines[i].startswith("**") and label_span(lines, i)
        if not span:
            i += 1
            continue
        out.append(span[1])
        i = span[0] + 1
    return out


def section_part(section: str, carried: int | None) -> int | None:
    """Which part a WRITEUP.md section belongs to.

    A numbered heading says so. An unnumbered one in the middle of the writeup, such as
    "Predictions revisited", belongs to the part whose heading it sits under. None means the
    name and date at the top, which are always checked."""
    if section == FRONT:
        return None
    m = PART_HEADING_RE.match(section)
    if m:
        return int(m.group("n"))
    if section.lower().startswith("working with claude"):
        return 4
    return carried


def report(reached: set[int]) -> int:
    """Print the report. Returns the number of things missing in a reached part."""
    missing = 0
    log = commits()

    print()
    print("== what is missing ==")

    if "Name and date" not in log:
        print("  setup: no `Name and date` commit yet. Run the `setup` skill.")
        missing += 1
    if "Part 0 predictions" not in log:
        print("  part 0: no `Part 0 predictions` commit yet. Nothing else runs before it.")
        missing += 1

    for part in sorted(PART_FILES):
        script, figures = PART_FILES[part]
        if part not in reached:
            print(f"  part {part}: not started ({script}).")
            continue
        for name in figures:
            if not (FIGURES / name).exists():
                print(f"  part {part}: figures/{name} is missing.")
                missing += 1
        for name in PART_OUTPUTS.get(part, []):
            if not (REPO / name).exists():
                print(f"  part {part}: {name} is missing.")
                missing += 1
        name = CRITERIA.get(part)
        if name and not (REPO / name).exists():
            print(f"  part {part}: {name} is missing; it is yours to write.")
            missing += 1
        elif name and still_shipped(name):
            print(f"  part {part}: {name} is still the paragraph the template shipped; "
                  f"it is yours to write.")
            missing += 1

    if not WRITEUP.exists():
        print("  WRITEUP.md is missing.")
        missing += 1
    carried = None
    for section, labels in blank_slots().items():
        part = section_part(section, carried)
        if part is not None:
            carried = part
        counted = part is None or part == 0 or part in reached
        numbered = part is not None and PART_HEADING_RE.match(section)
        where = f"part {part}" if numbered else section
        if not counted:
            plural = "slot" if len(labels) == 1 else "slots"
            print(f"  {where}: not started, {len(labels)} {plural} still XXXX.")
            continue
        for label in labels:
            print(f"  {where}: {label} is still XXXX.")
        missing += len(labels)

    if not missing:
        print("  nothing in a part you have reached.")
    print()
    print(f"{missing} missing in the parts you have reached.")
    return missing


def main() -> int:
    ratings, tags, movies, links = load_all()
    print(counts_line(ratings, tags, movies))

    part1_data(ratings, tags, movies, links)
    part2_tags(ratings, tags, movies, links)
    part3_users(ratings, tags, movies, links)

    reached = {p for p in PART_FILES if started(p)}
    if 3 in reached:
        reached.add(4)   # "Working with Claude" is written once the parts are done
    return 1 if report(reached) else 0


if __name__ == "__main__":
    sys.exit(main())
