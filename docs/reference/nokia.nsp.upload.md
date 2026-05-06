# Ansible Module: nokia.nsp.upload

**Upload files to Nokia NSP**

!!! note "Notes"

    Requires [ansible.netcommon.httpapi](https://docs.ansible.com/projects/ansible/latest/collections/ansible/netcommon/index.html) connection using Network OS [nokia.nsp.nsp](nokia.nsp.nsp.md).

## Synopsis

* Upload binary or text files to Nokia NSP servers.
* Uses NSP file-service endpoint for uploads.
* Handles single and multiple file uploads.

## Parameters

| Parameter | Type | Comments |
| --- | --- | --- |
| local_path {#param-local-path} | list | Path to local file(s) to upload.<br/>Can be a string for single file or list for batch uploads.<br/>File(s) must exist and be readable.<br/>**Required:** always |
| remote_path {#param-remote-path} | str | Remote directory on NSP file-service to upload files to.<br/>If this is a directory, filenames from `local_path` are used.<br/>**Required:** always |
| overwrite {#param-overwrite} | bool | Whether to overwrite existing files on NSP file-service.<br/>**Default:** `true` |

## Examples

```yaml
- name: Upload single file
  nokia.nsp.upload:
    local_path: /tmp/router.cfg
    remote_path: /nokia/nsp

# Upload multiple files
- name: Upload multiple files
  nokia.nsp.upload:
    local_path:
      - /tmp/test_upload_A.txt
      - /tmp/test_upload_B.txt
    remote_path: /nokia
```
## Return Values

| Parameter | Type | Comments |
| --- | --- | --- |
| local_path {#return-local-path} | str | Source file path<br/>**Returned:** always<br/>**Sample:** `"/tmp/workflow.json"` |
| remote_path {#return-remote-path} | str | Remote path or directory on NSP file-service<br/>**Returned:** always<br/>**Sample:** `"/workflows"` |
| remote_filename {#return-remote-filename} | str | Remote filename used for upload<br/>**Returned:** when local_path is a single file<br/>**Sample:** `"workflow.json"` |
| url {#return-url} | str | Upload endpoint URL (file-service)<br/>**Returned:** always<br/>**Sample:** `"/nsp-file-service-app/rest/api/v1/file/uploadFile?dirName=%2Fworkflows&overwrite=true"` |
| response {#return-response} | raw | Server response data<br/>**Returned:** always<br/>**Sample:** `{"status":"success"}` |
| results {#return-results} | list | List of per-file results when local_path is a list<br/>**Returned:** when local_path is a list<br/>**Sample:** `[]` |

*New in version "0.1.0"*
