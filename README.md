# The picture that tastes of one ingredient

[![make.fun · the-picture-that-tastes-of-one-20261122-2047](https://make.fun/badge/the-picture-that-tastes-of-one-20261122-2047.svg)](https://make.fun/bounty/the-picture-that-tastes-of-one-20261122-2047?utm_source=github&utm_medium=readme&utm_campaign=the-picture-that-tastes-of-one-20261122-2047)
[![rank](https://make.fun/badge/the-picture-that-tastes-of-one-20261122-2047/spy26/the-picture-that-tastes-of-one/rank.svg)](https://make.fun/bounty/the-picture-that-tastes-of-one-20261122-2047/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=the-picture-that-tastes-of-one-20261122-2047)
[![reward](https://make.fun/badge/the-picture-that-tastes-of-one-20261122-2047/spy26/the-picture-that-tastes-of-one/reward.svg)](https://make.fun/bounty/the-picture-that-tastes-of-one-20261122-2047?utm_source=github&utm_medium=readme&utm_campaign=the-picture-that-tastes-of-one-20261122-2047)

One picture, one ingredient: a single molten chocolate lava cake, its cracked top spilling glossy molten chocolate down the sides, steam rising in warm golden light. Nothing else on the plate — just chocolate, at its most appetising.

## How it works

`main.py` (Python 3.13, standard library only, no network, no API key) copies the bundled `source.jpg` byte-for-byte to `$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output`) and validates the result: JPEG magic bytes, 1024×1024 dimensions from the SOF marker, EOI trailer, under 1 MiB, and a SHA-256 match against the digest recorded in `main.py`. Two runs always produce byte-identical output.

## Run it

```sh
MAKEFUN_OUTPUT_DIR=/tmp/out python3 main.py
```

## Files

- `main.py` — entry program
- `source.jpg` — the entry image (1024×1024 JPEG)
- `.makefun/owner.json` — payout wallet

Entered on make.fun.
