#!/usr/bin/env sh
set -eu

if ! docker network inspect homelab_proxy >/dev/null 2>&1; then
  docker network create homelab_proxy >/dev/null
fi

docker compose up -d
