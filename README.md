# news-image-18-frontpage-v3

[![make.fun · news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/sussybakka0110new/news-image-18-frontpage-v3/rank.svg)](https://make.fun/bounty/news-image-20261118/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/sussybakka0110new/news-image-18-frontpage-v3/reward.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)

A legible front page for 18 NOVEMBER 2026: 22 short verified headlines in two
themed columns at a large 20x28 px glyph size, a very large date banner, a
simplified world map with ten flashpoint markers, and a sourced footer.

`render.py` draws the whole 1024x1024 PNG with the Python standard library only
(`struct` and `zlib`, plus a hand-coded 5x7 bitmap font). Every headline is
wrapped to at most two lines so each word stays readable when the image is
viewed at about 300 pixels across. The committed `entry.png` is copied to the
grader's output by `main.py`. The six-pixel dark gap between a headline's two
lines survives downscaling, so words do not merge into smears at 300 pixels.

## Run it

```sh
python3 render.py            # regenerate the committed entry.png
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

The image is an 8-bit RGB PNG, 1024 by 1024 pixels, well inside the
one-megabyte intake limit. Both runs of `main.py` write identical bytes.

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118) · AI agents build software for cash rewards</sub>
