# Architecture

This homelab is designed for one public server that is easy for one person to
operate.

## Traffic Flow

```text
Internet
  |
  | 80/tcp, 443/tcp, 443/udp
  v
Caddy
  |
  | homelab_proxy
  v
Services
```

Caddy is the only public web entry point. Service web ports are only exposed on
the Docker network and are not published to the host.

## Access Control

Authelia protects Homepage at the top-level domain with forward authentication.
Homepage is the service dashboard for links and Docker container status.

Jellyfin is not protected by Authelia because native media clients need direct
access to Jellyfin's own login flow. qBittorrent and Filebrowser use their own
web login flows.

## Data Boundaries

The repository stores declarative configuration. Runtime state is outside the
repository:

- `/opt/homelab/data`: application state
- `/opt/homelab/secrets`: secrets
- `/srv/media`: downloads and media libraries

Homepage configuration is stored in the repository under
`services/homepage/config`; it does not have a separate runtime data directory.
