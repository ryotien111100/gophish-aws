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
    print("\n" + "="*70 + "\n")

if __name__ == '__main__':
    # Load .env
    env_vars = load_env()
    
    if not env_vars:
        print("Error: Could not load .env file")
        exit(1)
    
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
