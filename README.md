# Gophish Phishing Framework

Simple phishing server with automatic multi-domain support.


## 🛠 Prerequisites

Run these commands to install Docker on Ubuntu:

```bash
# 1. Update and install dependencies
sudo apt update
sudo apt install apt-transport-https ca-certificates curl software-properties-common

# 2. Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 3. Add Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 4. Install Docker
sudo apt update
apt-cache policy docker-ce
sudo apt install docker-ce
```

## 📋 Quick Start

```bash
# 1. Edit domains in .env
nano .env

# 2. Generate Traefik routes
python3 setup.py

# 3. Start containers
docker compose up -d
```

Or use the shortcut:
```bash
./deploy.sh --restart
```

## 🔧 Configuration

### Adding Phishing Domains

Edit `.env` and add domains:

```properties
# Main phishing domain
PHISH_DOMAIN=phish.${DOMAIN}

# Additional domains (create as many as needed)
PHISH_DOMAIN_1=mail.${DOMAIN}
PHISH_DOMAIN_2=hrm.${DOMAIN}
PHISH_DOMAIN_3=secure.${DOMAIN}
```

Then run:
```bash
./deploy.sh --restart
```

### Changing Base Domain

```bash
# Edit .env
DOMAIN=newdomain.com

# All subdomains auto-update:
# - gophish.newdomain.com (admin panel)
# - phish.newdomain.com (phishing server)
# - traefik.newdomain.com (traefik dashboard)

# Restart
./deploy.sh --restart
```

## 📁 File Structure

```
gophish-prod/
├── .env                        # Configuration (edit this)
├── docker-compose.yml          # Services definition
├── docker-compose.override.yml  # Auto-generated routes (don't edit)
├── Dockerfile                  # Gophish build
├── setup.py                    # Route generator
├── deploy.sh                   # Deployment helper
├── generate-config.sh          # Runtime config generator
└── traefik/                    # Reverse proxy config
```

## 🚀 Deployment Workflow

```
1. Edit .env (add/remove PHISH_DOMAIN_*)
   ↓
2. Run: python3 setup.py (generates docker-compose.override.yml)
   ↓
3. Run: docker compose up -d (applies changes)
   ↓
4. Update DNS records (if adding new domains)
   ↓
5. Wait 2-3 minutes for SSL certificates
```

## 🔍 Verification

```bash
# Check configured domains
grep PHISH_DOMAIN .env

# Verify routes loaded
docker logs traefik | grep gophish-phish

# Test a domain
curl -k https://phish.yourdomain.com/login
```

## 💾 Data Persistence

All data (campaigns, landing pages, credentials) is stored in:
```
Docker volume: gophish-prod_gophish_data
```

Domain changes don't affect your data!

## 📌 Notes

- Admin panel: `https://gophish.yourdomain.com`
- Phishing server: `https://phish.yourdomain.com` (+ any extra domains)
- Traefik dashboard: `https://traefik.yourdomain.com`
- All traffic auto-upgrades to HTTPS
- SSL certificates auto-renewed via Let's Encrypt

## 🆘 Troubleshooting

**Domains not showing up?**
```bash
# Regenerate routes
python3 setup.py

# Check if generated correctly
cat docker-compose.override.yml

# Restart containers
docker compose down && docker compose up -d
```

**SSL certificate issues?**
```bash
# Check Traefik logs
docker logs traefik | tail -50
```

**Data lost after domain change?**
```bash
# Data is in Docker volume - check if volume exists
docker volume ls | grep gophish

# Restore volume if needed
# All data preserved in: gophish-prod_gophish_data
```
# gophish
