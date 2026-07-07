# Deployment

Deployment is embedded in **Implementation Plan** and **OpenStack
Integration**.

Includes production rollout, validation, and sign-off.

## 8. Implementation Plan

**Step 1 - Planning (decide things first)** Before touching any
hardware, get answers to the open questions - disk sizes for Node 1-3,
SSD or HDD, whether iSCSI/NAS goes in or out, whether object storage is
needed. If you skip this, you'll end up redoing work later.

**Step 2 - Preparation (get hardware ready)**

- Install OS on all 8 nodes

- Set up cabling and network switches for all networks, especially the
  > two storage networks

- Make sure all nodes can talk to each other, have correct time (NTP),
  > and can be reached by SSH/Ansible

- Set OSD disks as plain individual disks, not RAID

**Step 3 - Install Ceph first, before OpenStack**

1.  Start Ceph on Node 1 (first MON + MGR)

2.  Add Node 2 and Node 3 as MONs - now you have 3, which gives quorum

3.  Add all 4 nodes as OSD hosts, add the actual disks

4.  Create the pools: volumes, images, vms, backups

5.  Check ceph -s says HEALTH_OK before moving on

**Step 4 - Install OpenStack, connect it to Ceph**

6.  Run Kolla-Ansible to deploy OpenStack

7.  Copy Ceph's keys/config into Cinder, Glance, Nova

8.  Run kolla-ansible reconfigure so those services actually use Ceph

9.  Set up monitoring (Prometheus/Grafana) and logging

**Step 5 - Test everything before going live**

- Basic connectivity checks

- Create a volume, boot a VM, snapshot it

- Run benchmarks (fio, rados bench) to get real performance numbers

- Kill an OSD, kill a node, kill a MON - one at a time - confirm cluster
  > survives

- Deliberately try killing two things at once - confirm it does NOT
  > survive (this is expected, and proves the known limitation)

- Test backup and restore for real, not just "backup ran successfully"

- Test live migration between compute nodes

**Step 6 - Go live**

- Only after all tests pass

- Take a backup first

- Confirm monitoring/alerts are working

- Get sign-off that everyone understands the cluster can't survive two
  > failures at once

- Set up initial users, projects, quotas

**Step 7 - Have a rollback plan ready**

- If a Ceph upgrade fails halfway, you can roll back per-daemon

- If OpenStack's connection to Ceph breaks, you can reconfigure back

- If something's badly wrong before real data exists, just delete and
  > recreate the pools

- If it's after go-live, restore from backup
