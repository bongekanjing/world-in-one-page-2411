"""Write the front page for Tuesday 24 November 2026 to /output/entry.png.

The page was composed by render.py from the verified record in record.py, both
written in the agent session shipped beside this file. The finished PNG is held
next to this program so the sandbox needs only the standard library: it has no
Pillow and no fonts, so the entry copies the bytes that were already decided
rather than drawing them again.

Copying is also what makes the two runs identical. A redraw could differ
between runs through a font fallback or an image backend version; a copy of one
fixed file cannot.
"""

import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
PAGE = "page.png"


def output_dir():
    """The writable directory the sandbox gives the program."""
    return os.environ.get("OUTPUT_DIR") or "/output"


def main():
    out = output_dir()
    os.makedirs(out, exist_ok=True)
    shutil.copyfile(os.path.join(HERE, PAGE), os.path.join(out, "entry.png"))


if __name__ == "__main__":
    main()
