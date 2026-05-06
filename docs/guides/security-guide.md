# Security Guide

## Credential Protection

### Option 1: Ansible Vault for Secrets
  
Store sensitive credentials in encrypted Ansible Vault:

```bash
# Create vault for NSP credentials
mkdir -p group_vars/nsp
ansible-vault create group_vars/nsp/vault.yml
```

**Vault file structure:**

!!! note "group_vars/nsp/vault.yml"
    ```yaml
    vault_nsp_user: "api_automation"
    vault_nsp_password: "{{ secure_password }}"
    vault_nsp_client_id: "api_client_id"
    vault_nsp_client_secret: "{{ secret_key }}"
    ```

**Reference in inventory:**

!!! note "inventory.yml"
    ```yaml
    all:
      children:
        nsp:
          hosts:
            nsp_prod:
              ansible_host: nsp.example.com
              ansible_user: "{{ vault_nsp_user }}"
              ansible_password: "{{ vault_nsp_password }}"
              ansible_connection: httpapi
              ansible_network_os: nsp
    ```

**Running playbooks:**

```bash
# Prompt for vault password
ansible-playbook site.yml --ask-vault-pass

# Use vault password file (chmod 600)
chmod 600 ~/.vault_pass
ansible-playbook site.yml --vault-password-file ~/.vault_pass

# Use environment variable
export ANSIBLE_VAULT_PASSWORD_FILE=~/.vault_pass
ansible-playbook site.yml
```

**Vault best practices:**

- Store `.vault_pass` outside Git (add to `.gitignore`)
- Set file permissions to 600: `chmod 600 .vault_pass`
- Rotate vault passwords periodically
- Never commit vault passwords to version control
- Use separate vault files for different environments

### Option 2: Environment Variables for CI/CD

Pass credentials through CI/CD without storing in vault:

```bash
# In CI/CD pipeline (GitHub Actions, GitLab CI, etc.)
export ANSIBLE_HTTPAPI_USER="api_user"
export ANSIBLE_HTTPAPI_PASS="password"
export ANSIBLE_HTTPAPI_HOST="nsp.example.com"
```

**Using in playbook:**

!!! note "playbook.yml"
    ```yaml
    vars:
      ansible_user: "{{ lookup('env', 'ANSIBLE_HTTPAPI_USER') }}"
      ansible_password: "{{ lookup('env', 'ANSIBLE_HTTPAPI_PASS') }}"
      ansible_host: "{{ lookup('env', 'ANSIBLE_HTTPAPI_HOST') }}"
    ```

**CI/CD examples:**

!!! note "GitHub actions"
    ```yaml
    - name: Run playbook
      env:
        ANSIBLE_HTTPAPI_USER: ${{ secrets.NSP_API_USER }}
        ANSIBLE_HTTPAPI_PASS: ${{ secrets.NSP_API_PASS }}
      run: ansible-playbook site.yml
    ```

### Option 3: Interactive Password Prompts

Prompt users for sensitive input at runtime:

!!! note "playbook.yml"
    ```yaml
    - name: Get credentials
      hosts: localhost
      gather_facts: no
      
      vars_prompt:
        - name: nsp_username
          prompt: "NSP Username"
          private: no
        
        - name: nsp_password
          prompt: "NSP Password"
          private: yes
        
        - name: confirm_password
          prompt: "Confirm NSP Password"
          private: yes
      
      pre_tasks:
        - name: Validate passwords match
          assert:
            that:
              - nsp_password == confirm_password
            fail_msg: "Passwords do not match"
      
      roles:
        - nsp_operations
    ```

## TLS Certificate Management

Nokia NSP typically uses **self-signed certificates** by default. This requires special handling for secure communication. Disabling certificate validation is possible but not recommended for production environments.

!!! note "inventory/group_vars/nsp.yml"
    ```yaml
    ansible_httpapi_validate_certs: true
    ansible_httpapi_ca_certs: "/etc/ssl/certs/nsp_ca.pem"
    ```

The `ansible_httpapi_ca_certs` path should point to the CA certificate that signed the NSP server's certificate. This allows Ansible to validate the server's identity securely.

If public certificates are used, ensure that the CA is trusted by the system's certificate store, and `ansible_httpapi_validate_certs` can be set to `true` without specifying a custom CA path.

!!! danger "Security Risk"
    To disable validation, set `ansible_httpapi_validate_certs` to `false`. Disabling certificate validation is dangerous and should only be done in development or testing environments. Disables protection against man-in-the-middle attacks. 

## Security Compliance Checklist

**Credential Protection:**

- [ ] All credentials in vault or environment variables
- [ ] No passwords hardcoded in any files
- [ ] Vault password file outside version control
- [ ] Vault password file permissions: 600 (`chmod 600`)
- [ ] Inventory files restricted (mode 600 or vault-encrypted)
- [ ] No credentials in commit history (use `git-secrets` or similar)

**Certificate Management:**

- [ ] TLS validation enabled (`ansible_httpapi_validate_certs: true`)
- [ ] NSP CA certificate properly configured (or public CA used)
- [ ] Certificate expiration monitored (automation + alerts)

## See Also

- [User Guide](user-guide.md) - Operational security when running playbooks
- [Admin Guide](admin-guide.md) - Infrastructure setup and maintenance
- [Developer Guide](developer-guide.md) - Secure code practices in playbooks
