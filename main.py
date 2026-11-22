#!/usr/bin/env python3
"""Entry program for make.fun — "The picture that tastes of one ingredient".

The entry image is a single molten chocolate lava cake on a dark ceramic
plate: one cake, nothing else on the plate, its cracked top spilling glossy
molten chocolate down the sides and pooling on the plate, thin steam rising
in warm golden side light against a dark moody background. One ingredient,
one dish, one moment — chocolate, at its most appetising.

How it works
------------
This program does not generate or alter any pixels. It copies the bundled
``source.jpg`` byte-for-byte into ``$MAKEFUN_OUTPUT_DIR/entry.png`` (falling
back to ``/output`` when the variable is unset) and then verifies the copy
end to end, so the submitted file is exactly the image that was judged
during development:

* the copy starts with the JPEG magic bytes ``FF D8`` and ends with the
  end-of-image trailer ``FF D9``;
* the width and height parsed from the JPEG Start-Of-Frame marker are
  exactly 1024 x 1024;
* the file is smaller than 1 MiB;
* the SHA-256 digest of the written file matches ``EXPECTED_SHA256``
  below, proving the copy is byte-identical to the bundled source.

The program never writes into the repository directory; the only file it
creates is the entry image inside the output directory. It uses only the
Python standard library, needs no network access and no API key, and two
runs always produce byte-identical output because the copy is pure.
"""

import hashlib
import os
import sys

# SHA-256 of the bundled source.jpg (1024 x 1024 JPEG, 187235 bytes):
# a single molten chocolate lava cake, chocolate flowing, warm light.
EXPECTED_SHA256 = "29cf4bc2730bcaea1cf7e4343b2e663b5aa0970d7558f88a0edb3c685e52501c"
EXPECTED_WIDTH = 1024
EXPECTED_HEIGHT = 1024
MAX_BYTES = 1_048_576  # 1 MiB limit for the entry file.

SOURCE_NAME = "source.jpg"
ENTRY_NAME = "entry.png"


def _fail(message):
    """Print an error to stderr and exit non-zero."""
    print("error: " + message, file=sys.stderr)
    raise SystemExit(1)


def _jpeg_dimensions(data):
    """Return (width, height) parsed from the JPEG SOF marker.

    Walks the JPEG marker segments from the SOI marker until it finds a
    Start-Of-Frame segment (baseline/extended/progressive, 0xC0-0xCF
    excluding the DHT/JPG/arithmetic markers) and reads the height and
    width stored there. Raises ValueError on malformed input.
    """
    if len(data) < 4 or data[0] != 0xFF or data[1] != 0xD8:
        raise ValueError("missing JPEG SOI marker (expected FF D8)")
    pos = 2
    while pos + 9 <= len(data):
        if data[pos] != 0xFF:
            raise ValueError("expected JPEG marker at offset %d" % pos)
        marker = data[pos + 1]
        # Standalone markers carry no length field; skip them.
        if marker in (0x01,) or 0xD0 <= marker <= 0xD9:
            pos += 2
            continue
        seg_len = (data[pos + 2] << 8) | data[pos + 3]
        if seg_len < 2 or pos + 2 + seg_len > len(data):
            raise ValueError("truncated JPEG segment at offset %d" % pos)
        if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
                      0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
            height = (data[pos + 5] << 8) | data[pos + 6]
            width = (data[pos + 7] << 8) | data[pos + 8]
            return width, height
        pos += 2 + seg_len
    raise ValueError("no JPEG Start-Of-Frame marker found")


def _validate(data):
    """Validate the entry bytes; fail with a clear message otherwise."""
    if len(data) == 0:
        _fail("entry is empty")
    if len(data) > MAX_BYTES:
        _fail("entry is %d bytes, over the 1 MiB limit" % len(data))
    if data[0] != 0xFF or data[1] != 0xD8:
        _fail("entry does not start with JPEG magic bytes FF D8")
    if data[-2] != 0xFF or data[-1] != 0xD9:
        _fail("entry does not end with JPEG EOI trailer FF D9")
    try:
        width, height = _jpeg_dimensions(data)
    except ValueError as exc:
        _fail("cannot parse JPEG dimensions: %s" % exc)
    if (width, height) != (EXPECTED_WIDTH, EXPECTED_HEIGHT):
        _fail("entry is %dx%d, expected %dx%d"
              % (width, height, EXPECTED_WIDTH, EXPECTED_HEIGHT))
    digest = hashlib.sha256(data).hexdigest()
    if digest != EXPECTED_SHA256:
        _fail("SHA-256 mismatch: got %s, expected %s"
              % (digest, EXPECTED_SHA256))
    return digest


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source_path = os.path.join(here, SOURCE_NAME)
    if not os.path.isfile(source_path):
        _fail("bundled source image not found: %s" % source_path)

    with open(source_path, "rb") as fh:
        data = fh.read()

    # Validate the bundled source BEFORE writing anything, so a corrupt
    # or swapped source.jpg fails fast instead of producing a bad entry.
    _validate(data)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    out_dir_abs = os.path.abspath(out_dir)
    if out_dir_abs == here:
        _fail("refusing to write into the repository directory %s; "
              "set MAKEFUN_OUTPUT_DIR to a separate output directory"
              % here)
    try:
        os.makedirs(out_dir_abs, exist_ok=True)
    except OSError as exc:
        _fail("cannot create output directory %s: %s" % (out_dir_abs, exc))
    entry_path = os.path.join(out_dir_abs, ENTRY_NAME)
    if os.path.abspath(entry_path) == os.path.abspath(source_path):
        _fail("entry path %s would overwrite the bundled source image"
              % entry_path)

    # Pure byte-for-byte copy: the entry is exactly the bundled image.
    with open(entry_path, "wb") as fh:
        fh.write(data)

    with open(entry_path, "rb") as fh:
        written = fh.read()
    if written != data:
        _fail("written file differs from the bundled source image")

    digest = _validate(written)
    width, height = _jpeg_dimensions(written)
    print("wrote %s (%d bytes, %dx%d JPEG, sha256 %s)"
          % (entry_path, len(written), width, height, digest))
    return 0


if __name__ == "__main__":
    sys.exit(main())
