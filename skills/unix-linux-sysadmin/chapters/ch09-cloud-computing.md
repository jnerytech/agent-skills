# Chapter 9: Cloud Computing

## Core Idea
Cloud computing = leasing on-demand, metered compute/storage/network from shared capacity. The payoff is elasticity, infrastructure-as-code, global reach, and lower capex — but it demands a mental shift: cloud servers are **cattle, not pets** (ephemeral, can fail anytime; design for it). For most orgs, use a **public cloud**; private/hybrid rarely pays off.

## Frameworks Introduced
- **Cattle, not pets**: never name, nurse, or depend on a single instance. Treat instances as interchangeable, short-lived herd members. "Cloud native" = reliable despite unanticipated instance failures.
- **The three service models (who manages what)**: **IaaS** (you manage OS+up; vendor manages hardware/virtualization — most relevant to sysadmins), **PaaS** (you manage code; vendor manages OS+runtime), **SaaS** (you manage nothing but data/config).
- **Regions and availability zones**: a *region* = a geographic location of data centers; a *zone* = an independent (power/cooling/geography) data-center cluster within a region, peered by fast low-latency links. Deploy across zones/regions for high availability.
- **Infrastructure as code**: provision/release the entire lifecycle of networked systems via API/templates (CloudFormation, Terraform), version-controlled — not manual procurement.

## Key Concepts
- **VPS / instance**: a VM on the provider's hardware, created from an **image** (saved OS state: root FS + boot loader), sized by **instance type**. Pay only for use; no up-front cost.
- **Storage types**: **object store** (S3/GCS — flat namespace, near-unlimited, HTTPS, read-mostly, slow); **block storage** (EBS/persistent disk — virtual disks attachable to a VPS); **ephemeral/instance store** (fast local disk, *lost on instance deletion* — temp files only).
- **Networking**: build virtual networks with subnets/routes/firewall rules; instances get public routable IPs *or* private RFC1918 only (reach private hosts via bastion/jump host or VPN). Minimize external footprint.
- **Identity & authorization**: least privilege via IAM (AWS strongest — users/groups + *roles for systems* with auto key rotation). Azure = Active Directory; Google IAM coarser.
- **Serverless / functions-as-a-service** (Lambda, Cloud Functions): code runs in response to an event then terminates; no server/OS to manage; pay per execution time.
- **Cost components**: compute (per hour/minute), data transfer (per GiB, incl. inter-zone/region), storage (per GiB-month). On-demand is most expensive; reserved/committed-use and spot/preemptible discount it.

## Mental Models
- **Lift-and-shift rarely works.** Migrating a static enterprise app unchanged usually fails — cloud operational processes differ and individual instances are unreliable by design. Re-architect for ephemerality.
- **"Private cloud" ≠ more secure.** Public-cloud tenants are isolated by layers of hw/sw virtualization; a private cloud offers little practical security benefit and is expensive, complex, and feature-poor by comparison.
- **CLI/API over the web GUI for anything repeatable.** Use the console to learn and bootstrap; script everything via the CLI (`aws`/`gcloud`/`tugboat`) for automation and reproducibility.
- **Cost discipline = measure, monitor, avoid overprovisioning.** Autoscale down at low demand; use more, smaller instances for granularity; don't buy reserved capacity until usage patterns are clear.

## Anti-patterns
- **Treating an instance as a pet**: nursing a sick cloud server instead of replacing it ignores the platform's ephemerality.
- **Leaving instances/droplets running (or even powered-down)**: you're billed regardless; snapshot then destroy.
- **Serving large media directly from the cloud** instead of a CDN: a top driver of surprise data-transfer bills (along with multi-zone DB replication and cross-region snapshots — limit replication to 2 zones).
- **Provisioned-IOPS EBS clusters**: per-GiB-month *and* per-IOPS-month pricing "just might break the bank."
- **Logging in directly as root / using the default user long-term**: enable MFA on root, create named IAM users, disable the default image user after first boot, use SSH public keys only (no passwords).

