# sprite-tools

A suite of command-line tools for [Sprites](https://sprites.dev) that extend the standard `sprite` CLI with additional functionality.

## Tools

### sprite-get

Download a file from a Sprite environment.

```
sprite-get [-s SPRITE] [-o ORG] remote_path [local_path]
```

Use `-` as `local_path` to write to stdout.

### sprite-put

Upload a file to a Sprite environment.

```
sprite-put [-s SPRITE] [-o ORG] local_path [remote_path]
```

Use `-` as `local_path` to read from stdin (requires `remote_path`).

### sprite-cat

Read a file from a Sprite environment and write it to stdout.

```
sprite-cat [-s SPRITE] [-o ORG] path
```

### sprite-ls

List files in a Sprite environment.

```
sprite-ls [-s SPRITE] [-o ORG] [-l] [-r] [path]
```

- `-l` — long format showing mode, size, date, and name
- `-r` — recursive listing
- Default path: home directory

### sprite-rm

Delete files from a Sprite environment.

```
sprite-rm [-s SPRITE] [-o ORG] [-r] [-f] path [path ...]
```

- `-r` — delete directories recursively
- `-f` — suppress errors for missing files

### sprite-cp

Copy files within a Sprite environment.

```
sprite-cp [-s SPRITE] [-o ORG] [-r] source dest
```

- `-r` — copy directories recursively

### sprite-mv

Move or rename files within a Sprite environment.

```
sprite-mv [-s SPRITE] [-o ORG] source dest
```

### sprite-chmod

Change file permissions on a Sprite environment.

```
sprite-chmod [-s SPRITE] [-o ORG] [-r] mode path
```

- `mode` — octal permission mode (e.g. `0755` or `644`)
- `-r` — apply recursively

All tools resolve the target Sprite using (in order of precedence):

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
