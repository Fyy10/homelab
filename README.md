# homelab

Container orchestration for a single-server personal homelab.

This repository keeps Docker Compose files, reverse proxy configuration,
service configuration, scripts, and documentation in Git. Runtime data,
secrets, downloads, and media libraries live outside the repository.

## Architecture

- Caddy is the only public web entry point.
- Homepage is served from the top-level domain and protected by Authelia.
- qBittorrent Enhanced Edition Web UI is protected by Authelia.
- Filebrowser is protected by Authelia.
- Jellyfin is not protected by Authelia, so mobile and TV clients can connect normally.
- Service web ports are not published to the host.
- qBittorrent publishes only its fixed BitTorrent listen port.
- All container images use fixed tags. Do not use `latest`.

See [docs/architecture.md](docs/architecture.md) for the full layout.

## Runtime Layout

Configure these paths in `.env`, then create the matching directories on the
server:

```text
${HOMELAB_DATA_DIR}/
    authelia/
    caddy/
      config/
      data/
    filebrowser/
      config/
    jellyfin/
      cache/
    qbittorrent/
${HOMELAB_SECRETS_DIR}/
    authelia/
$(dirname "$HOMELAB_DATA_DIR")/backups/

${MEDIA_DIR}/
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

After copying and editing `.env`, run:

```sh
set -a
. ./.env
set +a

sudo mkdir -p "$HOMELAB_DATA_DIR"/{authelia,caddy,filebrowser,jellyfin,qbittorrent}
sudo mkdir -p "$HOMELAB_DATA_DIR"/caddy/{config,data}
sudo mkdir -p "$HOMELAB_DATA_DIR"/jellyfin/cache
sudo mkdir -p "$HOMELAB_DATA_DIR"/filebrowser/config
sudo mkdir -p "$HOMELAB_SECRETS_DIR"/authelia
sudo mkdir -p "$(dirname "$HOMELAB_DATA_DIR")"/backups
sudo mkdir -p "$MEDIA_DIR"/downloads/{incomplete,complete}
sudo mkdir -p "$MEDIA_DIR"/library/{movies,tv,music}
```

Directories written by services that run as `${PUID}:${PGID}` must be writable
by that user and group:

```sh
set -a
. ./.env
set +a

sudo chown -R "$PUID:$PGID" "$HOMELAB_DATA_DIR"/filebrowser
sudo chown -R "$PUID:$PGID" "$HOMELAB_DATA_DIR"/qbittorrent
sudo chown -R "$PUID:$PGID" "$MEDIA_DIR"
```

## Quick Start

1. Create the shared proxy network:

   ```sh
   docker network create homelab_proxy
   ```

2. Copy and edit the environment file:

   ```sh
   cp .env.example .env
   ```

3. Create runtime directories:

   ```sh
   set -a
   . ./.env
   set +a

   sudo mkdir -p "$HOMELAB_DATA_DIR"/{authelia,caddy,filebrowser,jellyfin,qbittorrent}
   sudo mkdir -p "$HOMELAB_DATA_DIR"/caddy/{config,data}
   sudo mkdir -p "$HOMELAB_DATA_DIR"/jellyfin/cache
   sudo mkdir -p "$HOMELAB_DATA_DIR"/filebrowser/config
   sudo mkdir -p "$HOMELAB_SECRETS_DIR"/authelia
   sudo mkdir -p "$(dirname "$HOMELAB_DATA_DIR")"/backups
   sudo mkdir -p "$MEDIA_DIR"/downloads/{incomplete,complete}
   sudo mkdir -p "$MEDIA_DIR"/library/{movies,tv,music}
   sudo chown -R "$PUID:$PGID" "$HOMELAB_DATA_DIR"/filebrowser
   sudo chown -R "$PUID:$PGID" "$HOMELAB_DATA_DIR"/qbittorrent
   sudo chown -R "$PUID:$PGID" "$MEDIA_DIR"
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
- `qbit.example.com`: qBittorrent Enhanced Edition, protected by Authelia
- `files.example.com`: Filebrowser, protected by Authelia
- `jellyfin.example.com`: Jellyfin, protected by Jellyfin's own login

Replace `example.com` with your real domain in `.env`. Caddy and Authelia read
the domain from the same environment file.

## TODO

Service structure:

- [x] Caddy
- [x] Authelia
- [x] Homepage
- [x] qBittorrent
- [x] Filebrowser
- [x] Jellyfin
- [ ] Prowlarr
- [ ] Radarr
- [ ] Sonarr
- [ ] Bazarr
