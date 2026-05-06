# Admin Guide

## Installation

!!! tip
    For detailed installation instructions, refer to the [Installation Guide](../getting-started/installation.md). This covers system requirements, virtual environment setup, and collection installation.

## Inventory Configuration

### Basic Setup

Create inventory file structure:

```bash
mkdir -p inventory/group_vars/nsp
mkdir -p inventory/host_vars
```

!!! note "inventory.yml"
    ```yaml
    ---
    all:
      children:
        nsp:
          vars:
            ansible_host: 192.168.1.100  # NSP server IP or hostname
            ansible_httpapi_port: 443    # NSP REST API port (default 443)
            ansible_user: admin          # NSP API username
            ansible_password: test123!   # NSP API user password
            ansible_connection: ansible.netcommon.httpapi
            ansible_network_os: nokia.nsp.nsp
    ```

!!! note "inventory/group_vars/nsp/default.yml"
    ```yaml
    ---
    # Connection settings
    ansible_httpapi_use_ssl: true
    ansible_httpapi_validate_certs: false
    ansible_httpapi_timeout: 30

    # Persistent connection settings
    ansible_persistent_command_timeout: 60
    ansible_persistent_connect_timeout: 30
    ```

!!! warning "Important"
    For TLS certificate validation and credential management (vault, environment variables), refer to the [Security Guide](security-guide.md).

### Multiple Environments

Manage separate NSP instances (production, staging, test):

!!! note "inventory.yml"
    ```yaml
    ---
    all:
      children:
        nsp_prod:
          hosts:
            nsp_prod_server:
              ansible_host: nsp-prod.example.com
              ansible_user: "..."
              ansible_password: "..."
        
        nsp_staging:
          hosts:
            nsp_staging_server:
              ansible_host: nsp-staging.example.com
              ansible_user: "..."
              ansible_password: "..."
    ```

## Ansible Configuration

!!! note "ansible.cfg"
    ```ini
    [defaults]
    # Collection paths
    collections_paths = ./collections:~/.ansible/collections

    # Inventory
    inventory = inventory.yml
    host_key_checking = False

    # Logging
    log_path = ./ansible.log
    verbosity = 1

    # Network defaults
    network_os = nokia.nsp.nsp
    connection = ansible.netcommon.httpapi

    [persistent_connection]
    # Timeouts (in seconds)
    connect_timeout = 30
    command_timeout = 60

    # Connection pooling
    proxy_commands = False
    ```

## Logging and Debugging

### Enable Ansible Logging

!!! note "ansible.cfg"
    ```ini
    [defaults]
    log_path = /var/log/ansible/nsp.log
    log_level = DEBUG
    ```

Create log directory:

```bash
sudo mkdir -p /var/log/ansible
sudo chmod 755 /var/log/ansible
```

### Monitor Logs

```bash
# View live logs
tail -f /var/log/ansible/nsp.log

# Search for errors
grep ERROR /var/log/ansible/nsp.log

# Search for authentication issues
grep -i auth /var/log/ansible/nsp.log

# View token generation
grep -i token /var/log/ansible/nsp.log
```

## Connection Timeouts

Configure timeouts based on NSP responsiveness. Use `connect_timeout` for TCP connection establishment and `command_timeout` for API response wait time. Both are configured in `ansible.cfg` under the `[persistent_connection]` section.

## Token Management

The bearer token has a 60-minute lifetime. Plan long-running operations accordingly while avoid long running tasks that exceed token lifetime. For long-running operations, consider breaking them into smaller playbooks or implementing token refresh logic in custom modules.

See [User Guide](user-guide.md) for more details on token lifetime and playbook planning.

## Performance Tuning

Parallel execution can be enabled by increasing the `forks` setting.
Connection pooling can be enabled via inventory variables:

!!! note "ansible.cfg"
    ```ini
    [defaults]
    forks = 5
    ```

!!! note "inventory/group_vars/nsp/default.yml"
    ```yaml
    ansible_httpapi_use_connection_pooling: true
    ```

## See Also

- [Security Guide](security-guide.md) - Secure credential and certificate management
- [User Guide](user-guide.md) - How users run playbooks
- [Developer Guide](developer-guide.md) - Playbook development patterns