## Code Examples
```sh
# AWS — aws CLI (Python/Boto), pip install awscli ; aws configure
aws ec2 run-instances --image-id ami-d440a6e7 --instance-type t2.nano \
    --associate-public-ip-address --key-name admin-key   # JSON output, scriptable
aws ec2 describe-instances --instance-id i-c4f60303
aws ec2 get-console-output --instance-id i-c4f60303      # debug boot/hang
aws ec2 stop-instances ...        # stop = keep; terminate = delete (root disk gone forever)

# GCP — gcloud (synchronous: waits until instance is up)
gcloud init ; gcloud compute images list --regexp 'debian.*'
gcloud compute instances create ulsah --image debian-8
gcloud compute ssh ulsah

# DigitalOcean — tugboat (Ruby gem); droplets boot ~55s
tugboat create -i ubuntu-16-04-x64 -k <ssh-key-id> ulsah-ubuntu
tugboat ssh ulsah-ubuntu
tugboat snapshot droplet ; tugboat destroy droplet      # memorialize then decommission
```

## Reference Tables
**Provider snapshot**: AWS = "900lb gorilla," rapid innovation, can be expensive/complex, strongest IAM. GCP = technically sophisticated, best global network, simpler sustained-use pricing. DigitalOcean = simple/cheap (droplets), great for dev/PoC, no true availability zones. Azure = distant second, good for Microsoft shops. OpenStack = DIY private cloud.

**Which layers you manage**: IaaS → OS + runtime + app + data (vendor: virt + hardware). PaaS → app + data (vendor: OS + runtime). SaaS → data/config only.

**Pricing models (compute)**: on-demand (most expensive, per hour/min) · AWS reserved (cheaper, up-front, tied to instance family) · AWS spot / GCP preemptible (deeply discounted spare capacity, interruptible) · GCP sustained-use (auto discount, ~30% monthly, switch anytime).

## Worked Example
**Launch an EC2 instance from the CLI and reach it.** `aws ec2 run-instances --image-id ami-d440a6e7 --instance-type t2.nano --associate-public-ip-address --key-name admin-key`. The AMI is region-specific CentOS 7; `t2.nano` = 1 CPU/512MiB; the `--associate-public-ip-address` flag is required because VPC-subnet instances default to *no* public IP. The JSON output yields `InstanceId` (e.g. `i-c4f60303`) — feed it to `aws ec2 describe-instances` to get the IP. But you still can't connect: AWS firewalls are **security groups**, and the unspecified `default` group allows *no* access. Adjust it to permit SSH (TCP 22) from your IP, then `ssh` in as the AMI's nonroot sudo user (`centos`/`ubuntu`/`ec2-user`) with your private key — passwords are disabled. Disable that default user and create named accounts after first boot.

## Key Takeaways
1. Cattle, not pets — instances are ephemeral; design for failure and re-architect rather than lift-and-shift.
2. IaaS is the sysadmin's domain; know the responsibility split for PaaS/SaaS.
3. Spread across availability zones/regions for HA; choose regions by user proximity.
4. Know the three storage types — especially that ephemeral storage vanishes on instance deletion.
5. Automate via CLI/API and infrastructure-as-code (CloudFormation/Terraform); the web console is for learning and emergencies.
6. Cost surprises come from data transfer, IOPS, and idle resources — measure, autoscale down, and don't over-commit to reserved capacity.

## Connects To
- **Ch 23**: configuration management — broadly applicable to cloud fleets.
- **Ch 13**: cloud TCP/IP networking, security groups (the network-layer detail).
- **Ch 24/25**: virtualization (the foundation) and containers (cloud-native packaging).
- **Ch 26**: CI/CD pipelines using cloud services and Terraform.
- **Ch 7**: SDKs/CLI tools are Python/Ruby (boto, gcloud) — scripting skills apply directly.
