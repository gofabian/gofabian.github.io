#!/bin/sh

docker run \
  -p 127.0.0.1:4002:4004 \
  -e TWS_USERID \
  -e TWS_PASSWORD \
  -e READ_ONLY_API=no \
  -e TRADING_MODE=paper \
  --health-cmd "bash -c 'echo > /dev/tcp/127.0.0.1/4004' || exit 1" \
  --health-interval 5s \
  --health-timeout 2s \
  --health-retries 10 \
  ghcr.io/gnzsnz/ib-gateway:stable
