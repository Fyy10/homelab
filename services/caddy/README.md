# Caddy

Caddy is the only public web entry point for this homelab.

## Public Ports

- `80/tcp`
- `443/tcp`
- `443/udp`

No application web service should publish its own host port. Route web traffic
through a site file in `config/sites/`.

## Adding a Site

Create a new file in `config/sites/`.

For internal/admin services, include Authelia:

```caddyfile
app.{$DOMAIN} {
  import security_headers
  import authelia
  reverse_proxy app:8080
}
```

For client-facing apps that do not work well with forward authentication, omit
the Authelia import and rely on the app's own authentication.
