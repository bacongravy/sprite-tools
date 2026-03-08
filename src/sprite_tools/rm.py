"""Delete files from a Sprite environment."""

import argparse
import subprocess
import sys
import urllib.parse

from sprite_tools.context import resolve_context, build_api_cmd, check_api_error


def main():
    parser = argparse.ArgumentParser(description="Delete files on a Sprite")
    parser.add_argument("-s", "--sprite", default=None, help="Sprite name")
    parser.add_argument("-o", "--org", default=None, help="Organization")
    parser.add_argument("-r", "--recursive", action="store_true", help="Delete directories recursively")
    parser.add_argument("-f", "--force", action="store_true", help="Suppress errors for missing files")
    parser.add_argument("path", nargs="+", help="Path(s) to delete")
    args = parser.parse_args()

    sprite, org = resolve_context(args.sprite, args.org)
    errors = 0

    for path in args.path:
        encoded = urllib.parse.quote(path, safe="")
        endpoint = f"/fs/delete?path={encoded}"
        if args.recursive:
            endpoint += "&recursive=true"
        cmd = build_api_cmd(sprite, org, endpoint, ["-X", "DELETE"])

        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            if not args.force:
                print(f"Error deleting {sprite}:{path}", file=sys.stderr)
                print(result.stderr.decode(), file=sys.stderr)
            errors += 1
            continue

        api_err = check_api_error(result.stdout)
        if api_err:
            if not args.force:
                print(f"Error deleting {path}: {api_err}", file=sys.stderr)
            errors += 1
            continue

        print(f"Deleted {sprite}:{path}", file=sys.stderr)

    if errors and not args.force:
        sys.exit(1)


if __name__ == "__main__":
    main()
