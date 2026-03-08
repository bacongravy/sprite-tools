# sprite-tools

A suite of command-line tools for [Sprites](https://sprites.dev) that extend the standard `sprite` CLI with additional functionality.

## Tools

### sprite-get

Download a file from a Sprite environment.

```
sprite-get [-s SPRITE] [-o ORG] remote_path [local_path]
```

### sprite-put

Upload a file to a Sprite environment.

```
sprite-put [-s SPRITE] [-o ORG] local_path [remote_path]
```

Both tools resolve the target Sprite using (in order of precedence):

1. The `-s` and `-o` command-line flags
2. A `.sprite` file found in the current directory or any parent
3. The global config at `~/.sprites/sprites.json`

## Installation

Install with [pipx](https://pipx.pypa.io/), which manages isolated environments for Python CLI tools:

```bash
# install pipx if you don't have it (macOS)
brew install pipx
pipx ensurepath

# install sprite-tools
pipx install git+https://github.com/bacongravy/sprite-tools.git
```

## License

MIT
