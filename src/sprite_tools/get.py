"""Get a file from a Sprite environment."""

import argparse
import os
import subprocess
import sys
import urllib.parse

from sprite_tools.context import resolve_context


def main():
    parser = argparse.ArgumentParser(description="Get a file from a Sprite")
    parser.add_argument("-s", "--sprite", default=None, help="Sprite name")
    parser.add_argument("-o", "--org", default=None, help="Organization")
    parser.add_argument("remote_path", help="Path on the sprite")
    parser.add_argument("local_path", nargs="?", default=None,
                        help="Local destination (default: basename of remote_path in cwd)")
    args = parser.parse_args()

    sprite, org = resolve_context(args.sprite, args.org)
    local_path = args.local_path or os.path.basename(args.remote_path)

    encoded = urllib.parse.quote(args.remote_path, safe="")
    cmd = ["sprite", "api", "-s", sprite, f"/fs/read?path={encoded}"]
    if org:
        cmd.extend(["-o", org])

    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        print(f"Error reading {sprite}:{args.remote_path}", file=sys.stderr)
        print(result.stderr.decode(), file=sys.stderr)
        sys.exit(1)

    with open(local_path, "wb") as f:
        f.write(result.stdout)

    print(f"Saved {len(result.stdout)} bytes to {local_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
