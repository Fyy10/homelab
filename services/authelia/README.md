# Authelia

Authelia provides forward authentication for internal web services.

## Setup

Create secret files on the server:

```sh
set -a
. ./.env
set +a

sudo mkdir -p "$HOMELAB_SECRETS_DIR"/authelia
openssl rand -hex 32 | sudo tee "$HOMELAB_SECRETS_DIR"/authelia/jwt_secret
openssl rand -hex 32 | sudo tee "$HOMELAB_SECRETS_DIR"/authelia/session_secret
openssl rand -hex 32 | sudo tee "$HOMELAB_SECRETS_DIR"/authelia/storage_encryption_key
sudo chmod 600 "$HOMELAB_SECRETS_DIR"/authelia/*
```

Create the real user database config:

```sh
cp services/authelia/config/users_database.yml.example services/authelia/config/users_database.yml
```

Generate a password hash:

```sh
docker run --rm authelia/authelia:4.39.20 authelia crypto hash generate argon2 --password 'change-me'
```

Replace the example hash in `users_database.yml`.

## Domain Configuration

Set `DOMAIN` in `.env`. Authelia renders `configuration.yml` with its template
filter, so the access rules and session cookie domain stay in sync with Caddy.

Please note that `session/cookies/authelia_url` cannot be the same as `session/cookies/default_redirection_url`.

## Protected Routes

- `https://${DOMAIN}`: Homepage

Authelia itself is available at `https://auth.${DOMAIN}` and is configured with
a bypass policy so login redirects work.
