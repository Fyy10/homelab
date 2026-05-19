# Access Control

Use Caddy and Authelia for services that behave like internal web applications.

## Protected by Authelia

- qBittorrent Web UI
- Filebrowser

These services should not publish host web ports.

## Not Protected by Authelia

- Jellyfin

Jellyfin uses its own users and login flow. This keeps mobile, TV, and desktop
clients working without forward-auth redirect problems.

## Default Rule

When adding a new service:

- Protect admin dashboards with Authelia.
- Avoid forward authentication for apps with native clients, sync protocols, or
  special APIs unless those clients have been tested.
