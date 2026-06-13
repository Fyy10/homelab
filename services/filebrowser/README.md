# Filebrowser

Filebrowser exposes `/srv/media` through a web UI. It is available through
Caddy at `files.${DOMAIN}` and protected by Authelia.

## Data

- Database: `/opt/homelab/data/filebrowser/filebrowser.db`
- Config: `/opt/homelab/data/filebrowser/config`
- Browsed files: `/srv/media`

Do not expose Filebrowser with a host `ports` mapping.
