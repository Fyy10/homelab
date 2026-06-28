# Jellyfin

Jellyfin is available through Caddy at `jellyfin.${DOMAIN}`.

It is not protected by Authelia because many mobile, TV, and media clients do
not handle forward-auth redirects well. Use Jellyfin's own user accounts,
strong passwords, and private libraries.

## Data

- App config: `/opt/homelab/data/jellyfin`
- MetaTube database: `/opt/homelab/data/jellyfin/plugin-servers/metatube/metatube.db`
- Media library: `/srv/media/library`
- Completed downloads: `/srv/media/downloads/complete`

The media mounts are read-only inside the container.

## MetaTube

The Compose stack includes an internal MetaTube service for Jellyfin plugin
access. It is only exposed on the Docker network at `metatube:8080`; Caddy does
not publish it directly.

MetaTube stores its SQLite database at:

```text
/opt/homelab/data/jellyfin/plugin-servers/metatube/metatube.db
```
