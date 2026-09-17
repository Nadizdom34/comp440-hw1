# The data for HW1

Six files ship here. You do not download anything, and you do not edit
anything in this directory.

| file | what it is | rows |
| --- | --- | --- |
| `ratings.csv.gz` | one row per rating: `userId,movieId,rating,timestamp` | 5,000,030 |
| `tags.csv.gz` | one row per tag application: `userId,movieId,tag,timestamp` | 1,244,210 |
| `movies.csv` | one row per movie: `movieId,title,genres` | 4,000 |
| `links.csv` | one row per movie: `movieId,imdbId,tmdbId` | 4,000 |
| `LICENSE.txt` | the MovieLens 32M README, including its usage license and citation | — |
| `make_compact.py` | the script that built the four data files above. Part 1 asks you to read it | — |

Read them with `load_data.py`, which handles the gzip transparently and sets
the two pandas options these files need. Two of those details are real traps,
and Part 1 asks you to verify them:

- Seventeen tag strings in the full dataset are the literal text `NA` or
  `null`. Under pandas' defaults those become missing values, so the loader
  passes `keep_default_na=False`.
- `imdbId` in `links.csv` has significant leading zeros, so the loader reads
  the `links.csv` columns as strings, not integers.

The files use CRLF line endings and UTF-8 encoding, exactly as MovieLens
distributes them.

## Where this came from

This is a compact subset of **MovieLens 32M**, built by `data/make_compact.py`,
which ships in this directory. The build is deterministic: the same source and
the same flags reproduce these files byte for byte. **Random seed: 440.**

Part 1 asks you to read that script, not to run it. Running it reads the full
MovieLens 32M download, about 250 MB unzipped, which this repo does not
include; the only thing that asks for a rerun is one of the extra credits. The
six steps below are what the script does.

The rule, in the order it is applied:

1. Keep the **top 4,000 movies** by rating count in the full `ratings.csv`,
   ties broken by `movieId` ascending. Counted over all 32M ratings, the
   most-rated of them has 102,929 and the least-rated has 1,188.

   Those two numbers describe the full data set, before step 4 sampled the
   users. In the file this directory ships, which holds only the sampled
   users' ratings, every count is smaller: the most-rated movie has 14,777
   ratings and the least-rated has **83**. If you are checking a number
   against `ratings.csv.gz`, 83 is the one you will find.
2. Keep only ratings on those movies.
3. A user is **eligible** if they have at least **20** ratings on those
   movies.
4. Include every eligible user who applied at least one tag to one of those
   movies, then add a uniform random sample of the remaining eligible users
   so that the kept rating count lands as close as possible to 5,000,000
   without exceeding 5,500,000. In this build all 14,019 eligible taggers
   were included, plus a random sample of 9,424 non-tagging eligible users.
5. Keep `tags.csv` rows whose movie is among the kept movies and whose user
   is included.
6. Keep `movies.csv` and `links.csv` rows for the kept movies only.

The file names, columns and header lines are the originals', so code you
write here runs unchanged on the full 32M dataset.

## What the cut did

| measurement | full ML-32M | this subset |
| --- | --- | --- |
| ratings | 32,000,204 | 5,000,030 |
| users | 200,948 | 23,443 |
| movies with ratings | 84,432 | 4,000 |
| tag applications | 2,000,072 | 1,244,210 |
| tagging users | 15,848 | 14,019 |
| movies with at least one tag | 51,323 | 3,999 |
| ratings per user, median | 73 | 103 |
| ratings per movie, median | 5 | 685 |
| density (ratings / users x movies) | 0.19% | 5.33% |

Keeping 62.2% of all tag applications and 88.5% of all taggers, in a subset
28 times denser than the full dataset. That density is what makes one movie's
tag list and one user's history short enough to read by hand.

Exactly one kept movie carries no tags at all: *Widows' Peak (1994)*,
movieId 452.

## License and citation

This subset is a transformation of MovieLens 32M and carries the same
license, which is in `LICENSE.txt`. From that file:

> The user may redistribute the data set, including transformations, so long
> as it is distributed under these same license conditions.

The license also forbids commercial use without permission from a GroupLens
faculty member, forbids any attempt to identify users, and requires that use
be acknowledged by citing:

> F. Maxwell Harper and Joseph A. Konstan. 2015. The MovieLens Datasets:
> History and Context. *ACM Transactions on Interactive Intelligent Systems
> (TiiS)* 5, 4: 19:1-19:19. <https://doi.org/10.1145/2827872>
