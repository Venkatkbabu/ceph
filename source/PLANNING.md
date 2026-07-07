<u>**Storage - Ceph on OpenStack**</u>

• Total of 8 Nodes, for Multi Controller node setup Out of these 8 nodes

• 3 Nodes (Controller + Ceph)

• 1 Node (Dedicated for Ceph)

• 4 Nodes (Compute Nodes)

Total Configuration is as follows

• 4 nodes X 16 X 64

• 4nodes X 16 X 96 = 4 TB = 6 TB

# Planning

## 1. Executive Summary

[**<u>CEPH :</u>**](https://docs.ceph.com/en/latest/start/)

Ceph is the foundational storage layer for this entire OpenStack
deployment. Rather than each OpenStack service (Cinder, Glance, Nova,
Manila) managing its own independent, siloed storage backend, this
architecture consolidates all persistent and semi-persistent storage
needs onto a single distributed Ceph cluster running across 4 of the 8
physical nodes. This is not a peripheral component — it is the layer
that determines whether the cluster's core business requirements (high
availability, no single point of failure, live migration without
downtime, disaster recovery) are actually achievable, and it should be
reviewed with that weight in mind.

Every virtual machine's boot image, every attached block volume, every
snapshot, and — if brought into scope - every object stored via
S3/Swift-compatible access and every shared file-system mount,
ultimately lives on Ceph. This means Ceph's design decisions
(replication factor, failure domain, node count, network segmentation)
directly bound what the entire OpenStack cluster can promise its users,
regardless of how well the compute or networking layers are designed.

**Role:** Ceph has no single storage controller or storage node that all
I/O must pass through. Data is spread (via the CRUSH algorithm) across
every OSD host in the cluster, so read and write load is naturally
balanced rather than bottle necked on one appliance. This directly
serves the business requirement of no single point of failure - a
requirement that a traditional single-controller SAN or a single NFS
filer cannot meet without expensive external clustering.

**Why Ceph:** Compared to alternatives such as LVM/local storage,
dedicated SAN, or ZFS, Ceph provides distributed replication that
eliminates single points of failure. It scales horizontally by adding
OSD nodes (or disks) without forklift upgrades and offers the tightest
native integration with OpenStack deployment tools like Kolla-Ansible,
aligning with standard reference architectures.

Integration Points:

- RBD for high-performance block storage (Cinder, Glance, Nova).

- RGW for S3 and Swift-compatible object storage.

- CephFS for shared filesystem needs (supporting NAS-style access where
  > required).

- External iSCSI and NAS gateways for integration with pre-existing
  > enterprise storage systems.

This cluster consists of 3 Controller + Ceph nodes, 1 dedicated Ceph
node, and 4 Compute nodes, providing 3x-replicated block, image, and
object storage with documented tolerance for a single-node failure.

### 1.1. Methodology

a **hybrid** - waterfall-style phased gates for the physical build (you
can't skip procurement), IaC/DevOps for everything
configuration-related, and SRE principles once you're live. Don't force
pure Agile sprints onto hardware delivery, and don't force pure
Waterfall onto ongoing operations.

### 1.2. Technology Stack

| **Layer**                | **Choice**                                                                        | **Why**                                                                                                   |
|-------------------------|-----------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------|
| OS                      | Ubuntu 24.04 LTS or Rocky/RHEL 9.x                                                | both have solid cephadm support                                                                         |
| Ceph                    | **Squid 19.2.x**                                                                  | It is an actively maintained stable branch, widely deployed, and receives backports and security fixes. |
| Deployment              | **cephadm**                                                                       | Ceph's own orchestrator — built-in dashboard, container-based, easiest day-2 lifecycle management       |
| OpenStack               | **2026.1 "Gazpacho"** via Kolla-Ansible or OpenStack-Ansible                      | Current release series; both integrate cleanly with external Ceph via RBD                               |
| Monitoring              | Prometheus + Grafana + Alertmanager (cephadm-managed)                             | Ships built-in with cephadm, no separate stack to maintain                                              |
| Logging                 | Loki or ELK/OpenSearch                                                            | Centralized log aggregation across 8 nodes — don't rely on SSH-and-grep during an incident              |
| Config management / IaC | Ansible (+ git)                                                                   | Industry standard for both Ceph and OpenStack node config; text-based, reviewable                       |
| Version control         | Git                                                                               | keep configs, runbooks, and diagrams versioned together                                                 |
| Backup                  | RBD snapshots + a real backup target (not just Ceph replication)                  | Replication protects against hardware failure, not accidental deletion or site loss                     |
| Benchmarking            | rados bench, rbd bench, fio (inside test VMs)                                     | Standard Ceph-native and application-level benchmarking tools                                           |
| Security                | CephX (default), dm-crypt at-rest encryption, TLS/msgr2 in transit                | Built into Ceph, low operational overhead to enable at cluster-creation time                            |
| Network                 | 25 GbE preferred (10 GbE minimum), separate public/cluster networks, LACP bonding | Matches DB-heavy workload's latency sensitivity                                                         |
| Virtualization          | KVM/QEMU (via Nova)                                                               | Standard OpenStack hypervisor                                                                           |
