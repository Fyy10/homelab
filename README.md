# homelab

Container orchestration for a single-server personal homelab.

This repository keeps Docker Compose files, reverse proxy configuration,
service configuration, scripts, and documentation in Git. Runtime data,
secrets, downloads, and media libraries live outside the repository.

## Architecture

- Caddy is the only public web entry point.
- Homepage is served from the top-level domain and protected by Authelia.
- qBittorrent Enhanced Edition Web UI uses its own authentication.
- Filebrowser uses its own authentication.
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
    authelia/
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
sudo mkdir -p /opt/homelab/secrets/authelia
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
   sudo mkdir -p /opt/homelab/secrets/authelia
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

## Automated Deployment

This repository includes a GitHub Actions workflow at
`.github/workflows/deploy.yml`. It is intentionally disabled by default. The
workflow only runs its deployment job when the repository variable
`HOMELAB_DEPLOY_ENABLED` is set to `true`.

The deployment model assumes the server keeps a persistent Git checkout and
stores runtime state outside that checkout:

```text
/opt/homelab/app      # Git checkout of this repository
/opt/homelab/data     # Container data
/opt/homelab/secrets  # Secret files
/opt/homelab/backups  # Backup output
/srv/media            # Downloads and media library
```

Prepare the server checkout once:

```sh
sudo mkdir -p /opt/homelab
sudo chown -R "$USER:$USER" /opt/homelab
git clone <repository-url> /opt/homelab/app
cd /opt/homelab/app
cp .env.example .env
```

Edit `/opt/homelab/app/.env`, create the runtime directories described above,
and configure Authelia secrets and users. The `.env` file and
`services/authelia/config/users_database.yml` are intentionally ignored by Git,
so deployments do not overwrite server-local secrets or users.

Configure these GitHub repository secrets:

- `HOMELAB_HOST`: server hostname or IP address
- `HOMELAB_USER`: SSH user used for deployment
- `HOMELAB_SSH_KEY`: private SSH key for that user
- `HOMELAB_SSH_PORT`: optional SSH port; defaults to `22`

When the server is ready, enable deployments by adding this GitHub repository
variable:

```text
HOMELAB_DEPLOY_ENABLED=true
```

Run the workflow manually from the GitHub Actions tab. The deployment job runs:

```sh
cd /opt/homelab/app
git fetch --prune origin
git reset --hard origin/main
docker compose config --quiet
docker compose pull
docker compose up -d --remove-orphans
docker image prune -f
```

To deploy automatically on pushes later, add a `push` trigger to
`.github/workflows/deploy.yml`.

## Services

- `example.com`: Homepage dashboard, protected by Authelia
- `auth.example.com`: Authelia
- `qbit.example.com`: qBittorrent Enhanced Edition, protected by qBittorrent's own login
- `files.example.com`: Filebrowser, protected by Filebrowser's own login
- `jellyfin.example.com`: Jellyfin, protected by Jellyfin's own login

Replace `example.com` with your real domain in `.env`. Caddy and Authelia read
the domain from the same environment file.
