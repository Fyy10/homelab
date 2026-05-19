# Backup

Back up configuration, data, and secrets with different expectations.

## Repository

The Git repository is the backup for Compose files, Caddy config, service
templates, scripts, and documentation.

## Application Data

Back up:

```text
/opt/homelab/data
```

This includes Caddy certificates, Authelia state, qBittorrent config,
Filebrowser database, and Jellyfin metadata.

## Secrets

Back up:

```text
/opt/homelab/secrets
```

Secrets should be encrypted before leaving the server.

## Media

Back up selected content from:

```text
/srv/media
```

Media can be large, so it may need a different retention policy than app data.
