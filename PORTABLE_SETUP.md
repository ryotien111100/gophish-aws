# 🎉 Portable Gophish Setup - Hoàn Thành!

## ✅ Tóm Tắt Thay Đổi

Gophish setup đã được cấu hình để **lưu toàn bộ data trong thư mục project**, giúp dễ dàng backup và migrate sang host khác.

---

## 📂 Cấu Trúc Thư Mục

```
gophish-prod/
├── data/                       # ← All persistent data here!
│   ├── gophish.db             # Database (campaigns, users, results)
│   ├── config.json            # Runtime config
│   ├── db/        (symlink)   # Database migrations
│   ├── static/    (symlink)   # Web assets
│   ├── templates/ (symlink)   # HTML templates
│   └── VERSION    (symlink)   # Version info
├── traefik/
│   ├── acme.json              # SSL certificates (auto-renewed)
│   ├── traefik.yml
│   └── config.yml
├── docker-compose.yml
├── docker-compose.override.yml
├── Dockerfile
├── .env
├── setup.py
├── deploy.sh
├── backup.sh                  # ← New backup script
└── .gitignore                 # ← Protect sensitive data

```

---

## 🔐 Login Credentials

**Admin Panel:** https://gophish.ryanworkdev.space

```
Username: admin
Password: a2e94a9a49ca3fe8
```

⚠️ **Đổi password ngay sau khi login lần đầu!**

---

## 💾 Backup & Migrate

### Cách 1: Sử dụng Script Tự Động

```bash
./backup.sh
# Tạo file: ~/backups/gophish-prod-backup-YYYYMMDD-HHMMSS.tar.gz
```

### Cách 2: Backup Thủ Công

```bash
# Dừng containers (recommended để database consistency)
docker compose down

# Tạo backup
cd /home/ryan
tar -czf gophish-prod-backup.tar.gz gophish-prod/

# Restart
cd gophish-prod
docker compose up -d
```

---

## 🚀 Restore Trên Host Mới

### Bước 1: Copy backup file

```bash
scp gophish-prod-backup.tar.gz user@newhost:~/
```

### Bước 2: Giải nén

```bash
tar -xzf gophish-prod-backup.tar.gz
cd gophish-prod
```

### Bước 3: Start containers

```bash
docker compose up -d
```

**That's it!** Tất cả data, SSL certs, configs đều được preserve:
- ✅ Phishing campaigns
- ✅ Landing pages
- ✅ Email templates
- ✅ Captured credentials
- ✅ SSL certificates
- ✅ User accounts

---

## 📊 Kiểm Tra Hệ Thống

### Check containers status

```bash
docker compose ps
```

### Check logs

```bash
# Gophish logs
docker compose logs gophish --tail 50

# Traefik logs
docker compose logs traefik --tail 50
```

### Check data directory

```bash
ls -lah data/
```

Output:
```
config.json      # Runtime config
gophish.db       # SQLite database (all your data)
db/              # Symlink to migrations
static/          # Symlink to web assets
templates/       # Symlink to HTML templates
VERSION          # Symlink to version info
```

---

## 🔧 Cách Hoạt Động

### Volume Mounting Strategy

**Before:**
```yaml
volumes:
  - gophish_data:/app   # ❌ Data in /var/lib/docker/volumes/
```

**After:**
```yaml
volumes:
  - ./data:/app/data    # ✅ Data in ./data/ (portable!)
```

### Symlink Magic

File `generate-config.sh` tạo symlinks từ `/app/data/` đến các thư mục cần thiết:

```bash
/app/data/
├── db/        -> /app/db        (from image)
├── static/    -> /app/static    (from image)
├── templates/ -> /app/templates (from image)
├── VERSION    -> /app/VERSION   (from image)
├── config.json     (persistent)
└── gophish.db      (persistent)
```

- **Read-only assets** (static, templates, db migrations) → symlink từ image
- **Writable data** (database, config) → lưu trong bind mount `./data/`

---

## 🎯 Use Cases

