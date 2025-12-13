#!/bin/bash
# Script to generate gophish config.json from environment variables
# This allows the domain to be changed without rebuilding the image

# Get admin domain from environment or use default
ADMIN_DOMAIN="${ADMIN_DOMAIN:-gophish.ryanworkdev.space}"

# Only create config if it doesn't exist (preserve existing data)
if [ ! -f /app/config.json ]; then
    cat > /app/config.json << EOF
{
  "admin_server": {
    "listen_url": "0.0.0.0:3333",
    "use_tls": false,
    "cert_path": "gophish_admin.crt",
    "key_path": "gophish_admin.key"
  },
  "phish_server": {
    "listen_url": "0.0.0.0:80",
    "use_tls": false,
    "cert_path": "example.crt",
    "key_path": "example.key"
  },
  "db_name": "sqlite3",
  "db_path": "gophish.db",
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
