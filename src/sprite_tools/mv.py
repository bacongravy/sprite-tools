"""Move/rename files within a Sprite environment."""

import argparse
import json
import subprocess
import sys

from sprite_tools.context import resolve_context, build_api_cmd, check_api_error


def main():
    parser = argparse.ArgumentParser(description="Move/rename files on a Sprite")
    parser.add_argument("-s", "--sprite", default=None, help="Sprite name")
    parser.add_argument("-o", "--org", default=None, help="Organization")
    parser.add_argument("source", help="Source path")
    parser.add_argument("dest", help="Destination path")
    args = parser.parse_args()

    sprite, org = resolve_context(args.sprite, args.org)

    body = {"source": args.source, "dest": args.dest}
    cmd = build_api_cmd(sprite, org, "/fs/rename", [
        "-X", "POST", "-H", "Content-Type: application/json", "--data-binary", "@-",
    ])

    result = subprocess.run(cmd, input=json.dumps(body).encode(), capture_output=True)
    if result.returncode != 0:
        print(f"Error moving on {sprite}", file=sys.stderr)
        print(result.stderr.decode(), file=sys.stderr)
        sys.exit(1)

    api_err = check_api_error(result.stdout)
    if api_err:
        print(f"Error: {api_err}", file=sys.stderr)
        sys.exit(1)

    print(f"Moved {sprite}:{args.source} -> {args.dest}", file=sys.stderr)


if __name__ == "__main__":
    main()
