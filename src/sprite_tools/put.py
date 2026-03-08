"""Put a file onto a Sprite environment."""

import argparse
import os
import subprocess
import sys
import urllib.parse

from sprite_tools.context import resolve_context, check_api_error


def main():
    parser = argparse.ArgumentParser(description="Put a file onto a Sprite")
    parser.add_argument("-s", "--sprite", default=None, help="Sprite name")
    parser.add_argument("-o", "--org", default=None, help="Organization")
    parser.add_argument("local_path", help="Local file to upload")
    parser.add_argument("remote_path", nargs="?", default=None,
                        help="Path on the sprite (default: basename of local_path)")
    args = parser.parse_args()

    sprite, org = resolve_context(args.sprite, args.org)

    if args.local_path == "-":
        data = sys.stdin.buffer.read()
        remote_path = args.remote_path
        if not remote_path:
            print("Error: remote_path is required when reading from stdin", file=sys.stderr)
            sys.exit(1)
    else:
        with open(args.local_path, "rb") as f:
            data = f.read()
        remote_path = args.remote_path or os.path.basename(args.local_path)

    encoded = urllib.parse.quote(remote_path, safe="")
    cmd = ["sprite", "api", "-s", sprite,
           f"/fs/write?path={encoded}&mkdir=true",
           "-X", "PUT", "-H", "Content-Type: application/octet-stream",
           "--data-binary", "@-"]
    if org:
        cmd.extend(["-o", org])

    result = subprocess.run(cmd, input=data, capture_output=True)
    if result.returncode != 0:
        print(f"Error writing to {sprite}:{remote_path}", file=sys.stderr)
        print(result.stderr.decode(), file=sys.stderr)
        sys.exit(1)

    api_err = check_api_error(result.stdout)
    if api_err:
        print(f"Error: {api_err}", file=sys.stderr)
        sys.exit(1)

    print(f"Uploaded {len(data)} bytes to {sprite}:{remote_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
