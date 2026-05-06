# Developer Guide

This guide introduces how to write playbooks against Nokia NSP using the `nokia.nsp` collection. It is tutorial-style, compact, and focuses on patterns and best practices.

!!! tip "Before you start"
    Complete [Installation](../getting-started/installation.md) and [Quick Start](../getting-started/quick-start.md) so you have a working inventory and connection to NSP.

## 1. Your first NSP playbook

A minimal play targets NSP and uses the HTTPAPI connection. All `nokia.nsp` modules run on the controller (NSP), not on network elements.

```yaml
---
- name: My first NSP playbook
  hosts: nsp
  gather_facts: false

  tasks:
    - name: Get NSP version
      nokia.nsp.version:
      register: ver

    - name: Show version
      ansible.builtin.debug:
        msg: "NSP version: {{ ver.version }}"
```

Run it with your inventory: `ansible-playbook -i inventory.yml playbook.yml`.

## 2. Choosing the right module

| Goal | Module |
|------|--------|
| NSP version or version check | `nokia.nsp.version` |
| RESTCONF get/set (read, create, update, delete) | `ansible.netcommon.restconf_get`, `ansible.netcommon.restconf_config` |
| RESTCONF operations | `nokia.nsp.rpc`, `nokia.nsp.action` |
| Generic NSP REST | `nokia.nsp.rest` |
| Upload files to NSP | `nokia.nsp.upload` |
| Download files from NSP | `nokia.nsp.download` |
| Workflow definitions and runs | `nokia.nsp.wfm` |
| Intent-types and intents | `nokia.nsp.ibn` |

**RESTCONF get/set**

Use the netcommon modules (`restconf_get`, `restconf_config`) for reading and writing RESTCONF data on NSP. They are the recommended choice for any `/restconf/data/...`-style API.

**RESTCONF RPC and actions**

Use **`nokia.nsp.rpc`** for global YANG RPCs and **`nokia.nsp.action`** for YANG actions on a resource.

**Generic REST**

Use **`nokia.nsp.rest`** only for NSP REST resources that have **no RESTCONF** equivalent. That is mainly the case for WFM, CAM, file-service, and some administrative APIs.

## 3. Best practices

### Use variables for reuse

Define NSP paths, IDs, and options in group or host vars so playbooks stay readable and reusable.

```yaml
# group_vars/nsp.yml
nsp_equipment_path: "/restconf/data/nsp-equipment:network/network-element"
```

```yaml
- name: Get network elements (RESTCONF – use netcommon)
  ansible.netcommon.restconf_get:
    path: "{{ nsp_equipment_path }}?fields=ne-id;ne-name;ip-address&include-meta=false"
  register: ne_list
```

### Check NSP version when needed

If a playbook depends on a minimum NSP release, fail fast with the module’s `check` parameter, or run a task only when the version is high enough.
The module returns `release` (e.g. `NSP-CN-25.11.0-rel.302`), `major`, and `minor`.
Use the numeric fields for a reliable comparison:

```yaml
- name: Ensure NSP version
  nokia.nsp.version:
    check: "23.11"
  register: nsp_version

- name: Use newer REST API (e.g. WFM, CAM – no RESTCONF)
  nokia.nsp.rest:
    method: GET
    path: /some/new/api
  when: nsp_version.major > 24
```

### Idempotency

*Idempotency* here means: running the same playbook or task again produces the same outcome and does not create duplicates or unintended changes. Where the API supports it, design tasks so they are safe to re-run.

- **RESTCONF data:** Use `restconf_get` to read current state and `restconf_config` only when changes are needed, so runs are idempotent.
- **Workflows, intent-types, and intents:** The collection’s dedicated operations are designed for idempotent use. For example, adding an intent creates or updates it; uploading a workflow can update an existing one. Prefer these modules over raw REST when managing workflows and intents. The **workflow** module also supports **check mode** (e.g. validate workflow without publishing).

