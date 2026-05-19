# Adding a Service

Each service gets its own directory under `services/`.

## Checklist

1. Create `services/<service>/compose.yaml`.
2. Use a fixed image tag. Do not use `latest`.
3. Store app state in `${HOMELAB_DATA_DIR}/<service>`.
4. Store large files in `${MEDIA_DIR}` only when they are media or downloads.
5. Store secrets in `${HOMELAB_SECRETS_DIR}/<service>`.
6. Add the service to the `homelab_proxy` network if it needs web access.
7. Use `expose` for the internal web port.
8. Do not use `ports` for web access.
9. Add a Caddy site file in `services/caddy/config/sites/`.
10. Add `import authelia` for internal/admin services.

## Service README

Every service README should document:

- Public URL
- Data paths
- Secret paths
- Whether Authelia protects the service
- Any host ports the service intentionally exposes
