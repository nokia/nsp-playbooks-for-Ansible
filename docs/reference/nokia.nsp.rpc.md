# Ansible Module: nokia.nsp.rpc

**Execute RPC operations on Nokia NSP**

!!! note "Notes"

    Requires [ansible.netcommon.httpapi](https://docs.ansible.com/projects/ansible/latest/collections/ansible/netcommon/index.html) connection using Network OS [nokia.nsp.nsp](nokia.nsp.nsp.md).

    For resource-specific operations use [nokia.nsp.action](nokia.nsp.action.md) instead.

## Synopsis

* Execute global RESTCONF RPC operations on Nokia NSP.
* Uses [nokia.nsp.nsp](nokia.nsp.nsp.md) connection for client authentication.
* Global operations not tied to specific resource instances.
* Input parameters must match YANG RPC input structure.

## Parameters

| Parameter | Type | Comments |
| --- | --- | --- |
| operation {#param-operation} | str | RPC operation name with namespace prefix (e.g., nsp-inventory:find).<br/>**Required:** always |
| input {#param-input} | dict | Input parameters for the RPC operation.<br/>Must match YANG RPC input definition.<br/>**Default:** `{}` |

## Examples

```yaml
- name: Query network inventory
  nokia.nsp.rpc:
    operation: nsp-inventory:find
    input:
      xpath-filter: "/nsp-equipment:network/network-element"
      fields: "ne-id;ne-name;ip-address"
      include-meta: false
```
## Return Values

| Parameter | Type | Comments |
| --- | --- | --- |
| output {#return-output} | dict | Operation output from RESTCONF RPC call<br/>**Returned:** always<br/>**Sample:** `{"nsp-inventory:output":{"data":[],"total-count":0}}` |
| failed {#return-failed} | bool | Module execution failed<br/>**Returned:** always |
| changed {#return-changed} | bool | Operation caused change (always false for RPC queries)<br/>**Returned:** always |

*New in version "0.1.0"*
