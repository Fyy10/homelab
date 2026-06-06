#!/usr/bin/env sh
set -eu

docker compose logs -f --tail=200 "$@"
