#!/usr/bin/env python3
"""
Auto-generate Traefik routing rules for all phishing domains
Reads from .env and generates docker-compose label overrides
"""
import os
import re
from pathlib import Path

def load_env():
    """Load .env file and parse environment variables"""
    env_vars = {}
    env_file = Path('.env')
    
    if not env_file.exists():
        print("Error: .env file not found")
        return env_vars
    
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    
    return env_vars

def expand_variables(value, env_vars):
    """Expand ${VAR} references in values"""
    pattern = r'\$\{([^}]+)\}'
    
    def replace_var(match):
        var_name = match.group(1)
        return env_vars.get(var_name, match.group(0))
    
    return re.sub(pattern, replace_var, value)

def get_phish_domains(env_vars):
    """Extract all phishing domains (PHISH_DOMAIN, PHISH_DOMAIN_1, etc)"""
    domains = []
    
    # Add primary domain
    if 'PHISH_DOMAIN' in env_vars:
        domain = expand_variables(env_vars['PHISH_DOMAIN'], env_vars)
        domains.append(domain)
    
    # Add numbered domains
    i = 1
    while f'PHISH_DOMAIN_{i}' in env_vars:
        domain = expand_variables(env_vars[f'PHISH_DOMAIN_{i}'], env_vars)
        domains.append(domain)
        i += 1
    
    return domains

def generate_traefik_labels(domains):
    """Generate Traefik routing rules for all domains"""
    labels = []
    
    for idx, domain in enumerate(domains):
        # Use router name based on index
        router_name = f"gophish-phish-{idx}" if idx > 0 else "gophish-phish"
        
        # HTTP redirect
        labels.append(f'traefik.http.routers.{router_name}-http.entrypoints=http')
        labels.append(f'traefik.http.routers.{router_name}-http.rule=Host(`{domain}`)')
        labels.append(f'traefik.http.routers.{router_name}-http.middlewares=redirect-to-https')
        labels.append(f'traefik.http.routers.{router_name}-http.service=gophish-phish')
        
        # HTTPS router
        labels.append(f'traefik.http.routers.{router_name}.entrypoints=https')
        labels.append(f'traefik.http.routers.{router_name}.rule=Host(`{domain}`)')
        labels.append(f'traefik.http.routers.{router_name}.tls=true')
        labels.append(f'traefik.http.routers.{router_name}.tls.certresolver=letsencrypt')
        labels.append(f'traefik.http.routers.{router_name}.middlewares=gophish-headers')
        labels.append(f'traefik.http.routers.{router_name}.service=gophish-phish')
        
    return labels

def generate_docker_compose_override(labels):
    """Generate docker-compose.override.yml content"""
    yaml_content = """# ============================================
# AUTO-GENERATED: Phishing Domain Routes
# DO NOT EDIT MANUALLY
# Run: python3 generate_phish_routes.py
# ============================================

version: '3'

services:
  gophish:
    labels:
"""
    
    for label in labels:
        yaml_content += f'      - "{label}"\n'
    
    return yaml_content

def set_traefik_permissions():
    """Set correct file permissions for Traefik configuration files"""
    import stat
    
    files_permissions = {
        'traefik/acme.json': 0o600,      # -rw------- (only owner can read/write - SSL keys)
        'traefik/config.yml': 0o644,     # -rw-r--r-- (owner write, all read)
        'traefik/traefik.yml': 0o644,    # -rw-r--r-- (owner write, all read)
    }
    
    print("\n" + "="*70)
    print("🔒 SETTING FILE PERMISSIONS")
    print("="*70)
    
    for file_path, permission in files_permissions.items():
        path = Path(file_path)
        if path.exists():
            os.chmod(path, permission)
            # Get permission in octal format for display
            perm_str = oct(permission)[2:]
            print(f"  ✅ {file_path}: {perm_str}")
        else:
            print(f"  ⚠️  {file_path}: File not found, skipping")
    
    print("="*70)

