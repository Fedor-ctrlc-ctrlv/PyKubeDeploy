#!/usr/bin/env bash
set -euo pipefail

resolvectl dns enp0s3 1.1.1.1 8.8.8.8
resolvectl domain enp0s3 '~.'