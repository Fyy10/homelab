# qBittorrent Enhanced Edition

The qBittorrent Web UI is not exposed directly to the host. It is available
through Caddy at `qbit.${DOMAIN}` and protected by Authelia.

Since it is protected by Authelia, you may want to add Caddy's IP/subnet to qBittorrent's whitelist to avoid double-auth.

Use the following command to look for Caddy's IP/subnet:

```bash
docker network inspect homelab_proxy
# look for 172.18.0.x/16 in container name caddy
```

The BitTorrent listen port is exposed directly so peers can connect:

- `${QBITTORRENT_PORT}/tcp`
- `${QBITTORRENT_PORT}/udp`

## Data

- App config: `/opt/homelab/data/qbittorrent`
- Downloads: `/srv/media/downloads`

Set qBittorrent's incomplete and completed download folders to:

- `/srv/data/downloads/incomplete`
- `/srv/data/downloads/complete`
