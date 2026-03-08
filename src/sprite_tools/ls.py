"""List files in a Sprite environment."""

import argparse
import json
import subprocess
import sys
import urllib.parse

from sprite_tools.context import resolve_context, build_api_cmd, check_api_error


def main():
    parser = argparse.ArgumentParser(description="List files on a Sprite")
    parser.add_argument("-s", "--sprite", default=None, help="Sprite name")
    parser.add_argument("-o", "--org", default=None, help="Organization")
    parser.add_argument("-l", "--long", action="store_true", help="Long format")
    parser.add_argument("-r", "--recursive", action="store_true", help="Recursive listing")
    parser.add_argument("path", nargs="?", default=".", help="Path to list (default: home directory)")
    args = parser.parse_args()

    sprite, org = resolve_context(args.sprite, args.org)

    encoded = urllib.parse.quote(args.path, safe="")
    endpoint = f"/fs/list?path={encoded}"
    if args.recursive:
        endpoint += "&recursive=true"
    cmd = build_api_cmd(sprite, org, endpoint)

    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        print(f"Error listing {sprite}:{args.path}", file=sys.stderr)
        print(result.stderr.decode(), file=sys.stderr)
        sys.exit(1)

    api_err = check_api_error(result.stdout)
    if api_err:
        print(f"Error: {api_err}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(result.stdout)
    entries = data.get("entries") or []

    for entry in entries:
        name = entry.get("name", "")
        is_dir = entry.get("isDir", False)
        if args.long:
            mode = entry.get("mode", "")
            size = entry.get("size", 0)
            mod_time = entry.get("modTime", "")[:19]
            suffix = "/" if is_dir else ""
            print(f"{mode:>6}  {size:>10}  {mod_time}  {name}{suffix}")
        else:
            print(f"{name}/" if is_dir else name)


if __name__ == "__main__":
    main()
