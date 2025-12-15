#!/bin/bash
# Script to generate gophish config.json from environment variables
# This allows the domain to be changed without rebuilding the image

# Get admin domain from environment or use default
ADMIN_DOMAIN="${ADMIN_DOMAIN:-gophish.ryanworkdev.space}"

# Create data directory if it doesn't exist
mkdir -p /app/data

# Create symlinks to required files/directories so gophish can find them when running from /app/data
ln -sf /app/VERSION /app/data/VERSION 2>/dev/null || true
ln -sf /app/static /app/data/static 2>/dev/null || true
ln -sf /app/templates /app/data/templates 2>/dev/null || true
ln -sf /app/db /app/data/db 2>/dev/null || true

# Only create config if it doesn't exist (preserve existing data)
if [ ! -f /app/data/config.json ]; then
    cat > /app/data/config.json << EOF
{
  "admin_server": {
    "listen_url": "0.0.0.0:3333",
    "use_tls": false,
    "cert_path": "/app/data/gophish_admin.crt",
    "key_path": "/app/data/gophish_admin.key"
  },
  "phish_server": {
    "listen_url": "0.0.0.0:80",
    "use_tls": false,
    "cert_path": "/app/data/example.crt",
    "key_path": "/app/data/example.key"
  },
  "db_name": "sqlite3",
  "db_path": "/app/data/gophish.db",
  "migrations_prefix": "db/db_",
  "contact_address": "",
  "trusted_origins": ["https://${ADMIN_DOMAIN}"],
  "logging": {
    "filename": "",
    "level": "info"
  }
}
EOF
    echo "Generated config.json with admin domain: ${ADMIN_DOMAIN}"
else
    echo "config.json already exists, preserving existing configuration"
fi
