# Quick Start

Get up and running with the Nokia NSP Ansible collection in 5 minutes.

!!! tip "Prerequisites"
    Before starting, ensure you have completed the [Installation](installation.md) guide with all dependencies installed and the collection ready to use.

## 1. Create Inventory File

Create Ansible inventory:

!!! note "inventory.yml"
    ```yaml
    ---
    all:
      hosts:
        nsp:
          ansible_host: 192.168.1.100  # NSP server IP or hostname
          ansible_httpapi_port: 443    # NSP REST API port (default 443)

          ansible_user: admin          # NSP API username
          ansible_password: test123!   # NSP API user password

          ansible_connection: ansible.netcommon.httpapi
          ansible_network_os: nokia.nsp.nsp

          ansible_httpapi_use_ssl: true
          ansible_httpapi_validate_certs: false
    ```

!!! warning "Important"
    In this example, the password is hardcoded as part of the NSP inventory and SSL certificate verification is disabled. **This is not recommended for production environments!** For secure practices, use Ansible Vault to encrypt sensitive data and enable SSL certificate validation. More information is found in the [Security Guide](../guides/security-guide.md).

## 2. Create Playbook

Create Ansible playbook:

!!! note "my_playbook.yml"
    ```yaml
    ---
    - name: NSP REST API Example
      hosts: nsp
      gather_facts: no

      tasks:
      - name: Get NSP equipment
        ansible.netcommon.restconf_get:
          path: "/restconf/data/nsp-equipment:network/network-element?fields=ne-id;ne-name;ip-address&include-meta=false"
        register: nsp_inventory

      - name: Display inventory
        debug:
          var: nsp_inventory
    ...
    ```

## 3. Run Playbook

```bash
ansible-playbook -i inventory.yml my_playbook.yml
```

## 4. View Results

!!! note "Output Example"
    ``` bash
    TASK [Query network elements] **
    ok: [nsp_server]

    TASK [Display results] **
    ok: [nsp_server] =>
    inventory.output:
        nsp-equipment:data:
        - ip-address: 192.168.1.101
            ne-id: "1034::cafe:1"
            ne-name: router1
        - ip-address: 192.168.1.102
            ne-id: "1034::cafe:2"
            ne-name: router2
    ```
