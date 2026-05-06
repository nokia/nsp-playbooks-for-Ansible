# Ansible Module: nokia.nsp.version

**Check Nokia NSP version**

!!! note "Notes"

    Requires [ansible.netcommon.httpapi](https://docs.ansible.com/projects/ansible/latest/collections/ansible/netcommon/index.html) connection using Network OS [nokia.nsp.nsp](nokia.nsp.nsp.md).

    This module uses an undocumented internal API endpoint.

## Synopsis

* Retrieve the NSP system version via internal REST API endpoint.
* Supports version validation against minimum release requirements.

## Parameters

| Parameter | Type | Comments |
| --- | --- | --- |
| check {#param-check} | str | Optional minimum required version in `major.minor` format.<br/>Examples `25.11`, `24.11`, `23.11`<br/>If specified, fails if NSP version is lower than this value. |

## Examples

```yaml
- name: Get NSP version
  nokia.nsp.version:
  register: nsp_version

- name: Validate minimum NSP version
  nokia.nsp.version:
    check: "25.4"
  register: nsp_version
```
## Return Values

| Parameter | Type | Comments |
| --- | --- | --- |
| release {#return-release} | str | "NSP Release (example: NSP-CN-25.11.0-rel.302)"<br/>**Returned:** always |
| major {#return-major} | int | Major version number<br/>**Returned:** always |
| minor {#return-minor} | int | Minor version number<br/>**Returned:** always |

*New in version "0.1.0"*
