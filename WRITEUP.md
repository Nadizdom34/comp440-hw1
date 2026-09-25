# HW1 writeup

**Name:** Nadezhda Dominguez Salinas
**Date:** 2026-09-25

Every placeholder below gets your answer, told to Claude or typed in here yourself. Every number
you give comes from a script in this repo; say which one. Claude may format tables and figures
here; the words are yours.

## Part 0. Predictions

Give these to Claude before any analysis runs. One sentence each, plus one sentence on why you
think so.

**(1) A movie you know well, and what its three most-used tags will be:** The movie White Chicks, and its associated tags would be comedy, action, and drama.

**(1) Why you think so:** The movie is very funny and includes two FBI agents as the main characters who have alot of action scenes throughout the film which are pretty dramatic.

**(2) Out of every 100 people who rated movies here, how many ever added a tag?** My guess is 22 people.

**(2) Why you think so:** I believe less than half of the people would take the time to associate a tag, and from that half (50) some people are indecisive and may decide to not add a tag, so the number could drop to 22.

**(3) Can one person's tags take over a movie's tag list? Yes or no:** Yes.

**(3) Why you think so:** It is possible if a movie has very few user associated tags to begin with, therefore one user's many tags could override the movies tags.

## Part 1. Whose data is this?

Code: `part1_data.py`.

**My rule for cutting 32 million ratings to 5 million** (written before reading `data/make_compact.py`)**:** My rule is that I would get rid of all ratings below 1, as I feel they are not as descriptive, and get rid of all ratings that are 1.5, 2.5, 4.5 as I feel they are not adding to the value of the rating.

**One rule I considered and rejected, and why:** I thought about dropping the rating values 2, 4, and only have the extreme rating scale of 1, 3, 5 to show the ratings associated with bad, okay, and great movies as this would make it easier to decode movies. I rejected it though, because it is too extreme, and I'm unsure if many movies have a 5 star ratings that outbalance their okay ratings so it might not be fair.

**One interesting thing from `data/README.md`:** I found it interesting that it is stated that a user is only eligible if they have at least 20 ratings, as I had a similar thought of only keeping users who had at least a certain threshold of ratings.

**How the script's rule differs from mine, and what each keeps that the other drops:** The rule differs from mine as it describes to only keep a certain amount of the top movies and filters a lot more by a certain threshold of user unique ratings made, along with adding a uniform random sample of the remaining eligible users. Meanwhile mine, drops all the ratings below 1 and all of the half step ratings besides the 3.5 ratings, so mine is missing a lot more of the filtering in order to get from 32M rating to 5M ratings. In my rule the users survive because I did not put a certain number threshold for the amount of ratings a user needs, and also all of the half step ratings are possible to survive in their version of rules, meanwhile mine gets rid of all but one half step ratings (3.5).

**First check. Which of Claude's numbers, the different route you took, and whether it matched** (one good target: 6 tags are the literal text `NA`, which pandas drops unless told not to)**:** The number I checked was the "tag applications", the different route I took was reading the data/README.md and both numbers matched to be 1,244,210 for part1_data.py section (d).

**Second check. Which of Claude's numbers, the different route you took, and whether it matched:** I checked the movies with at least one tag for the second check, the different route I took was using a different reader for the file and instead of using .nunique() I did a len(.groupby("movieId")) to group the tags by movie and then count the number of movies (with at least one tag), both numbers matched 3,999 for part1_data section (d).

## Part 2. What tags best describe a movie?

Code: `part2_tags.py`.

**My movie, and why I picked it:** White Chicks. I picked it because it is one of my favorite movies, and I think it's hilarious how they incorporated such a girly theme into an action-ish concept for a movie.

**Its most misleading tag in the count-ordered list, and why it misleads:** The most misleading tag is Terry Crews, because why would someone put the actors name as a Tag, I expected tags to be mainly descriptive factors of the movies or acting style, or theme, instead of the actor's names.

**What I learned about how MovieLens collects ratings and tags, from rating and tagging my movie myself (about 100 words):** I learned from going onto the movielens myself that to rate the movie you just click on the number of stars that you think it's worth. Next when attaching tags to the movie you are able to observe the community tags through an organized view of top tags or all tags, along with sorting them alphabetically or in different ways. Once you type in the tag you want it pops up the little text box along with the number of times that that tag has been used which is interesting that they allow you to see other tags before adding your own, as I feel like it might influence some users perspective of what tag to associate a movie with if they are able to see other users tags. I think it's interesting that I can make my own tag instead of having a pre-selected options of tag I can associate something with, and that when I started typing it provides suggestions to fill the word for the tag I'm trying to write.

### Up close

One sentence on the figure written before you saw it and one after. The two tables are where the
details below come from. Say which script made them.

**The figure, when the tags and the ratings arrived. What I expected:** I believe that the ratings did not come into play until at least a year after the movie was released, because people could not have readily accessed the movie on their phone or laptop back then, so they would have to have waited until it was out on DVD unless they went to the theatre. So I expected there to be a slow amount of ratings until the most recent years and for the tags I think that feature appeared years after the movie, so it most likely did not start getting tagged in slow increments until the 2010s.
**The figure, what it shows:** In the figure I notice that the ratings slowly started around 20 rating beginning in 2004 and slowly increased and then decreased a few years after released, until about 2015 where the amount of ratings skyrocketed to around 100 ratings before then starting a decreasing trend until 2023. Then in the tag ratings it is very scattered and mainly empty until the first activity of tagging in 2006 and then disappears until 2009 and 2010 with a very few amount of tags lower than 5, and 0 tags for the years 2011 and 2012 until 2013 a boost of activity, and the highest boom of tags are until 2018 where there was a boom of over 10 tag applications. Overall I notice that the amount of ratings for the movie are noticeably higher than the tag applications.

