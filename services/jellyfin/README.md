# Jellyfin

Jellyfin is available through Caddy at `jellyfin.${DOMAIN}`.

It is not protected by Authelia because many mobile, TV, and media clients do
not handle forward-auth redirects well. Use Jellyfin's own user accounts,
strong passwords, and private libraries.

## Data

- App config: `/opt/homelab/data/jellyfin`
- Media library: `/srv/media/library`
- Completed downloads: `/srv/media/downloads/complete`

The media mounts are read-only inside the container.
