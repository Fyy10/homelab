#!/usr/bin/env sh
set -eu

if [ ! -f .env ]; then
  echo "Missing .env. Copy .env.example to .env and edit it."
  exit 1
fi

if ! docker network inspect homelab_proxy >/dev/null 2>&1; then
  echo "Missing Docker network: homelab_proxy"
  echo "Create it with: docker network create homelab_proxy"
  exit 1
fi

docker compose config >/dev/null
echo "Configuration looks valid."
