# Analysis

## 2. Requirements

This Ceph deployment will serve as the primary and unified storage
backend for our new 8-node OpenStack cluster. The goal is to replace
multiple separate storage systems with a single, scalable, and highly
resilient solution that can handle all major storage needs of the cloud
platform.

Ceph will provide reliable block storage for Cinder (volumes, snapshots,
backups, and attachments to virtual machines) and Glance (image storage
and management). It will also support ephemeral disks for Nova instances
where required. Object storage will be delivered through the RADOS
Gateway (RGW) with S3 and Swift compatibility starting from Phase 1.
Additionally, we plan to support external enterprise systems by exposing
storage through iSCSI gateways for block-level access and NAS-style file
sharing using NFS via CephFS where legacy applications need it.

The design prioritizes high availability. The cluster must tolerate the
failure of any single Ceph node without data loss or significant
downtime. This will be achieved primarily through a 3x replication
policy across the four Ceph nodes. Automated recovery mechanisms should
handle rebalancing and healing of data in the background with minimal
impact on running workloads.

**Key Non-Functional Requirements:**

- High Availability and Resilience: Deploy three Ceph Monitors (MONs)
  > for quorum, multiple Managers (MGRs), and ensure no single point of
  > failure in the control or data path. The system should support
  > graceful node maintenance and automatic failover.

- Performance: Deliver strong IOPS and low latency suitable for
  > production VM workloads. This depends heavily on dedicated
  > high-speed storage **networks, proper** tuning of BlueStore backend,
  > appropriate PG (Placement Group) counts, and efficient use of
  > hardware resources.

- Scalability: The architecture must allow easy horizontal scaling. We
  > should be able to add more OSDs or even additional storage nodes in
  > the future without disrupting operations or requiring major
  > reconfiguration.

- Security: Enforce strict network isolation for all Ceph traffic, use
  > CephX authentication for all clients, and limit access to iSCSI and
  > NAS gateways. Sensitive data should be protected both in transit and
  > at rest where possible.

- Manageability and Observability: The cluster should be easy to
  > monitor, troubleshoot, and maintain. Integration with standard
  > monitoring tools for health checks, capacity alerts, and performance
  > metrics is essential.

- Capacity: Provide sufficient usable storage after replication overhead
  > to support the initial deployment and anticipated growth. The design
  > takes into account the hardware configuration of 16-core nodes with
  > 64 GB and 96 GB RAM across the cluster.

**Infrastructure Needs:**

- Node Distribution: Ceph services will run on 4 nodes out of the total
  > 8-node cluster. This includes 3 hyper-converged Controller + Ceph
  > nodes and 1 dedicated Ceph node focused on storage capacity. The
  > remaining 4 nodes will act as pure Compute nodes and Ceph clients.

- Networking: Full use of the planned 11 networks. Special attention
  > must be given to the Storage Public Network (for client traffic from
  > OpenStack services such as Nova, Cinder, and Glance) and the Storage
  > Cluster Network (for internal OSD replication, heartbeats, and
  > recovery traffic). Dedicated and isolated networks are also required
  > for the Enterprise External Storage through iSCSI and NAS to avoid
  > interference with core cluster operations.

- Hardware: All Ceph nodes will have 16 CPU cores. RAM configuration
  > includes 64 GB on some nodes and 96 GB on others. Each Ceph node
  > must have sufficient disks for OSDs, with separate OS boot drives to
  > ensure best performance and reliability. Network interfaces should
  > be configured with bonding for redundancy and higher throughput on
  > storage-related networks.

- Software and Integration: Ceph must integrate smoothly with our chosen
  > OpenStack deployment method. We will use modern best practices such
  > as BlueStore as the OSD backend.

**Assumptions and Constraints:**

- Exact disk types, quantities, and speeds per node will be finalized
  > during procurement.

- The underlying network infrastructure (VLANs, switches, and IP
  > addressing) for all 11 networks must be ready and tested before Ceph
  > deployment.

- Team will have sufficient access and permissions for installation,
  > configuration, and testing.
