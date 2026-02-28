# KagiMCP Network Container

This repo builds a Docker image that runs `kagimcp` over network transport (`streamable-http` by default), not only local `stdio/uvx` usage.

## License and usage notes

- Upstream project [`kagisearch/kagimcp`](https://github.com/kagisearch/kagimcp) is MIT licensed.
- MIT generally allows creating and publishing derivative containers, including to Docker Hub.
- You still need to comply with Kagi API terms and keep `KAGI_API_KEY` private.
- This repository does not include Kagi source code directly; it installs from upstream at build time.

> Not legal advice. If your organization has compliance requirements, have counsel review your redistribution model.

## What this image provides

- `MCP_TRANSPORT=streamable-http` by default (recommended MCP network transport)
- Optional `MCP_TRANSPORT=sse`
- Optional `MCP_TRANSPORT=stdio` for compatibility
- Configurable host/port/path via env vars

## Runtime configuration

- `KAGI_API_KEY` (required for search/summarizer calls)
- `KAGI_SUMMARIZER_ENGINE` (optional; defaults upstream to `cecil`)
- `MCP_TRANSPORT` (`streamable-http` | `sse` | `stdio`)
- `MCP_HOST` (default: `0.0.0.0`)
- `MCP_PORT` (default: `8000`)
- `MCP_PATH` (default: `/mcp` for streamable-http, `/sse` for sse)

## Build locally

```bash
docker build -t ghcr.io/your-org/kagimcp-network:dev --build-arg KAGIMCP_REF=v0.1.4 .
```

## Run locally (network MCP)

```bash
docker run --rm -p 8000:8000 \\
  -e KAGI_API_KEY=YOUR_KEY \
  -e MCP_TRANSPORT=streamable-http \
  ghcr.io/your-org/kagimcp-network:dev
```

Then connect your MCP client to:

- `http://localhost:8000/mcp` for `streamable-http`
- `http://localhost:8000/sse` for `sse`

## GitHub Actions auto-publish

Workflow: `.github/workflows/docker-publish.yml`

Behavior:

- Runs every 6 hours.
- Checks latest upstream `kagisearch/kagimcp` tag.
- Rebuilds/pushes only when upstream tag changes.
- Publishes GHCR tags:
  - `latest`
  - `<upstream-tag>` (example `v0.1.4`)
- Commits updated `.upstream-version` after successful publish.

Required repository setting:

- Workflow permissions must allow `Read and write permissions` so the workflow can commit `.upstream-version`.

Authentication for image publish uses built-in `GITHUB_TOKEN`.

If the package appears private after first publish, set visibility to public in GitHub Packages settings.

Manual rebuild option:

- Run workflow dispatch and set `upstream_ref` (tag, branch, or commit SHA).

## Docker Compose

`docker-compose.yml` is included for local usage. It maps port `8000`, passes env vars, and uses a container healthcheck.

```bash
cp .env.example .env
docker compose up --build -d
docker compose ps
```

## Repo automation

- `dependabot.yml` watches:
  - GitHub Actions versions
  - Docker base image dependencies in `Dockerfile`
- `ci.yml` runs on push/PR and validates the image can build and become healthy.
- `security-scan.yml` runs Trivy filesystem and image vulnerability scans.
- `live-api-test.yml` runs a real MCP tool call (`kagi_search_fetch`) against Kagi API using repo secret `KAGI_API_KEY`.

### Live API test setup

- Add repository secret: `KAGI_API_KEY`
- Optional repository variable: `KAGI_LIVE_TEST_QUERY`
- Optional repository variable: `KAGI_LIVE_TEST_MODE` (`auto`, `search`, `summarizer`; default `auto`)
- Optional repository variable: `KAGI_LIVE_TEST_SUMMARY_URL` (default `https://www.kagi.com`)
- Trigger manually from Actions (`Live API Test`) or wait for weekly schedule.

In `auto` mode, the workflow tries `kagi_search_fetch` first and falls back to `kagi_summarizer` when Search API access is unauthorized.
