# Ansible Module: nokia.nsp.wfm

**Manage workflows in Nokia NSP**

!!! note "Notes"

    Requires [ansible.netcommon.httpapi](https://docs.ansible.com/projects/ansible/latest/collections/ansible/netcommon/index.html) connection using Network OS [nokia.nsp.nsp](nokia.nsp.nsp.md).

    Exactly one of [`upload`](#param-upload), [`define`](#param-define), [`execute`](#param-execute), or [`delete`](#param-delete) must be specified.

    Using check-mode workflows will be validated but not created/updated.

    Updates follow lifecycle: DRAFT → update → PUBLISHED.

    Creates follow lifecycle: create → PUBLISHED.

## Synopsis

* Create, update, delete, and execute workflows in Workflow Manager.
* Upload workflows from files or directories (with optional README and UI schemas).
* Create workflows from YAML definition.
* Execute workflows synchronously.

## Parameters

| Parameter | Type | Comments |
| --- | --- | --- |
| upload {#param-upload} | path | Create or updates a workflow.<br/>User provides either a file path or a directory path.<br/>If file is provided, it must be a valid YAML file.<br/>If directory is provided, it must contain exactly one `.yaml` or `.yml` file.<br/>Automatically transitions  lifecycle: DRAFT → PUBLISHED.<br/>Upload includes `README.md` and UI schema `.json` files if present.<br/>Mutually exclusive with [`define`](#param-define), [`execute`](#param-execute), or [`delete`](#param-delete). |
| define {#param-define} | str | Create or updates a workflow.<br/>Workflow definition is provided as YAML text.<br/>A compelete and valid workflow definition must be provided.<br/>Automatically transitions  lifecycle: DRAFT → PUBLISHED.<br/>Mutually exclusive with [`upload`](#param-upload), [`execute`](#param-execute), or [`delete`](#param-delete). |
| execute {#param-execute} | str | Execute a workflow synchronously.<br/>Workflow name or UUID to be provided.<br/>Returns execution result with state and output.<br/>Mutually exclusive with [`upload`](#param-upload), [`define`](#param-define), or [`delete`](#param-delete). |
| delete {#param-delete} | str | Deletes a workflow from NSP.<br/>Workflow name or UUID to be provided. |
| input {#param-input} | dict | Input parameters for workflow execution.<br/>Used if [`execute`](#param-execute) is used.<br/>**Default:** `{}` |

## Examples

```yaml
- name: Upload workflow from file
  nokia.nsp.wfm:
    upload: workflow.yaml

- name: Upload workflow from directory
  nokia.nsp.wfm:
    upload: /path/to/workflow_dir/

- name: Define workflow inline
  nokia.nsp.wfm:
    define: |
      ---
      version: '2.0'
      helloworld:
        description: Simple test workflow
        type: direct
        tags:
          - test
        input:
          - host: localhost
          - seconds: 1
        output:
          result: <% task("pingtask").result %>
        tasks:
          pingtask:
            action: nsp.ping
            input:
              host: <% $.host %>
              duration: <% $.seconds %>

- name: Execute workflow by name
  nokia.nsp.wfm:
    execute: helloworld
    input:
      host: localhost
      seconds: 5

- name: Execute workflow by UUID
  nokia.nsp.wfm:
    execute: "{{ workflow_id }}"
    input:
      host: localhost
      seconds: 5

- name: Delete workflow
  nokia.nsp.wfm:
    delete: my_workflow

- name: Complete CI/CD pipeline
  block:
    - name: Upload workflow
      nokia.nsp.wfm:
        upload: workflows/helloworld/helloworld.yaml
      register: wf

    - name: Execute workflow
      nokia.nsp.wfm:
        execute: "{{ wf.workflow_id }}"
        input:
          host: localhost
          seconds: 5

    - name: Cleanup workflow
      nokia.nsp.wfm:
        delete: "{{ wf.workflow_id }}"
```
## Return Values

| Parameter | Type | Comments |
| --- | --- | --- |
| workflow_id {#return-workflow-id} | str | UUID of the workflow<br/>**Returned:** success<br/>**Sample:** `a1b2c3d4-e5f6-7890-abcd-ef1234567890` |
| workflow_name {#return-workflow-name} | str | Name of the workflow<br/>**Returned:** success<br/>**Sample:** `my_workflow` |
| status {#return-status} | str | Workflow status<br/>**Returned:** when upload or define<br/>**Sample:** `PUBLISHED` |
| execution_id {#return-execution-id} | str | UUID of the execution<br/>**Returned:** when execute<br/>**Sample:** `f1e2d3c4-b5a6-7890-cdef-123456789abc` |
| state {#return-state} | str | Execution state<br/>**Returned:** when execute<br/>**Sample:** `SUCCESS` |
| output {#return-output} | dict | Workflow execution output<br/>**Returned:** when execute and completed |
| state_info {#return-state-info} | str | Execution state information or error details<br/>**Returned:** when execute |
| changed {#return-changed} | bool | Whether workflow was created, updated, or deleted<br/>**Returned:** always |
| msg {#return-msg} | str | Human-readable message describing the operation result<br/>**Returned:** always |

*New in version "0.1.0"*
