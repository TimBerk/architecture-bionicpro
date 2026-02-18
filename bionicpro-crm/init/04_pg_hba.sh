#!/usr/bin/env bash
set -euo pipefail

cat >> "$PGDATA/pg_hba.conf" <<'EOF'
# Debezium logical replication
host    replication     debezium        0.0.0.0/0       scram-sha-256
EOF
