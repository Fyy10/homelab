# Adding a Service

Each service gets its own directory under `services/`.

## Checklist

1. Create `services/<service>/compose.yaml`.
2. Use a fixed image tag. Do not use `latest`.
3. Store app state in `${HOMELAB_DATA_DIR}/<service>`.
4. Store large files in `${MEDIA_DIR}` only when they are media or downloads.
5. Store secrets in `${HOMELAB_SECRETS_DIR}/<service>`.
6. Document any required service data directory and ownership setup.
7. Add the service to the `homelab_proxy` network if it needs web access.
8. Use `expose` for the internal web port.
9. Do not use `ports` for web access.
10. Add a Caddy site file in `services/caddy/config/sites/`.
11. Add `import authelia` for internal/admin services.

## Service README

Every service README should document:

- Public URL
- Data paths
- Secret paths
- Whether Authelia protects the service
- Any host ports the service intentionally exposes
