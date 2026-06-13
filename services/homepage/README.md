# Homepage

Homepage provides the top-level homelab dashboard.

## Public URL

- `https://${DOMAIN}`

## Data Paths

- Config: `services/homepage/config`

Homepage is configured from repository-managed YAML files and does not require
a runtime data directory.

## Secrets

No service-specific secrets are required.

## Access Control

Homepage is protected by Authelia through Caddy forward authentication.

## Host Ports

No host ports are published. Caddy routes traffic to Homepage over the
`homelab_proxy` Docker network.

## Docker Status

Homepage mounts `/var/run/docker.sock` read-only so it can display container
status and stats. This gives the Homepage container visibility into Docker
metadata; keep the dashboard behind Authelia.
