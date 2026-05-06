# Ansible Module: nokia.nsp.ibn

**Execute create, update, and delete operations on Nokia NSP's Intent Manager application.**

!!! note "Notes"

    Requires [ansible.netcommon.httpapi](https://docs.ansible.com/projects/ansible/latest/collections/ansible/netcommon/index.html) connection using Network OS [nokia.nsp.nsp](nokia.nsp.nsp.md).

## Synopsis

* Create, update and delete intent-types in the intent-type catalog.
* Add, update and delete intent instances.

## Parameters

| Parameter | Type | Comments |
| --- | --- | --- |
| operation {#param-operation} | str | The operation to perform on NSP's Intent Manager application<br/>**Choices:** `upload_intent_type`, `add_intent`, `delete_intent`, `delete_intent_type`<br/>**Required:** always |
| path {#param-path} | path | Path to the filesystem folder containing the intent-type to be uploaded.<br/>Required if [`operation`](#param-operation)=`upload_intent_type`. |
| intent_type {#param-intent-type} | str | Name of the intent-type.<br/>Required if [`operation`](#param-operation) is `add_intent`, `delete_intent`, or `delete_intent_type`. |
| version {#param-version} | int | Version of the intent-type.<br/>Required if [`operation`](#param-operation) is `add_intent` or `delete_intent_type`. |
| target {#param-target} | str | Intent target acting as unique identifier in the realm of the intent-type.<br/>Might be a composition of target compontents.<br/>For required syntax, check intent-type `meta-info.json`. |
| config {#param-config} | dict | Intent configuration (instance of the intent-type YANG model).<br/>Required if [`operation`](#param-operation)=`add_intent`. |
| desired_state {#param-desired-state} | str | Desired network state for the intent.<br/>Used if [`operation`](#param-operation)=`add_intent`.<br/>**Choices:** `active`, `suspend`, `delete`<br/>**Default:** `active` |
| perform {#param-perform} | str | Allows to run an intent operation immediately after intent is created or updated.<br/>If omitted, the intent is only created/updated and no operation is triggered.<br/>Used if [`operation`](#param-operation)=`add_intent`.<br/>**Choices:** `audit`, `synchronize` |
| remove_from_network {#param-remove-from-network} | bool | By default, intents are deleted from the controller (NSP) only keeping the network configuration as is.<br/>To remove the intent from the controller and the network, this option must be set to `true`.<br/>Used if [`operation`](#param-operation)=`delete_intent`.<br/>**Default:** `false` |
| force {#param-force} | bool | By default, only the intent-type is removed from the controller (NSP).<br/>If intents for the corresponding intent-type version are present, deletion will fail.<br/>To force deletion of the intent-type together with all intents, this option must be set to `true`.<br/>Used if [`operation`](#param-operation)=`delete_intent_type`.<br/>**Default:** `false` |

## Examples

```yaml
- name: Upload intent-type
  nokia.nsp.ibn:
    operation: upload_intent_type
    path: /path/to/intent_types/iplink
  register: upload_result

- name: Add or update intent (then synchronize)
  nokia.nsp.ibn:
    operation: add_intent
    intent_type: "{{ upload_result.intent_type }}"
    version: "{{ upload_result.version }}"
    target: cid001
    config:
      "iplink:iplink":
        description: "Madrid / Barcelona"
        admin-state: enable
        endpoint-a:
          ne-id: "1034::cafe:1"
          port-id: "1/1/c1/1"
        endpoint-b:
          ne-id: "1034::cafe:2"
          port-id: "1/1/c1/1"
    desired_state: active
    perform: synchronize
  register: add_intent_result

- name: Delete intent (remove from network then controller)
  nokia.nsp.ibn:
    operation: delete_intent
    target: cid001
    intent_type: iplink
    remove_from_network: true

- name: Delete intent-type
  nokia.nsp.ibn:
    operation: delete_intent_type
    intent_type: iplink
    version: 1
    force: true
```
## Return Values

| Parameter | Type | Comments |
| --- | --- | --- |
| intent_type {#return-intent-type} | str | Intent-type name<br/>**Returned:** upload_intent_type, add_intent, delete_intent, delete_intent_type |
| version {#return-version} | int | Intent-type version<br/>**Returned:** upload_intent_type, add_intent, delete_intent_type |
| target {#return-target} | str | Intent target<br/>**Returned:** add_intent, delete_intent |
| changed {#return-changed} | bool | True when something was created, updated, or deleted<br/>**Returned:** always |
| msg {#return-msg} | str | Human-readable result message<br/>**Returned:** always |
| audit_result {#return-audit-result} | dict | Output of audit when *perform*=audit<br/>**Returned:** add_intent with perform=audit |
| sync_result {#return-sync-result} | dict | Output of synchronize when *perform*=synchronize<br/>**Returned:** [`operation`](#param-operation)=`add_intent` with [`perform`](#param-perform)=`synchronize` |

*New in version "0.1.0"*
