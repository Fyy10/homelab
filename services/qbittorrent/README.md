# qBittorrent Enhanced Edition

The qBittorrent Web UI is not exposed directly to the host. It is available
through Caddy at `qb.example.com` and protected by Authelia.

The BitTorrent listen port is exposed directly so peers can connect:

- `${QBITTORRENT_PORT}/tcp`
- `${QBITTORRENT_PORT}/udp`

## Data

- App config: `/opt/homelab/data/qbittorrent`
- Downloads: `/srv/media/downloads`

Set qBittorrent's incomplete and completed download folders to:

- `/downloads/incomplete`
- `/downloads/complete`
