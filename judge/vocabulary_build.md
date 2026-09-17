# How `vocabulary.txt` was built

The vocabulary is the fixed candidate list the judge scores against, and the
same list every student uses. It is built from the compact set's own tag
applications, with seed 440, by `judge/build_inputs.py` in the
instructor's repository.

## The rule

1. **Clean every tag application**: lowercase it and strip surrounding
   whitespace. That is the only cleaning applied. Nothing is stemmed, no
   plurals are merged, no synonyms are collapsed. Deciding whether to merge
   `sci-fi` and `science fiction` is the student's decision in Part 2, not
   the vocabulary's.
2. **Drop cleaned tags that are** purely numeric (digits, optionally with one
   decimal separator), one character or shorter, or longer than 60
   characters.
3. **Rank what remains by the number of distinct users who applied it**, not
   by the number of applications. This is deliberate: one account supplied a
   third of all tag applications in MovieLens 32M, so an
   application-weighted ranking would largely describe that one account.
4. **Keep the top 300.** Ties are broken by tag text ascending,
   so the list is reproducible.

## What that produced

| measurement | value |
| --- | --- |
| tag applications in the compact set | 1,244,210 |
| distinct raw tag strings | 86,088 |
| distinct tag strings after cleaning | 80,800 |
| cleaned tags dropped by rule 2 | 262 |
| cleaned tags eligible for ranking | 80,538 |
| vocabulary size | 300 |
| distinct-user count of the last tag kept | 311 |
| tag applications the vocabulary covers | 481,074 of 1,244,210 (38.7%) |

Dropped by reason:

| reason | cleaned tags dropped |
| --- | --- |
| one character or empty | 23 |
| over 60 characters | 169 |
| purely numeric | 70 |

## The top 30

Ranked by distinct users, which is the ranking that built the list. The
application counts are shown beside them only to make the difference between
the two rankings visible; the judge never sees either number.

| rank | tag | distinct users | applications |
| --- | --- | --- | --- |
| 1 | `sci-fi` | 2,628 | 10,491 |
| 2 | `atmospheric` | 2,109 | 9,039 |
| 3 | `visually appealing` | 2,010 | 6,737 |
| 4 | `twist ending` | 1,995 | 6,040 |
| 5 | `thought-provoking` | 1,957 | 5,593 |
| 6 | `surreal` | 1,944 | 6,306 |
| 7 | `funny` | 1,876 | 6,874 |
| 8 | `comedy` | 1,859 | 7,366 |
| 9 | `action` | 1,846 | 8,214 |
| 10 | `dark comedy` | 1,825 | 5,200 |
| 11 | `psychology` | 1,595 | 4,478 |
| 12 | `dystopia` | 1,521 | 5,154 |
| 13 | `classic` | 1,501 | 4,525 |
| 14 | `great soundtrack` | 1,464 | 3,683 |
| 15 | `social commentary` | 1,438 | 4,423 |
| 16 | `cinematography` | 1,423 | 4,609 |
| 17 | `dark` | 1,423 | 4,344 |
| 18 | `fantasy` | 1,407 | 4,552 |
| 19 | `time travel` | 1,398 | 3,730 |
| 20 | `quirky` | 1,384 | 4,463 |
| 21 | `psychological` | 1,370 | 3,613 |
| 22 | `thriller` | 1,335 | 4,101 |
| 23 | `mindfuck` | 1,333 | 3,292 |
| 24 | `space` | 1,329 | 3,567 |
| 25 | `stylized` | 1,320 | 4,543 |
| 26 | `adventure` | 1,308 | 4,270 |
| 27 | `romance` | 1,296 | 4,447 |
| 28 | `black comedy` | 1,264 | 3,451 |
| 29 | `great acting` | 1,246 | 3,177 |
| 30 | `disturbing` | 1,234 | 3,398 |

## Amendment, 2026-09-15: two unhyphenated duplicates removed

The rule above cleans case and whitespace and nothing else, so it kept two pairs
that are the same tag spelled two ways: `thought-provoking` with
`thought provoking`, and `post-apocalyptic` with `post apocalyptic`. A judge
asked to rate both members of a pair is being asked the same question twice,
and the pair crowds out two other tags.

The unhyphenated member of each pair was dropped, and the next two tags below
the old cut were taken so the list is still 300:

| dropped | distinct users | taken instead | distinct users |
| --- | --- | --- | --- |
| `post apocalyptic` | 400 | `imaginative` | 310 |
| `thought provoking` | 321 | `paranoia` | 310 |

The hyphenated spellings stay, so no idea was lost. The `tags` column of
`movies.csv` was rebuilt from the amended list by the same rule. No
movie was left with an empty candidate list, and across the 100 movies in the
shipped file the tags per movie run from 5 to 89, with a median of 11.

Note that this is not the same thing as deciding whether `sci-fi` and
`science fiction` are one tag. That decision is still the student's, in Part 2.
Two spellings of one word are a defect in the list; two words for one idea are
a judgement call.
