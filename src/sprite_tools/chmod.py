"""Change file permissions on a Sprite environment."""

import argparse
import json
import re
import subprocess
import sys

from sprite_tools.context import resolve_context, build_api_cmd, check_api_error


def main():
    parser = argparse.ArgumentParser(description="Change file permissions on a Sprite")
    parser.add_argument("-s", "--sprite", default=None, help="Sprite name")
    parser.add_argument("-o", "--org", default=None, help="Organization")
    parser.add_argument("-r", "--recursive", action="store_true", help="Apply recursively")
    parser.add_argument("mode", help="Octal mode (e.g. 0755 or 644)")
    parser.add_argument("path", help="Path on the sprite")
    args = parser.parse_args()

    if not re.match(r"^[0-7]{3,4}$", args.mode):
        print(f"Error: invalid mode '{args.mode}' (expected octal, e.g. 0755 or 644)", file=sys.stderr)
        sys.exit(1)

    sprite, org = resolve_context(args.sprite, args.org)

    body = {"path": args.path, "mode": args.mode, "recursive": args.recursive}
    cmd = build_api_cmd(sprite, org, "/fs/chmod", [
        "-X", "POST", "-H", "Content-Type: application/json", "--data-binary", "@-",
    ])

    result = subprocess.run(cmd, input=json.dumps(body).encode(), capture_output=True)
    if result.returncode != 0:
        print(f"Error changing permissions on {sprite}:{args.path}", file=sys.stderr)
        print(result.stderr.decode(), file=sys.stderr)
        sys.exit(1)

    api_err = check_api_error(result.stdout)
    if api_err:
        print(f"Error: {api_err}", file=sys.stderr)
        sys.exit(1)

    print(f"Changed mode of {sprite}:{args.path} to {args.mode}", file=sys.stderr)


if __name__ == "__main__":
    main()
