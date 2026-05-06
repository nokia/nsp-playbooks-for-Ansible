# Ansible Module: nokia.nsp.rest

**Execute NSP REST API calls**

!!! note "Notes"

    Requires [ansible.netcommon.httpapi](https://docs.ansible.com/projects/ansible/latest/collections/ansible/netcommon/index.html) connection using Network OS [nokia.nsp.nsp](nokia.nsp.nsp.md).

    Success is 2xx; 404 for DELETE is also considered success (resource already absent).

    For file operations use [nokia.nsp.upload](nokia.nsp.upload.md) and [nokia.nsp.download](nokia.nsp.download.md).

    Option [`dest`](#param-dest) handles text files only with UTF-8 encoding.

## Synopsis

* Execute REST API calls against Nokia NSP.
* Similar to [ansible.builtin.uri](https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/uri_module.html) but uses [ansible.netcommon.httpapi](https://docs.ansible.com/projects/ansible/latest/collections/ansible/netcommon/index.html) connection with Network OS [nokia.nsp.nsp](nokia.nsp.nsp.md).

## Parameters

| Parameter | Type | Comments |
| --- | --- | --- |
| path {#param-path} | str | REST API endpoint without base URL<br/>**Required:** always |
| method {#param-method} | str | HTTP method to use<br/>**Choices:** `GET`, `POST`, `PUT`, `DELETE`, `PATCH`<br/>**Default:** `GET` |
| body {#param-body} | raw | API request body<br/>Dict/list are serialized as JSON |
| dest {#param-dest} | path | Write response body content as file<br/>If file exists, will be overwritten<br/>For binary downloads use [nokia.nsp.download](nokia.nsp.download.md) |
| headers {#param-headers} | dict | This module automatically sets the authorization, content-type and accept headers.<br/>User can enforce content-type and accept headers by passing them in [`headers`](#param-headers).<br/>User may also pass additional headers as needed.<br/>If not set, `Accept` defaults to `application/json`<br/>If not set, `Content-Type` is inferred from [`body`](#param-body) to become either `application/json` or `text/plain`.<br/>**Default:** `{}` |
| timeout {#param-timeout} | int | Socket timeout in seconds<br/>**Default:** `30` |

## Examples

```yaml
- name: Execute WFM action via REST API
  nokia.nsp.rest:
    method: POST
    path: /wfm/api/v1/action-execution
    headers:
      Content-Type: application/json
      Accept: application/json
    body:
      name: nsp.ping
      examples: Default
      description: "Test ping action"
      input:
        host: localhost
        duration: 1
  register: result

- name: List files in NSP file storage
  nokia.nsp.rest:
    method: GET
    path: /nsp-file-service-app/rest/api/v1/directory?dirName=/nokia
  register: file_list
```
## Return Values

| Parameter | Type | Comments |
| --- | --- | --- |
| status {#return-status} | int | HTTP status code<br/>**Returned:** always |
| content {#return-content} | str | Response body content as string<br/>**Returned:** when server returns a response body |
| json {#return-json} | raw | Response body parsed as JSON<br/>**Returned:** when response is valid JSON |
| elapsed {#return-elapsed} | int | Seconds elapsed for the request<br/>**Returned:** always |
| path {#return-path} | str | Destination file path (if dest specified)<br/>**Returned:** when dest is specified |
| changed {#return-changed} | bool | Whether the request changed state<br/>**Returned:** always |
| headers {#return-headers} | dict | Response headers<br/>**Returned:** always |

*New in version "0.1.0"*
