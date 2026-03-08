"""Read a file from a Sprite environment and write it to stdout."""

import argparse
import subprocess
import sys
import urllib.parse

from sprite_tools.context import resolve_context, build_api_cmd, check_api_error


def main():
    parser = argparse.ArgumentParser(description="Read a file from a Sprite to stdout")
    parser.add_argument("-s", "--sprite", default=None, help="Sprite name")
    parser.add_argument("-o", "--org", default=None, help="Organization")
    parser.add_argument("path", help="Path on the sprite")
    args = parser.parse_args()

    sprite, org = resolve_context(args.sprite, args.org)

    encoded = urllib.parse.quote(args.path, safe="")
    cmd = build_api_cmd(sprite, org, f"/fs/read?path={encoded}")

    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        print(f"Error reading {sprite}:{args.path}", file=sys.stderr)
        print(result.stderr.decode(), file=sys.stderr)
        sys.exit(1)

    api_err = check_api_error(result.stdout)
    if api_err:
        print(f"Error: {api_err}", file=sys.stderr)
        sys.exit(1)

    sys.stdout.buffer.write(result.stdout)


if __name__ == "__main__":
    main()