### 1. Development → Production

```bash
# Dev environment
cd ~/gophish-dev
docker compose up -d
# ... test campaigns ...

# Backup
tar -czf backup.tar.gz gophish-dev/

# Deploy to production
scp backup.tar.gz prod-server:~/
ssh prod-server
tar -xzf backup.tar.gz
cd gophish-dev
docker compose up -d
```

### 2. Server Migration

```bash
# Old server
docker compose down
tar -czf gophish-backup.tar.gz gophish-prod/

# New server
scp old-server:~/gophish-backup.tar.gz .
tar -xzf gophish-backup.tar.gz
cd gophish-prod
docker compose up -d
```

### 3. Disaster Recovery

```bash
# Regular backups (cron job)
0 2 * * * cd /home/ryan/gophish-prod && ./backup.sh

# Restore from backup
tar -xzf ~/backups/gophish-prod-backup-20251215-103000.tar.gz
cd gophish-prod
docker compose up -d
```

---

## 📝 Best Practices

### 1. Regular Backups

```bash
# Add to crontab
crontab -e

# Run backup daily at 2 AM
0 2 * * * cd /home/ryan/gophish-prod && ./backup.sh
```

### 2. Secure .env File

```bash
chmod 600 .env  # Only owner can read/write
```

### 3. SSL Certificate Backup

SSL certificates in `traefik/acme.json` are automatically backed up with the project folder.

### 4. Database Backup (Paranoid Mode)

```bash
# Extra database backup outside Docker
docker exec gophish sqlite3 /app/data/gophish.db ".backup '/tmp/backup.db'"
docker cp gophish:/tmp/backup.db ./gophish-$(date +%Y%m%d).db
```

---

## 🚨 Troubleshooting

### Container keeps restarting

```bash
docker compose logs gophish --tail 100
```

### Data not persisting

```bash
# Check mount
docker inspect gophish | grep Mounts -A 20

# Should see:
# "Source": "/home/ryan/gophish-prod/data"
# "Destination": "/app/data"
```

### Permission issues

```bash
# Fix data directory permissions
sudo chown -R 1000:1000 data/
```

---

## 🎓 Technical Details

### Why Symlinks?

Gophish expects this structure when running:
```
/app/
├── gophish        (binary)
├── config.json    (config)
├── gophish.db     (database)
├── static/        (web assets)
├── templates/     (HTML templates)
├── db/            (migrations)
└── VERSION        (version)
```

We mount `./data:/app/data` and use symlinks so:
- Binary stays in `/app/` (from Docker image)
- Data persists in `/app/data/` (bind mount to host)
- Gophish can access everything via symlinks

### Working Directory

Container runs with:
```bash
cd /app/data && /app/gophish
```

This way:
- `config.json` is in current directory (gophish finds it)
- Database writes to current directory (persisted in `./data/`)
- Symlinks make static/templates accessible

---

## 📖 Related Files Modified

1. **docker-compose.yml** - Changed volume mount to `./data:/app/data`
2. **Dockerfile** - Updated CMD to run from `/app/data` directory
3. **generate-config.sh** - Added symlink creation for required files/directories
4. **backup.sh** - New script for easy backups
5. **.gitignore** - Prevent committing sensitive data

---

## ✨ Benefits Summary

✅ **Portable**: Entire setup in one folder
✅ **Easy Backup**: `tar -czf` the whole directory
✅ **Easy Migrate**: Extract and run on new host
✅ **Version Control**: Can commit everything except data/
✅ **No Docker Volume**: No hidden data in `/var/lib/docker/volumes/`
✅ **Transparent**: Can inspect data directly in `./data/`

---

## 🔗 Quick Commands Reference

```bash
# Start
docker compose up -d

# Stop
docker compose down

# Logs
docker compose logs -f

# Rebuild
docker compose build gophish

# Backup
./backup.sh

# Status
docker compose ps

# Check data
ls -lah data/
```

---

**Created:** 2025-12-15
**Status:** ✅ Production Ready
