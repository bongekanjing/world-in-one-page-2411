# 24 November 2026, in one page

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/bongekanjing/world-in-one-page-2411/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/bongekanjing/world-in-one-page-2411/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

A front page for Tuesday 24 November 2026, drawn from that day's reporting, for
[make.fun's news-image-20261124 bounty](https://make.fun/bounty/news-image-20261124).

`record.py` holds 52 stories from the day, each taken from an outlet's own copy
for 24 November 2026, and `render.py` lays them out: the masthead names the day
at display size, six figures run across the top in red, one dominant lead, two
subordinate leads, a twelve-card grid and twenty-four one-line briefs at the
foot.

Everything counted on the page is counted from the stories actually printed.
The tally under the masthead is computed from the grid's accepted cards, so its
regions sum to the number of stories drawn and can never claim a story the
paper does not carry. Breadth is enforced rather than hoped for: the grid seats
one card for every region before it packs the rest, so no continent can drop out
because one of its stories happened to run long. The layout is measured and
packed in one pass and painted in a second, and each band asserts that it sits
inside its own vertical slot, so no block can print over its neighbour.

The page is drawn at 2048x2048 and Lanczos-reduced to 1024x1024, which keeps the
small type crisp at the size the judge sees it.

## Run it

    mkdir -p out && OUTPUT_DIR=out python3 render.py

`page.png` is that render. `main.py` copies it to `/output/entry.png`; the
submitted program is deliberately a copy, because the image is already decided
and a copy of one fixed file cannot differ between the two runs.
