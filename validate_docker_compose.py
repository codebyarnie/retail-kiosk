#!/usr/bin/env python3
"""Validate docker-compose.yml configuration."""

import yaml
import sys

def validate_docker_compose():
    """Validate docker-compose configuration."""
    try:
        with open('docker-compose.yml', 'r') as f:
            config = yaml.safe_load(f)

        # Check services exist
        services = config.get('services', {})
        required_services = ['postgres', 'redis', 'qdrant']

        for service in required_services:
            if service not in services:
                print(f"✗ Missing required service: {service}")
                return False

        print(f"✓ All required services present: {', '.join(required_services)}")

        # Check healthchecks
        for service_name, service_config in services.items():
            if 'healthcheck' not in service_config:
                print(f"✗ Service {service_name} missing healthcheck")
                return False

        print("✓ All services have health checks configured")

        # Check volumes
        volumes = config.get('volumes', {})
        if len(volumes) < 3:
            print("✗ Not all volumes configured")
            return False

        print(f"✓ Volumes configured: {', '.join(volumes.keys())}")

        # Check networks
        networks = config.get('networks', {})
        if not networks:
            print("✗ No networks configured")
            return False

        print(f"✓ Networks configured: {', '.join(networks.keys())}")

        print("\nDocker compose configuration is valid")
        return True

    except yaml.YAMLError as e:
        print(f"✗ YAML parsing error: {e}")
        return False
    except Exception as e:
        print(f"✗ Validation error: {e}")
        return False

if __name__ == '__main__':
    success = validate_docker_compose()
    sys.exit(0 if success else 1)
