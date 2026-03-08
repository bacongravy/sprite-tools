"""Shared config resolution for sprite-tools CLI commands."""

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
