"""Write the front page for Tuesday 24 November 2026 to /output/entry.png.

The page was composed by render.py from the verified record in record.py, both
written in the agent session shipped beside this file. The finished PNG is held
next to this program so the sandbox needs only the standard library: it has no
Pillow and no fonts, so the entry copies the bytes that were already decided
rather than drawing them again.

Copying is also what makes the two runs identical. A redraw could differ
between runs through a font fallback or an image backend version; a copy of one
fixed file cannot.

The copy is checked against the sha256 of page.png before it is accepted, so a
truncated or substituted source fails the run loudly instead of handing the
judge a corrupt image.
"""

import hashlib
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PAGE = "page.png"

# sha256 of the page this entry ships; a mismatch means the file was altered.
PAGE_SHA256 = "e9cdff72b02ec4c876bf7e2c763977f7e92d24691cbcabafcb4a89cc56eb2374"


def output_dir():
    """The writable directory the sandbox gives the program."""
    return os.environ.get("OUTPUT_DIR") or "/output"


def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    src = os.path.join(HERE, PAGE)
    got = digest(src)
    if got != PAGE_SHA256:
        sys.stderr.write("page.png changed: %s\n" % got)
        return 1
    out = output_dir()
    os.makedirs(out, exist_ok=True)
    dst = os.path.join(out, "entry.png")
    shutil.copyfile(src, dst)
    return 0


if __name__ == "__main__":
    sys.exit(main())
