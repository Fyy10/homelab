# homelab

Container orchestration for a single-server personal homelab.

This repository keeps Docker Compose files, reverse proxy configuration,
service configuration, scripts, and documentation in Git. Runtime data,
secrets, downloads, and media libraries live outside the repository.

## Architecture

- Caddy is the only public web entry point.
- Authelia protects internal/admin web interfaces with forward authentication.
- qBittorrent Enhanced Edition Web UI is protected by Authelia.
- Filebrowser is protected by Authelia.
- Jellyfin is not protected by Authelia, so mobile and TV clients can connect normally.
- Service web ports are not published to the host.
- qBittorrent publishes only its fixed BitTorrent listen port.
- All container images use fixed tags. Do not use `latest`.

See [docs/architecture.md](docs/architecture.md) for the full layout.

## Runtime Layout

Create these directories on the server:

```text
/opt/homelab/
  data/
  secrets/
  backups/

/srv/media/
  downloads/
    incomplete/
    complete/
  library/
    movies/
    tv/
    music/
```

Copy `.env.example` to `.env` and edit the domain, timezone, user IDs, and paths.

## Quick Start

1. Create the shared proxy network:

   ```sh
   docker network create homelab_proxy
   ```

2. Create runtime directories:

   ```sh
   sudo mkdir -p /opt/homelab/{data,secrets,backups}
   sudo mkdir -p /srv/media/downloads/{incomplete,complete}
   sudo mkdir -p /srv/media/library/{movies,tv,music}
   ```

3. Copy the environment file:

   ```sh
   cp .env.example .env
   ```

4. Configure Authelia secrets and users. See [services/authelia/README.md](services/authelia/README.md).

5. Start the stack:

   ```sh
   ./scripts/up.sh
   ```

## Services

- `auth.example.com`: Authelia
- `qb.example.com`: qBittorrent Enhanced Edition, protected by Authelia
- `files.example.com`: Filebrowser, protected by Authelia
- `jellyfin.example.com`: Jellyfin, protected by Jellyfin's own login

Replace `example.com` with your real domain in `.env` and Authelia config.
