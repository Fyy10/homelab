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
    authelia/
    caddy/
    filebrowser/
    jellyfin/
      cache/
    qbittorrent/
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

## Service Data Directories

Create service data directories before the first `docker compose up`. This
prevents Docker from auto-creating missing bind mount source directories with a
UID/GID that does not match the service process.

For the default paths in `.env.example`:

```sh
sudo mkdir -p /opt/homelab/data/{authelia,caddy,filebrowser,jellyfin,qbittorrent}
sudo mkdir -p /opt/homelab/data/jellyfin/cache
sudo mkdir -p /opt/homelab/secrets
sudo mkdir -p /opt/homelab/backups
sudo mkdir -p /srv/media/downloads/{incomplete,complete}
sudo mkdir -p /srv/media/library/{movies,tv,music}
```

If `.env` uses different paths, create the same service subdirectories under
the configured `HOMELAB_DATA_DIR`, `HOMELAB_SECRETS_DIR`, and `MEDIA_DIR`.

Directories written by services that run as `${PUID}:${PGID}` must be writable
by that user and group. With the default `PUID=1000` and `PGID=1000`:

```sh
sudo chown -R 1000:1000 /opt/homelab/data/filebrowser
sudo chown -R 1000:1000 /opt/homelab/data/qbittorrent
sudo chown -R 1000:1000 /srv/media
```

## Quick Start

1. Create the shared proxy network:

   ```sh
   docker network create homelab_proxy
   ```

2. Create runtime directories:

   ```sh
   sudo mkdir -p /opt/homelab/data/{authelia,caddy,filebrowser,jellyfin,qbittorrent}
   sudo mkdir -p /opt/homelab/data/jellyfin/cache
   sudo mkdir -p /opt/homelab/secrets
   sudo mkdir -p /opt/homelab/backups
   sudo mkdir -p /srv/media/downloads/{incomplete,complete}
   sudo mkdir -p /srv/media/library/{movies,tv,music}
   sudo chown -R 1000:1000 /opt/homelab/data/filebrowser
   sudo chown -R 1000:1000 /opt/homelab/data/qbittorrent
   sudo chown -R 1000:1000 /srv/media
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
- `qbit.example.com`: qBittorrent Enhanced Edition, protected by Authelia
- `files.example.com`: Filebrowser, protected by Authelia
- `jellyfin.example.com`: Jellyfin, protected by Jellyfin's own login

Replace `example.com` with your real domain in `.env` and Authelia config.
