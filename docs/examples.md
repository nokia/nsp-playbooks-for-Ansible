# Example Use Cases

!!! important "How Ansible and Nokia NSP Work Together"
    This Ansible Collection is designed to build advanced solutions that combine the capabilities of Ansible and Nokia NSP:

    - **NSP** acts as the network domain controller and single source of truth for network inventory, services, infrastructure, and higher-level intents. It enables network automation through programmable engines (Intent Manager, Workflow Manager, Operations Manager) and supporting infrastructure (Resource Manager).
    - **Ansible** adds orchestration, repeatability, integration with other systems (CI/CD, ticketing, cloud), and scriptable workflows across NSP and non-NSP resources.

This page outlines example use cases you can implement with the `nokia.nsp` collection and gives a high-level view of how to approach them. For concrete implementation, start with the [Developer Guide](guides/developer-guide.md) and [Reference](reference/index.md), and use the playbook examples included in the collection.

---

## Use case 1: Onboarding of network devices (Day 0)

### Goal

Add new network elements (e.g. SR OS or SRLinux) so they become NSP-managed.

### Approach

Devices must be reachable from the domain controller (NSP) and have a base configuration in place: system name, location, management protocols, and a management user. This example assumes Secure ZTP is not used, as it raises the bar for both management and network infrastructure. In-band vs out-of-band management is another choice: in-band avoids a dedicated DCN but complicates onboarding (at least one interface and IGP must be configured for reachability); out-of-band often only needs an IP and default route on the OOB interface.

You build:

* [ ] An inventory of the new devices. Use host/group variables for *day 0* configuration (device name, management IP, system IP, etc.)
* [ ] An Inventory with host/group variables for your NSP system(s) including host information, username, and password
* [ ] Multi-step playbook(s) that verifies reachability, applies *day 0* config via CLI actions (and TLS certs if needed), then uses this collection to create or update mediation and discovery policies in NSP, trigger discovery, and run post-discovery actions (e.g. create/update equipment and topology groups).

Structuring the playbook in two plays—one per device, one for controller operations—keeps concerns separate; delegation is an alternative. Include a step to validate NSP version first so the environment stays controlled.

---

## Use case 2: Automated NSP onboarding

### Goal

Automate NSP post-installation for lab, staging, or digital-twin environments: artifacts, discovery policies, telemetry subscriptions, equipment groups, and topology groups. The target is a consistent, repeatable environment for testing and validation.

### Approach

Start from a freshly installed NSP instance. Use a playbook with this collection to create or update discovery policies, telemetry subscriptions, equipment and topology groups, and to install CAM artifacts.

## Use case 3: CI/CD for workflow design

### Goal

Run automated validation of new NSP workflows against a staging environment before promoting them to production.

### Approach

Design workflows in Git and follow a GitOps process with peer review and maintainers approving merge requests (MRs). Use GitLab CI (or similar) to trigger validation and deployment automatically.

---

## Use case 4: CI/CD for intent-type design

### Goal

Apply the same GitOps and CI/CD pattern for intent-types: validate and test changes in staging, then promote to production with automated pipelines and peer review.

### Approach

Store intent-type definitions in Git; Use GitOps flow including peer review and merge requests, then a CI/CD pipeline that validates and deploys to staging (e.g. with `nokia.nsp.ibn`) and, after checks pass, promotes to production. Automation ensures consistency and traceability.

## Use case 5: Security audits

### Goal

Use NSP as a proxy to the network to audit security configuration, event logs, and security-related telemetry counters.

### Approach

Do not rely on NSP alone: use tools such as `nmap` to validate actual network device behavior. Run controlled security tests against network devices and confirm that expected security events are generated and visible in NSP.

---

## Use case 6: Reporting

### Goal

Query NSP inventory and operational data to feed reporting or downstream automation—for example, automatically creating Grafana dashboards for identified resources.

### Approach

Use this `nokia.nsp.rpc` or netcommon RESTCONF modules to query NSP’s inventory and operational data. Feed the results into your reporting stack—for example by generating config or API payloads for Grafana, a data lake, or other tools—or into downstream automation that reacts to current state. Playbooks can run on a schedule or be triggered by events to keep reports and dashboards up to date.
