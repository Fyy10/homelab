# Filebrowser

Filebrowser exposes `/srv/media` through a web UI. It is available through
Caddy at `files.${DOMAIN}` and protected by Filebrowser's own login.

## Data

- Database: `/opt/homelab/data/filebrowser/filebrowser.db`
- Browsed files: `/srv/media`

Do not expose Filebrowser with a host `ports` mapping.