**Two interesting details I learned up close that the counts did not show:** The first detail that stands out to me in the figures is the appearance of a boom in ratings/tag applications, I did not expect there to be a peak popularity of number of tags/ratings almost more than a decade of the movies release. The second detail that stands out is the appearance of what I had mentioned of a few users being the ones who made the most number of associated tags to the movies, though the number of top taggers is lower than I expected.

**Anything up close that contradicted something I had already written down. Which one, what the data showed, and what you now think. Or "nothing yet":** The contradiction shown is the number of tags that the movie/ number of ratings as I had thought there would be a much higher number of rating since I associated the movie White Chicks to be very popular, but the actual number is very low. Also contradicts the pattern I predicted of the slow movement of number of ratings/tag applications as it shows boom in activity for both. One of the contradiction besides the slow movement was not expected anything of ratings until a year later, yet the figure shows ratings in the first years. Now I can see that the pattern is more random and dispersed especially for tag applications as there are some years that there is no activity.

### My definition

**My `score(movie, tag)`** (one or two sentences, precise enough that a classmate could code it)**:** XXXX

**One definition I considered and rejected, and why:** XXXX

**Which tags I merged as the same tag, which I kept apart, and why:** XXXX

**Why my definition, in about 150 words. Name one thing it gains and one thing it loses:**

XXXX

### The judge

The two slots below are read by scripts, so write them as bare lines: one item to a line, the
movieId first, no bullets and no numbering. A movie line looks like `296, Pulp Fiction (1994)`.
An order line looks like `296: nonlinear, hit men, dark comedy, ...`, the tags best first.

**My ten movies:**

XXXX

**My own order of the ten most-used tags, written before looking at any data: my movie from step 1, then my nine others from step 4:**

8531: comedy, disguise, black comedy, silly, fbi, undercover, black men dressed up like white women, buddy cop, cross dressing, Terry Crews

**One criterion I considered for the judge and rejected, and why** (the one I used is in `judge/criterion.md`)**:** XXXX

**Agreement. The number `agreement.py` gives for your `score()`, for popularity and for your own order, and which of the three came closest to the judge:** XXXX

**How the judge skill is built: the files it is made of and what each one does (about 150 words):**

XXXX

**What happens when I run `/judge`, from the first check to the CSV (about 150 words):**

XXXX

**Why a skill: what a skill like this gives you that a script or a prompt alone does not, and where you would use one next (about 100 words):**

XXXX

### The viewer and the disagreements

**One thing `movie_results.html` showed me that was useful, and one thing about it that got in my way:** XXXX

Then three improvements. For each: what the page would not let you see, what you had Claude
change, and what the changed page shows that the first draft did not.

**Improvement 1:** XXXX

**Improvement 2:** XXXX

**Improvement 3:** XXXX

Then the three disagreements. A disagreement is a movie and a tag where your `score()` and the
judge are furthest apart. For each: the movie and the tag, where your `score()` put it and where
the judge put it, and what you think accounts for the gap.

**Disagreement 1:** XXXX

**Disagreement 2:** XXXX

**Disagreement 3:** XXXX

**One other high-level pattern in the results, and what you think is behind it:** XXXX

## Predictions revisited

**Which of my three predictions were wrong, and what I make of each miss:** XXXX

## Part 3. What tags best describe a user?

Code: `part3_users.py`.

The slot below is read by a script, so write it as bare lines: one rating to a line, no bullets
and no numbering, the movieId first and the rating last, as in `296, Pulp Fiction (1994), 4.5`.

**My 20 ratings:**

XXXX

**My `score(user, tag)`, in a sentence, and why I started there (about 100 words):**

XXXX

**What my score says about me: my top ten tags, and whether they describe my taste (about 100 words):**

XXXX

**What my user viewer shows and why I chose that (about 100 words):**

XXXX

**What I put in the description column for a person, and why (about 150 words):**

XXXX

**My criterion for people: what it asks the judge to do that the movie criterion did not (about 60 words):**

XXXX

**The user-tag pairs I chose to judge, how many, and why those (about 100 words):**

XXXX

**Improvement 1: what I changed in the scoring function, what the judge and the viewer showed before and after (about 150 words):**

XXXX

**Improvement 2: the same (about 150 words):**

XXXX

## Part 4. Working with Claude

Give these to Claude the way you gave it the rest. Graded on the catch and the candor, not on
making Claude look good or bad.

**A moment where Claude was wrong or overconfident, how you caught it, and where it
happened. Name the part and the step, so the moment can be found:** XXXX

**One call where you overrode Claude, and why:** XXXX

**What you would hand to Claude sooner next time:** XXXX

**Did Claude name the misleading tag in Part 2 step 1 before you did? What happened:** XXXX

**The figure. Would asking Claude "what does this show?" have produced your sentence, and what
would have been missing from it:** XXXX

**Hours spent:** XXXX

**Anyone who helped you, or "no one":** XXXX
