# Ansible Module: nokia.nsp.action

**Execute actions on Nokia NSP RESTCONF resources**

!!! note "Notes"

    Requires [ansible.netcommon.httpapi](https://docs.ansible.com/projects/ansible/latest/collections/ansible/netcommon/index.html) connection using Network OS [nokia.nsp.nsp](nokia.nsp.nsp.md).

    For global operations use [nokia.nsp.rpc](nokia.nsp.rpc.md) instead.

    Resource path must URL-encode special characters properly.

## Synopsis

* Executes RESTCONF actions on Nokia NSP.
* Uses [nokia.nsp.nsp](nokia.nsp.nsp.md) connection for client authentication.
* Actions are bound to specific resource instances.

## Parameters

| Parameter | Type | Comments |
| --- | --- | --- |
| path {#param-path} | str | Reference data resource against the action is executed.<br/>RESTCONF compliant URI syntax must be used.<br/>Special characters must be URL-encoded.<br/>Namespace prefixes must be used appropriately.<br/>**Required:** always |
| operation {#param-operation} | str | Action name with optional namespace.<br/>**Required:** always |
| input {#param-input} | dict | Input parameters for the action.<br/>Must match YANG definition of the action.<br/>**Default:** `{}` |

## Examples

```yaml
- name: Audit intent configuration
  nokia.nsp.action:
    path: "ibn:ibn/intent={{ ne_id | urlencode }},{{ intent_name | urlencode }}"
    operation: audit

- name: Synchronize intent state
  nokia.nsp.action:
    path: "ibn:ibn/intent={{ ne_id | urlencode }},{{ intent_name | urlencode }}"
    operation: synchronize
```
## Return Values

| Parameter | Type | Comments |
| --- | --- | --- |
| output {#return-output} | dict | Operation output from RESTCONF resource action<br/>**Returned:** always<br/>**Sample:** `{"ibn:output":{"audit-report":{"intent-type":"helloworld","target":"1034::dead:beef:1"}}}` |
| failed {#return-failed} | bool | Module execution failed<br/>**Returned:** always |
| changed {#return-changed} | bool | Action caused resource change (action-dependent)<br/>**Returned:** always |

*New in version "0.1.0"*
