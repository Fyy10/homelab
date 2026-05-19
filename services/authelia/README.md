# Authelia

Authelia provides forward authentication for internal web services.

## Setup

Create secret files on the server:

```sh
sudo mkdir -p /opt/homelab/secrets/authelia
openssl rand -hex 32 | sudo tee /opt/homelab/secrets/authelia/jwt_secret
openssl rand -hex 32 | sudo tee /opt/homelab/secrets/authelia/session_secret
openssl rand -hex 32 | sudo tee /opt/homelab/secrets/authelia/storage_encryption_key
sudo chmod 600 /opt/homelab/secrets/authelia/*
```

Create the real user database:

```sh
cp services/authelia/config/users_database.yml.example services/authelia/config/users_database.yml
```

Generate a password hash:

```sh
docker run --rm authelia/authelia:4.38.10 authelia crypto hash generate argon2 --password 'change-me'
```

Replace the example hash in `users_database.yml`.

## Domain Configuration

Update `configuration.yml` and replace every `example.com` value with the real
domain. The Caddy config reads the domain from `.env`, but Authelia's policy
file is intentionally explicit so access rules are easy to audit.
