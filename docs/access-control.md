# Access Control

Use Caddy and Authelia for services that behave like internal web applications.

## Protected by Authelia

- Homepage at `https://${DOMAIN}`

Protected services should not publish host web ports.

## Not Protected by Authelia

- Jellyfin
- qBittorrent Web UI
- Filebrowser

Jellyfin uses its own users and login flow. This keeps mobile, TV, and desktop
clients working without forward-auth redirect problems.

qBittorrent and Filebrowser also use their own web authentication in the current
stack configuration.

## Default Rule

When adding a new service:

- Protect admin dashboards with Authelia.
- Avoid forward authentication for apps with native clients, sync protocols, or
  special APIs unless those clients have been tested.