### Check mode, diff, and change reporting

!!! warning "Use with care"
    **Check mode** (`--check`), **diff mode** (`--diff`), and **change indication** (`changed: true/false`) are only supported by this collection in **very selective scenarios**. Do not blindly trust them for all tasks.

    Many NSP APIs (e.g. RPCs, actions, generic REST) do not report whether they would or did change state; check mode may only run the playbook flow without guaranteeing a real “no changes” simulation. Always validate playbooks in a development or lab environment and run regression in a staging environment before using them in production.

## 4. Iterating over devices while talking to NSP

A common pattern is: you have a list of devices (from inventory or from NSP), and you need to run tasks on NSP per device (e.g. configure something on each device via NSP’s RESTCONF proxy).
Ansible’s **task delegation** is the right tool.

### Pattern: device list in inventory, NSP does the work

Play targets your **devices** (or a group), but NSP-facing tasks are **delegated** to the NSP host. NSP uses device identity (e.g. `ne-id`) in the API path; the loop variable comes from the device list.

```yaml
---
- name: Configure devices via NSP
  hosts: my_devices
  gather_facts: false

  vars:
    # Map inventory hostname to NSP ne-id (could come from group_vars or dynamic source)
    ne_id_map:
      device_a: "1034::cafe:1"
      device_b: "1034::cafe:2"
    ne_id: "{{ ne_id_map[inventory_hostname] }}"

  tasks:
    - name: Apply config on device via NSP RESTCONF (use netcommon)
      ansible.netcommon.restconf_config:
        path: "/restconf/data/network-device-mgr:network-devices/network-device={{ ne_id }}/root/nokia-conf:/configure/system/name"
        method: put
        content: |
          {"nokia-conf:name": "{{ inventory_hostname }}"}
      delegate_to: nsp
      delegate_facts: false
```

Here, `hosts: my_devices` runs the task once per device; `delegate_to: nsp` runs the task on the NSP host so the `nokia.nsp.nsp` connection is used. The `path` and `body` use the current device’s `ne_id` and `inventory_hostname`.

### Pattern: device list from NSP, then operate per device

First fetch the list from NSP, then loop over it and delegate to NSP for each item.

```yaml
---
- name: Operate on each NSP-managed device
  hosts: nsp
  gather_facts: false

  tasks:
    - name: Get network elements from NSP (RESTCONF – use netcommon)
      ansible.netcommon.restconf_get:
        path: "/restconf/data/nsp-equipment:network/network-element?fields=ne-id;ne-name&include-meta=false"
      register: ne_response

    - name: Set list of ne-ids
      ansible.builtin.set_fact:
        ne_list: "{{ (ne_response.output | default({}))['nsp-equipment:data'] | default([]) | map(attribute='ne-id') | list }}"

    - name: Ensure config on each device via RESTCONF (use netcommon)
      ansible.netcommon.restconf_config:
        path: "/restconf/data/network-device-mgr:network-devices/network-device={{ item | urlencode }}/root/..."
        method: patch
        content: { ... }
      loop: "{{ ne_list }}"
      loop_control:
        label: "{{ item }}"
```

The play runs on NSP; the loop runs one REST call per `ne-id`. No need for `delegate_to` because the play is already targeting NSP.

### When to use which

- **Play targets devices, one task per device:** use `hosts: devices` and `delegate_to: nsp` so each device gets its own `ne_id`/vars and NSP executes the API call.
- **Play targets NSP, one task per item from NSP:** use `hosts: nsp` and `loop: "{{ ne_list }}"` (or similar) so all calls run on NSP with different `item` values.

## 5. Mixing NSP and local or other hosts

- **Run a task on the control node (e.g. create a file, run a script):** use `delegate_to: localhost` so the task runs on the machine running Ansible; the rest of the play can still target NSP.
- **Run a task on a specific NSP when you have multiple:** use `delegate_to: nsp_prod` (or the right host) so that task uses that host’s connection.
