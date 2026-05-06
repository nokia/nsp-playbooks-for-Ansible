# Ansible Module: nokia.nsp.download

**Download files from Nokia NSP**

!!! note "Notes"

    Requires [ansible.netcommon.httpapi](https://docs.ansible.com/projects/ansible/latest/collections/ansible/netcommon/index.html) connection using Network OS [nokia.nsp.nsp](nokia.nsp.nsp.md).

## Synopsis

* Downloads binary or text files from Nokia NSP.
* Supports NSP file-service application and custom endpoints.
* Streams downloads to reduce memory usage for large files.
* Calculates MD5 checksum of downloaded files for verification.
* Handles both single and multiple file downloads.

## Parameters

| Parameter | Type | Comments |
| --- | --- | --- |
| url {#param-url} | str | Full URL of the resource to download.<br/>Path may include query parameters.<br/>Mutually exclusive with [`remote_path`](#param-remote-path). |
| remote_path {#param-remote-path} | list | Remote file path(s) on NSP file-service application<br/>Can be a string for single file or list for batch downloads.<br/>Mutually exclusive with [`url`](#param-url). |
| local_path {#param-local-path} | path | Local path where file will be saved.<br/>If this is a directory, filename from remote path is used.<br/>Parent directories are created automatically.<br/>**Required:** always |

## Examples

```yaml
- name: Download using file-service path
  nokia.nsp.download:
    remote_path: /nokia/nsp/cam/artifacts/bundle/my-bundle.zip
    local_path: /tmp

- name: Download using full URL
  nokia.nsp.download:
    url: /nsp-file-service-app/rest/api/v1/file/downloadFile?filePath=/nokia/nsp/cam/artifacts/bundle/my-bundle.zip
    local_path: /tmp/my-bundle.zip

- name: Download multiple files
  nokia.nsp.download:
    remote_path:
      - /nokia/test_upload_A.txt
      - /nokia/test_upload_B.txt
    local_path: /tmp/download/
```
## Return Values

| Parameter | Type | Comments |
| --- | --- | --- |
| remote_path {#return-remote-path} | str | Remote file path or URL downloaded<br/>**Returned:** always<br/>**Sample:** `"/nokia/nsp/cam/artifacts/bundle/file.zip"` |
| local_path {#return-local-path} | str | Local destination file path<br/>**Returned:** always<br/>**Sample:** `"/tmp/file.zip"` |
| file_size {#return-file-size} | int | Downloaded file size in bytes<br/>**Returned:** always<br/>**Sample:** `1048576` |
| checksum {#return-checksum} | str | MD5 checksum of downloaded file<br/>**Returned:** always<br/>**Sample:** `"d41d8cd98f00b204e9800998ecf8427e"` |
| results {#return-results} | list | List of per-file results when remote_path is a list<br/>**Returned:** when remote_path is a list<br/>**Sample:** `[]` |

*New in version "0.1.0"*
