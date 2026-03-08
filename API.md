# Sprites API Reference

Unofficial API reference for [Sprites](https://sprites.dev), derived from the
[sprites-go](https://github.com/superfly/sprites-go),
[sprites-js](https://github.com/superfly/sprites-js), and
[sprites-py](https://github.com/superfly/sprites-py) SDK source code.

See also the [official API documentation](https://sprites.dev/api).

## Overview

- **Base URL**: `https://api.sprites.dev`
- **Authentication**: Bearer token in the `Authorization` header
- **Content-Type**: `application/json` (unless otherwise noted)
- **Path pattern**: Most endpoints live under `/v1/sprites/{name}/...`

## Authentication

All requests require a Bearer token:

```
Authorization: Bearer <token>
```

Tokens can be created from a Fly.io macaroon:

### Create Token

```
POST /v1/organizations/{org_slug}/tokens
Authorization: FlyV1 <fly_macaroon>
```

**Request body:**

```json
{
  "description": "string",
  "invite_code": "string"       // optional
}
```

**Response:**

```json
{
  "token": "string"
}
```

---

## Sprite Management

### Create Sprite

```
POST /v1/sprites
```

**Request body:**

```json
{
  "name": "string",
  "config": {
    "ram_mb": 512,
    "cpus": 1,
    "region": "string",
    "storage_gb": 10
  },
  "environment": {
    "KEY": "VALUE"
  }
}
```

**Timeout:** 120 seconds.

### Get Sprite

```
GET /v1/sprites/{name}
```

**Response:**

```json
{
  "id": "string",
  "name": "string",
  "organization_name": "string",
  "status": "string",
  "url": "string",
  "primary_region": "string",
  "bucket_name": "string",
  "created_at": "ISO8601",
  "updated_at": "ISO8601",
  "config": { ... },
  "environment": { ... },
  "url_settings": { ... }
}
```

### List Sprites

```
GET /v1/sprites
```

**Query parameters:**

| Parameter            | Type    | Description              |
|----------------------|---------|--------------------------|
| `max_results`        | integer | Max results per page     |
| `continuation_token` | string  | Pagination cursor        |
| `prefix`             | string  | Filter by name prefix    |

**Response:**

```json
{
  "sprites": [ ... ],
  "has_more": true,
  "next_continuation_token": "string"
}
```

### Delete Sprite

```
DELETE /v1/sprites/{name}
```

Returns `204 No Content`.

### Upgrade Sprite

```
POST /v1/sprites/{name}/upgrade
```

Returns `204 No Content`. Timeout: 60 seconds.

### Update URL Settings

```
PUT /v1/sprites/{name}
```

**Request body:**

```json
{
  "url_settings": {
    "auth": "public" | "sprite"
  }
}
```

---

## Command Execution

### Execute Command (WebSocket)

```
WebSocket /v1/sprites/{name}/exec
```

**Query parameters:**

| Parameter    | Type     | Description                          |
|--------------|----------|--------------------------------------|
| `cmd`        | repeated | Command arguments                    |
| `path`       | string   | Command path (argv[0])               |
| `env`        | repeated | Environment variables (`KEY=VALUE`)  |
| `dir`        | string   | Working directory                    |
| `tty`        | string   | `"true"` to allocate a PTY          |
| `rows`       | string   | Terminal height                      |
| `cols`       | string   | Terminal width                       |
| `stdin`      | string   | `"true"` to enable stdin             |
| `detachable` | string   | `"true"` for detachable sessions     |
| `cc`         | string   | `"true"` for control mode            |

**Binary stream protocol** — each binary message is prefixed with a stream ID
byte:

| ID | Stream    |
|----|-----------|
| 0  | STDIN     |
| 1  | STDOUT    |
| 2  | STDERR    |
| 3  | EXIT      |
| 4  | STDIN_EOF |

The EXIT message contains the exit code as a single byte following the stream
ID.

**Text messages** — JSON objects sent as text frames for control events:

| Type             | Description                      |
|------------------|----------------------------------|
| `port_opened`    | A port was opened on the sprite  |
| `port_closed`    | A port was closed on the sprite  |
| `session_info`   | Session metadata                 |
| `resize`         | Terminal resize request          |
| `signal`         | Signal delivery                  |

### Attach to Session

```
WebSocket /v1/sprites/{name}/exec/{session_id}
```

Same protocol as execute, without the `cmd` parameter. A legacy query
parameter form (`/exec?id={session_id}`) is also supported.

**Response headers:**

| Header                    | Description                                    |
|---------------------------|------------------------------------------------|
| `X-Sprite-Capabilities`  | Comma-separated server capabilities (e.g. `signal`, `control`) |
| `Sprite-Version`          | Server version string                          |

### Get Sprite Version

```
HEAD /v1/sprites/{name}/exec
```

Returns the `Sprite-Version` response header without starting a session.

### List Sessions

```
GET /v1/sprites/{name}/exec
```

**Response:**

```json
{
  "sessions": [
    {
      "id": "string",
      "command": "string",
      "workdir": "string",
      "created": "ISO8601",
      "bytes_per_second": 0,
      "is_active": true,
      "tty": false,
      "last_activity": "ISO8601"
    }
  ]
}
```

### Kill Session

```
POST /v1/sprites/{name}/exec/{session_id}/kill
```

**Query parameters** (alternative to request body):

| Parameter | Type   | Description                          |
|-----------|--------|--------------------------------------|
| `signal`  | string | Signal name (e.g. `TERM`, `KILL`)    |
| `timeout` | string | Timeout duration (e.g. `"0s"`)       |

**Request body** (alternative to query parameters):

```json
{
  "signal": "SIGTERM",
  "timeout": 10
}
```

**Response:** NDJSON stream of progress messages. Returns `410 Gone` if the
session has already exited.

---

## Control Connection (Multiplexed WebSocket)

```
WebSocket /v1/sprites/{name}/control
```

A multiplexed connection that can run multiple operations concurrently using
JSON control envelopes (sent as text frames prefixed with `control:`) and
binary data frames using the same stream ID protocol as exec.

Clients should send the `Sprite-Client-Features: control` header when
connecting.

**Supported operations:** `exec`, `fs.read`, `fs.write`, `fs.list`,
`fs.delete`, `fs.chmod`, `fs.chown`, `fs.copy`, `fs.rename`, `proxy`

**Start an operation:**

```json
{
  "type": "op.start",
  "op": "exec",
  "args": {
    "cmd": ["ls", "-la"],
    "env": ["KEY=VALUE"],
    "dir": "/app",
    "tty": "false",
    "rows": "24",
    "cols": "80",
    "stdin": "false"
  }
}
```

**Completion message:**

```json
{
  "type": "op.complete",
  "args": {
    "exitCode": 0
  }
}
```

**Error message:**

```json
{
  "type": "op.error",
  "args": { ... }
}
```

---

## Proxy (TCP Tunnel)

```
WebSocket /v1/sprites/{name}/proxy
```

Opens a TCP tunnel to a port inside the sprite.

**Initialization** — client sends a text message:

```json
{
  "host": "localhost",
  "port": 8080
}
```

**Server response:**

```json
{
  "status": "connected",
  "target": "string"
}
```

After the handshake, all subsequent messages are bidirectional binary frames
forwarded to/from the TCP connection.

---

## Filesystem

### List Directory

```
GET /v1/sprites/{name}/fs/list
```

**Query parameters:**

| Parameter    | Type   | Description                            |
|--------------|--------|----------------------------------------|
| `path`       | string | File or directory path                 |
| `workingDir` | string | Working directory for relative paths   |
| `recursive`  | string | `"true"` for recursive listing         |

**Response:**

```json
{
  "path": "string",
  "entries": [
    {
      "name": "string",
      "path": "string",
      "type": "string",
      "size": 1024,
      "mode": "0755",
      "modTime": "ISO8601",
      "isDir": false
    }
  ],
  "count": 5
}
```

### Read File

```
GET /v1/sprites/{name}/fs/read
```

**Query parameters:**

| Parameter    | Type   | Description                            |
|--------------|--------|----------------------------------------|
| `path`       | string | File path                              |
| `workingDir` | string | Working directory for relative paths   |

**Response:** Binary file contents (`application/octet-stream`). May return
`206 Partial Content` for range requests.

### Write File

```
PUT /v1/sprites/{name}/fs/write
Content-Type: application/octet-stream
```

**Query parameters:**

| Parameter      | Type   | Description                            |
|----------------|--------|----------------------------------------|
| `path`         | string | File path                              |
| `workingDir`   | string | Working directory for relative paths   |
| `mode`         | string | Octal permissions (e.g. `"0644"`)      |
| `mkdirParents` | string | `"true"` to create parent directories  |

**Body:** Binary file contents.

**Response:**

```json
{
  "path": "string",
  "size": 1024,
  "mode": "0644"
}
```

### Delete File or Directory

```
DELETE /v1/sprites/{name}/fs/delete
```

**Query parameters:**

| Parameter    | Type   | Description                            |
|--------------|--------|----------------------------------------|
| `path`       | string | File or directory path                 |
| `workingDir` | string | Working directory for relative paths   |
| `recursive`  | string | `"true"` for recursive delete          |

**Response:**

```json
{
  "deleted": ["string"],
  "count": 1
}
```

### Rename

```
POST /v1/sprites/{name}/fs/rename
```

**Request body:**

```json
{
  "source": "string",
  "dest": "string",
  "workingDir": "string"
}
```

**Response:**

```json
{
  "source": "string",
  "dest": "string"
}
```

### Copy

```
POST /v1/sprites/{name}/fs/copy
```

**Request body:**

```json
{
  "source": "string",
  "dest": "string",
  "workingDir": "string",
  "recursive": true
}
```

**Response:**

```json
{
  "copied": [{ "source": "string", "dest": "string" }],
  "count": 1,
  "totalBytes": 1024
}
```

### Change Permissions

```
POST /v1/sprites/{name}/fs/chmod
```

**Request body:**

```json
{
  "path": "string",
  "workingDir": "string",
  "mode": "0755",
  "recursive": false
}
```

**Response:**

```json
{
  "affected": [{ "path": "string", "mode": "0755" }],
  "count": 1
}
```

### Change Ownership

Available via the control connection only (no REST endpoint).

**Control operation:** `fs.chown`

**Parameters:**

| Parameter   | Type    | Description                            |
|-------------|---------|----------------------------------------|
| `path`      | string  | File or directory path                 |
| `workingDir`| string  | Working directory for relative paths   |
| `uid`       | integer | User ID                                |
| `gid`       | integer | Group ID                               |
| `recursive` | boolean | Apply recursively                      |

---

## Checkpoints

### List Checkpoints

```
GET /v1/sprites/{name}/checkpoints
```

**Query parameters:**

| Parameter | Type   | Description    |
|-----------|--------|----------------|
| `history`    | string | History filter            |
| `includeAuto`| string | `"true"` to include auto checkpoints |

**Response:**

```json
[
  {
    "id": "string",
    "create_time": "ISO8601",
    "comment": "string",
    "history": ["string"],
    "is_auto": false
  }
]
```

### Get Checkpoint

```
GET /v1/sprites/{name}/checkpoints/{checkpoint_id}
```

**Response:** Single checkpoint object (same format as list items).

### Create Checkpoint

```
POST /v1/sprites/{name}/checkpoint
```

**Request body:**

```json
{
  "comment": "string"    // optional
}
```

**Response:** NDJSON stream of progress messages.

### Restore Checkpoint

```
POST /v1/sprites/{name}/checkpoints/{checkpoint_id}/restore
```

**Response:** NDJSON stream of progress messages.

---

## Services

### List Services

```
GET /v1/sprites/{name}/services
```

**Response:**

```json
[
  {
    "name": "string",
    "cmd": "string",
    "args": ["string"],
    "needs": ["string"],
    "http_port": 8080,
    "state": {
      "name": "string",
      "status": "stopped" | "starting" | "running" | "stopping" | "failed",
      "pid": 1234,
      "started_at": "ISO8601",
      "error": "string",
      "restart_count": 0,
      "next_restart_at": "ISO8601"
    }
  }
]
```

### Get Service

```
GET /v1/sprites/{name}/services/{service_name}
```

**Response:** Single service object (same format as list items).

### Create or Update Service

```
PUT /v1/sprites/{name}/services/{service_name}
```

**Query parameters:**

| Parameter  | Type   | Description                          |
|------------|--------|--------------------------------------|
| `duration` | string | Monitoring duration (e.g. `"30s"`)   |

**Request body:**

```json
{
  "cmd": "string",
  "args": ["string"],
  "needs": ["string"],
  "http_port": 8080
}
```

**Response:** NDJSON stream of log events.

### Delete Service

```
DELETE /v1/sprites/{name}/services/{service_name}
```

Returns `204 No Content`.

### Start Service

```
POST /v1/sprites/{name}/services/{service_name}/start
```

**Query parameters:**

| Parameter  | Type   | Description                          |
|------------|--------|--------------------------------------|
| `duration` | string | Monitoring duration (e.g. `"30s"`)   |

**Response:** NDJSON stream of log events.

### Stop Service

```
POST /v1/sprites/{name}/services/{service_name}/stop
```

**Query parameters:**

| Parameter | Type   | Description                               |
|-----------|--------|-------------------------------------------|
| `timeout` | string | Timeout before force kill (e.g. `"30s"`)  |

**Response:** NDJSON stream of log events.

### Signal Service

```
POST /v1/sprites/{name}/services/signal
```

**Request body:**

```json
{
  "name": "string",
  "signal": "SIGTERM"
}
```

Returns `204 No Content`.

---

## Network Policy

### Get Network Policy

```
GET /v1/sprites/{name}/policy/network
```

**Response:**

```json
{
  "rules": [
    {
      "domain": "string",
      "action": "allow" | "deny",
      "include": "string"
    }
  ]
}
```

The `domain`/`action` and `include` fields are mutually exclusive within a
rule. Use `include` to reference a named policy set (e.g. `"defaults"`).

### Update Network Policy

```
POST /v1/sprites/{name}/policy/network
```

**Request body:** Same format as the GET response.

Returns `204 No Content`.

---

## NDJSON Stream Format

Several endpoints return newline-delimited JSON streams. Each line is a JSON
object with at least a `type` field:

```json
{"type": "stdout", "data": "...", "timestamp": 1234567890}
{"type": "stderr", "data": "...", "timestamp": 1234567890}
{"type": "exit", "exit_code": 0, "timestamp": 1234567890}
{"type": "error", "data": "...", "timestamp": 1234567890}
{"type": "complete", "timestamp": 1234567890}
{"type": "started", "timestamp": 1234567890}
{"type": "stopping", "timestamp": 1234567890}
{"type": "stopped", "timestamp": 1234567890}
```

Service log streams may also include a `log_files` object on `"complete"`
messages.

## Error Responses

| Status | Meaning                                        |
|--------|------------------------------------------------|
| 400    | Bad request                                    |
| 401    | Authentication failed                          |
| 404    | Resource not found                             |
| 409    | Conflict (e.g. service already running)        |
| 410    | Gone (e.g. session already exited)             |
| 429    | Rate limited (includes `Retry-After` header)   |

Rate-limited responses include these headers:

| Header                  | Description             |
|-------------------------|-------------------------|
| `Retry-After`           | Seconds to wait         |
| `X-RateLimit-Limit`     | Request limit           |
| `X-RateLimit-Remaining` | Remaining requests      |
| `X-RateLimit-Reset`     | Reset time              |

Error bodies may be JSON (`{"error": "...", "code": "..."}`) or plain text.
