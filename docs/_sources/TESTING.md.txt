# Testing

## 7. High Availability & Resilience

### 7.1 Design Overview

This section documents the failure scenarios the cluster is designed to
tolerate, the mechanisms providing that tolerance, and the failure
scenarios it does not tolerate given the current 8-node topology. Both
are presented together deliberately, so the document's HA claims are
bounded and testable rather than open-ended.

### 7.2 Failure Scenario Matrix

| **Failure Scenario** | **Detection Method** | **Cluster Response** | **Outcome** |
|--------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------|
| **Single OSD (Disk) Failure**                                            | Ceph marks OSD **down** after heartbeat timeout                                                                                      | Affected PGs re-replicated from surviving copies on other hosts                                                                                             | HEALTH_WARN → self-heals to HEALTH_OK; no data loss                                                                                  |
| **Single Ceph Storage Node Failure (Node 1, Node 2, Node 3, or Node 4)** | MON detects host unreachable; all OSDs on that host marked **down**                                                                  | CRUSH redistributes affected PGs across remaining 3 hosts                                                                                                   | Tolerated — no data loss, per host-level CRUSH failure domain                                                                        |
| **Single Monitor (MON) Failure**                                         | Remaining MONs detect quorum member loss                                                                                             | Cluster continues with 2 of 3 MONs                                                                                                                          | Tolerated — quorum maintained; 3rd MON must be restored before risking a 2nd failure                                                 |
| **Active Manager (MGR) Failure**                                         | Standby detects active MGR lease expiry                                                                                              | Standby promotes to active automatically                                                                                                                    | Tolerated — brief metrics/dashboard gap only, no I/O impact                                                                          |
| **RabbitMQ Node Failure**                                                | Cluster membership monitoring                                                                                                        | Remaining nodes continue serving RPC                                                                                                                        | Tolerated                                                                                                                            |
| **Galera Database Node Failure**                                         | Galera cluster membership monitoring                                                                                                 | Remaining nodes continue serving reads/writes                                                                                                               | Tolerated, provided quorum (2 of 3) maintained                                                                                       |
| **Second Concurrent Ceph Storage Node Failure**                          | The cluster detects that multiple storage nodes have become unavailable while recovery from a previous failure is still in progress. | Ceph cannot maintain the configured replication policy because the remaining number of storage nodes is insufficient for valid three-way replica placement. | Not tolerated — only 1 host of margin exists beyond the minimum required for valid replica placement at 4 hosts/3x replication       |
| **Planned Maintenance During an Existing Node Failure**                  | A storage node is intentionally placed into maintenance mode while another storage node is already unavailable.                      | The cluster attempts to rebalance data; however, the available storage nodes are insufficient to maintain the required replication level.                   | Not tolerated — same root constraint; taking a node offline for maintenance consumes the same margin an unplanned failure would need |

### 7.3 Replication and Data Protection

| **Mechanism**                       | **Configuration**            | **Protects Against**                                             |
|-------------------------------------|------------------------------|------------------------------------------------------------------|
| **Synchronous 3× Replicatio**n      | size = 3, min_size = 2       | Disk failure, host failure, silent single-copy corruption        |
| **Host-level CRUSH Failure Domain** | 4-host topology              | Replica co-location on the same physical host                    |
| **RBD Snapshots**                   | Point-in-time, copy-on-write | Logical errors, accidental changes — not a substitute for backup |

Replication protects against hardware failure. It does not protect
against accidental deletion or logical corruption, since those changes
replicate just as faithfully as legitimate writes — this is why backup
is treated as a separate requirement below.

### 7.4 Backup Strategy

| **Requirement**                                   | **Design**                                                                                                                                                    |
|---------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Independent Failure Domain from Primary Pools** | A dedicated **backups** pool is used separately from the **volumes** and **images** pools to logically isolate backup data from primary production workloads. |
| **Backup Method**                                 | OpenStack **Cinder** **Backup** service is used to create and manage backups of persistent block volumes stored within the Ceph cluster.                      |
| **Recovery Point Objective (RPO)**                | **Not yet specified**                                                                                                                                         |
| **Recovery Time Objective (RTO)**                 | **Not yet specified**                                                                                                                                         |

**Open item:** the backups pool currently resides in the same 4-host
cluster as primary data. This protects against accidental deletion or
logical error, but not against a full-cluster/site-level event. Whether
site-level disaster recovery is a requirement - and therefore whether an
off-cluster or second-site backup target is needed - should be confirmed
with stakeholders.

### 7.5 High Availability Testing Plan

1.  Simulate single OSD failure - confirm recovery, HEALTH_OK
    > restoration, no client I/O errors.

2.  Simulate single OSD host failure - confirm rebalancing, confirm
    > Cinder/Glance/Nova continuity.

3.  Simulate single MON failure - confirm quorum maintained with 2 of 3.

4.  Simulate active MGR failure - confirm standby promotion.

5.  Simulate RabbitMQ and Galera node failures independently - confirm
    > OpenStack API availability.

6.  Attempt a second concurrent failure during Test 2's recovery
    > window - expected to demonstrate the documented limitation; run
    > deliberately so it is evidenced, not just asserted.

7.  Perform a full backup-and-restore cycle - validate actual recovery,
    > not just backup job completion.

### 7.6 Multi-Site & Disaster Recovery Extensions (Future Scope)

#### 7.6.1 RBD Mirroring

RBD mirroring enables asynchronous replication of RBD images between two
Ceph clusters (primary and secondary site).

**Use Cases**:

- Disaster Recovery for critical Cinder volumes.

- Cross-site data protection.

**Recommendation**: RBD mirroring should be considered for production
workloads that require Recovery Point Objective (RPO) of minutes to
hours. It is enabled per-pool or per-image and supports both
journal-based and snapshot-based mirroring.

#### 7.6.2 CephFS Mirroring

CephFS supports mirroring between two clusters for shared file system
disaster recovery.

**Recommendation**: If CephFS is used (via Manila or direct NFS), CephFS
mirroring should be enabled for critical file shares.

#### 7.6.3 RGW Multisite (Geo-Replication)

RGW supports active-active multisite replication for object storage.

**Use Cases**:

- Global object storage with low-latency access.

- Disaster recovery for S3/Swift data.

**Recommendation**: RGW multisite should be implemented if object
storage (RGW) is in scope and geo-redundancy is required.

#### 7.6.4 Backup Strategy Recommendation

| **Protection Method** | **Protects Against**                | **Recommended For**         | **Best Practice** |
|-----------------------|-------------------------------------|-----------------------------|-------------------|
| 3x Replication        | Hardware /node failure              | All data                    | Always enabled    |
| RBD Snapshots         | Accidental deletion, logical errors | Critical volumes & images   | Daily/Weekly      |
| External Backup       | Full cluster / site failure         | Production data             | Weekly + offsite  |
| RBD Mirroring         | Site-level disaster                 | Business-critical workloads | If DR required    |
| RGW Multisite         | Site-level disaster (object data)   | Object storage              | If RGW in scope   |
