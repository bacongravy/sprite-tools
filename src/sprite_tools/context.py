"""Shared config resolution and helpers for sprite-tools CLI commands."""

import json
import os
import sys


def find_sprite_file():
    """Walk up from cwd looking for a .sprite file."""
    d = os.getcwd()
    while True:
        candidate = os.path.join(d, ".sprite")
        if os.path.isfile(candidate):
            with open(candidate) as f:
                return json.load(f)
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def load_global_config():
    """Load ~/.sprites/sprites.json and return current_selection."""
    path = os.path.expanduser("~/.sprites/sprites.json")
    if not os.path.isfile(path):
        return None
    with open(path) as f:
        data = json.load(f)
    return data.get("current_selection")


def resolve_context(args_sprite, args_org):
    """Resolve sprite name and org from args, .sprite file, or global config."""
    sprite_file = find_sprite_file()
    if sprite_file:
        sprite = args_sprite or sprite_file.get("sprite")
        org = args_org or sprite_file.get("organization")
        return sprite, org

    global_cfg = load_global_config()
    org = args_org or (global_cfg and global_cfg.get("org"))
    if not args_sprite:
        print("Error: no .sprite file found and no -s specified", file=sys.stderr)
        sys.exit(1)
    return args_sprite, org


def build_api_cmd(sprite, org, endpoint, curl_args=None):
    """Build a sprite api command. curl_args come after the endpoint."""
    cmd = ["sprite", "api", "-s", sprite, endpoint]
    if org:
        cmd.extend(["-o", org])
    if curl_args:
        cmd.extend(curl_args)
    return cmd


def check_api_error(stdout_bytes, expect_json=False):
    """Check API response for errors. Returns error string if present, else None.

    Detects both JSON {"error": ...} responses and plain-text error messages
    like "Bad Request". If expect_json is True, any non-JSON response is an error.
    """
    try:
        data = json.loads(stdout_bytes)
        if isinstance(data, dict) and "error" in data:
            return data["error"]
    except (json.JSONDecodeError, ValueError):
        text = stdout_bytes.decode("utf-8", errors="replace").strip()
        if text and (expect_json or text in ("Bad Request", "Not Found",
                                              "Internal Server Error",
                                              "Unauthorized", "Forbidden")):
            return text
    return None
