#!/usr/bin/env python3
"""
Generate a Sublime Merge .sublime-commands file from the official
gitmojis.json.
Usage
-----
$ python gitmoji_to_commands.py gitmojis.json  >  Gitmoji.sublime-commands
(or supply -o/--output to let the script write the file for you)

The generated JSON looks like:
[
    {
        "caption": "Gitmoji: Improve structure/format of the code :art: (🎨)",
        "command": "copy_to_clipboard",
        "args": { "text": "🎨 " }
    },
    ...
]
"""

import argparse
import json
import pathlib
import sys
from typing import Dict, List


def clean_description(desc: str) -> str:
    """
    • Trim leading/trailing spaces
    • Drop the final period, if any
    • Compress “ / ” to “/” to match the examples
    """
    desc = desc.strip()
    if desc.endswith("."):
        desc = desc[:-1]
    # normalise slashes – remove surrounding spaces
    desc = desc.replace(" /", "/").replace(" /", "/").replace("/", "/")
    return desc


def gitmoji_to_command(g: Dict[str, str]) -> Dict:
    """Convert a single gitmoji entry to a Sublime command-palette command."""
    caption = f"Gitmoji: {clean_description(g['description'])} {g['code']}"
    f"({g['emoji']})"
    return {
        "caption": caption,
        "command": "copy_to_clipboard",
        "args": {"text": f"{g['emoji']}"},
    }


def build_command_list(catalog: Dict) -> List[Dict]:
    """Create the list that will be dumped as JSON."""
    # keep the original order so it matches https://gitmoji.dev
    return [gitmoji_to_command(g) for g in catalog["gitmojis"]]


def main() -> None:
    p = argparse.ArgumentParser(
        description="Convert gitmojis.json →" "*.sublime-commands"
    )
    p.add_argument(
        "-i",
        "--input",
        type=pathlib.Path,
        help="gitmojis JSON file (as on" "gitmoji.dev)",
    )
    p.add_argument(
        "-o",
        "--output",
        type=pathlib.Path,
        help="Output .sublime-commands file (stdout if omitted)",
    )
    args = p.parse_args()

    try:
        catalog = json.loads(args.input.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as e:
        sys.exit(f"❌  Cannot read '{args.input}': {e}")

    commands = build_command_list(catalog)

    # Serialise with UTF-8 and no ASCII-escaping so emoji stay intact
    out_json = json.dumps(commands, ensure_ascii=False, indent=4)

    if args.output:
        args.output.write_text(out_json, encoding="utf-8")
        print(f"✅  Wrote {len(commands)} commands to {args.output}")
    else:
        print(out_json)


if __name__ == "__main__":
    main()