def print_summary(domains):
    """Print configuration summary"""
    print("\n" + "="*70)
    print("✅ PHISHING DOMAINS CONFIGURED")
    print("="*70)
    
    for idx, domain in enumerate(domains, 1):
        print(f"  {idx}. {domain}")
    
    print("\n" + "="*70)
    print("📝 NEXT STEPS:")
    print("="*70)
    print("1. Verify domains in .env are correct:")
    print("   grep PHISH_DOMAIN .env")
    print("\n2. Rebuild containers:")
    print("   docker compose down")
    print("   docker compose up -d")
    print("\n3. Verify Traefik loaded routes:")
    print("   docker logs traefik | grep -i 'gophish-phish'")
    print("\n4. Test domains (after DNS is updated):")
    for domain in domains:
        print(f"   curl -k https://{domain}/login")
    print("="*70 + "\n")

def setup_directories():
    """Create necessary directories and files if they don't exist"""
    print("\n" + "="*70)
    print("📂 CHECKING DIRECTORIES")
    print("="*70)

    # 1. Create data directory
    data_dir = Path('data')
    if not data_dir.exists():
        try:
            data_dir.mkdir(exist_ok=True)
            # Try to set owner to 1000:1000 (standard docker user)
            # This might require sudo if current user is not owner
            os.chown(data_dir, 1000, 1000)
            print("  ✅ Created data directory")
        except PermissionError:
            print("  ⚠️  Created data directory but could not set ownership to 1000:1000")
            print("      (You may need to run: sudo chown -R 1000:1000 data)")
        except Exception as e:
            print(f"  ❌ Error creating data directory: {e}")
    else:
        print("  ✅ data directory exists")

    # 2. Create traefik/acme.json
    acme_file = Path('traefik/acme.json')
    if not acme_file.exists():
        try:
            acme_file.parent.mkdir(exist_ok=True)
            acme_file.write_text("{}")
            os.chmod(acme_file, 0o600)
            print("  ✅ Created traefik/acme.json")
        except Exception as e:
            print(f"  ❌ Error creating acme.json: {e}")
    else:
        print("  ✅ traefik/acme.json exists")

def configure_traefik_email(env_vars):
    """Inject ACME_EMAIL from .env into traefik.yml"""
    print("\n" + "="*70)
    print("📧 CONFIGURING TRAEFIK EMAIL")
    print("="*70)
    
    traefik_file = Path('traefik/traefik.yml')
    if not traefik_file.exists():
        print("  ❌ traefik/traefik.yml not found")
        return

    if 'ACME_EMAIL' not in env_vars:
        print("  ⚠️  ACME_EMAIL not found in .env, skipping")
        return

    email = env_vars['ACME_EMAIL']
    content = traefik_file.read_text()
    
    # Check if placeholder exists or if we need to update
    if 'your-email@example.com' in content:
        new_content = content.replace('your-email@example.com', email)
        traefik_file.write_text(new_content)
        print(f"  ✅ Updated traefik.yml with email: {email}")
    elif f'email: {email}' in content:
        print(f"  ✅ traefik.yml already configured with: {email}")
    else:
        # Fallback regex replacement if placeholder is missing but email is different
        import re
        new_content = re.sub(r'email: .*', f'email: {email}', content)
        if new_content != content:
            traefik_file.write_text(new_content)
            print(f"  ✅ Updated traefik.yml with email: {email}")
        else:
            print("  ✅ traefik.yml email is up to date")

if __name__ == '__main__':
    # Load .env
    env_vars = load_env()
    
    if not env_vars:
        print("Error: Could not load .env file")
        exit(1)
    
    # Setup directories first
    setup_directories()

    # Configure Traefik email
    configure_traefik_email(env_vars)

    # Set correct file permissions for Traefik files
    set_traefik_permissions()
    
    # Get phishing domains
    domains = get_phish_domains(env_vars)
    
    if not domains:
        print("Error: No PHISH_DOMAIN variables found in .env")
        exit(1)
    
    # Generate labels
    labels = generate_traefik_labels(domains)
    
    # Generate docker-compose.override.yml
    override_content = generate_docker_compose_override(labels)
    
    # Write to file
    output_file = Path('docker-compose.override.yml')
    output_file.write_text(override_content)
    print(f"✅ Generated: {output_file}")
    
    # Print summary
    print_summary(domains)
