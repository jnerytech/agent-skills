# Chapter 24: Virtualization

## Core Idea
Server virtualization runs multiple OS instances concurrently on one physical machine, with a **hypervisor** parceling out CPU/memory/I/O among isolated guests. It decouples hardware from OS — yielding flexibility, portability, programmatic management, and higher hardware utilization — and underpins both cloud computing and containers. The modern baseline is **hardware-assisted virtualization** (Intel VT / AMD-V); don't fuss over the taxonomy of virtualization modes — keep software updated and the hypervisor picks the best one.

## Frameworks Introduced
- **Virtualization spectrum** (evolution toward less overhead): **full virtualization** (emulate all hardware, unmodified guests, slow — uses QEMU) → **paravirtualization** (modified guests cooperate with the hypervisor, ~10× faster) → **hardware-assisted** (CPU/memory virtualized in silicon, guests unaware) → **paravirtualized drivers** (install special disk/net/display drivers; the rest handled by hardware) → modern blends (Xen PVH).
- **Type 1 vs Type 2 hypervisor**: Type 1 = bare-metal/native, runs directly on hardware (VMware ESXi, XenServer); Type 2 = runs atop a host OS (VirtualBox, VMware Workstation, bhyve). "More academic than practical" — KVM blurs the line (a kernel module).
- **VM vs Container**: a VM is a *full OS* (own kernel, init, drivers) sharing hardware via a hypervisor; a container is *the facade of an OS* — isolated processes sharing the host kernel. VMs: GB images, ~minutes to boot, complete isolation, dozens/host. Containers: MB images, <1s start, shared kernel, many/host.
- **Infrastructure as code via image-building** (Packer): describe an image in a template, version-control it, build identically for any platform — transparency, repeatability, reversibility, audit trail.

## Key Concepts
- **Hypervisor** (VMM): mediates between VMs and hardware; guests access hardware only through it and are isolated from each other. Guests can be heterogeneous (CentOS + FreeBSD + Windows side by side).
- **Live migration**: move a running VM between physical hosts with no service interruption — hypervisor copies memory deltas until source and target match. Enables HA, maintenance, disaster recovery.
- **VM images**: templates of configured OSes a hypervisor loads; portable across hosts (standardized virtual hardware) but hypervisor-specific (conversion tools exist). Snapshot a VM to make a new image.
- **Xen**: paravirtual bare-metal hypervisor (0.1–3.5% overhead); powers AWS. **dom0** (privileged, full hardware access, runs drivers + manages other domains) vs **domU** (unprivileged guests). Manage with `xl`; config in `/etc/xen`.
- **KVM**: turns the Linux kernel *into* the hypervisor — guests are normal Linux processes (control with `top`/`ps`/`kill`); full virtualization via QEMU + VT/AMD-V; default for most distros, supports Windows guests.
- **Containers on VMs ("bin packing")**: standard cloud pattern — VMs subdivide physical hosts, containers run atop VMs for density.

## Mental Models
- **Don't memorize virtualization modes.** The boundaries are porous; the hypervisor works out the best option per guest. Keep software updated to get the latest enhancements automatically; only pick a non-default mode for old hardware/hypervisors.
- **Containers and VMs are complementary, not competing.** Use VMs to slice physical servers into managed chunks, then run containerized apps atop them for optimal density — the standard architecture for cloud-hosted containerized apps.
- **Tooling converges even when tech diverges.** Xen and KVM are fundamentally different but both install/manage guests with `virt-install`/`virt-manager` (Xen uses `xl`, KVM uses `virsh`).
- **Image-as-code beats hand-tuned images.** Modify a Packer template and commit it instead of manually patching a golden image — you get a reversible audit trail.

## Anti-patterns
- **VirtualBox for production**: consumer-grade Type 2 hypervisor — weak performance and hardware support; fine for dev/test, not production.
- **FreeBSD bhyve for general use today**: new, limited hardware support, missing core features — choose another solution until it matures.
- **File-backed VBD when you have a performance bottleneck**: dedicated disk/LV is faster; but file-backed VBDs are more flexible (manage with `mv`/`cp`, sparse/grow-on-demand) and the usual best default — easy to migrate to a dedicated disk later.
- **Hand-applying changes to images**: lose repeatability/auditability — use Packer templates in version control.

## Code Examples
```sh
# Xen guest install + management
sudo virt-install -n chef -f /vm/chef.img -l http://example.com/myos -r 512 --nographics
sudo xl list                 # running domains (Domain-0 + guests)
sudo xl console 19           # attach to a guest console (Ctrl-] to detach)
# guest config: /etc/xen/chef ; symlink into /etc/xen/auto to autostart at boot

# KVM guest install + management (virt-install + virsh)
sudo virt-install --connect qemu:///system -n UbuntuYakkety -r 512 \
  -f ~/ubuntu.img -s 12 -c /dev/dvd --os-type linux --accelerate --hvm --vnc
sudo virsh
  list                       # virtual machines (running/shut off)
  start Windows2016Server ; shutdown CentOS

# Packer: build an image from a JSON template (infrastructure as code)
packer build custom_ami.json
# builders define HOW to create the image; provisioners (shell/Chef/Ansible) configure it
```
```json
// Packer template: amazon-ebs builder + shell provisioner
{
  "builders": [{ "type": "amazon-ebs", "region": "us-west-2",
    "source_ami": "ami-d440a6e7", "instance_type": "t2.medium",
    "ami_virtualization_type": "hvm", "ami_name": "ULSAH5E" }],
  "provisioners": [{ "type": "shell", "source": "customize_ami.sh" }]
}
```

## Reference Tables
**VM vs Container**: VM = full OS via hypervisor, ~1-2min boot, long-lived, GB images, dozens/host, complete isolation, any OS. Container = process group via shared kernel, <1s start, frequently replaced, MB images, many/host, shares host kernel (same kernel, distro may differ).

**Linux hypervisors**: Xen (paravirtual bare-metal, dom0/domU, powers AWS), KVM (kernel-as-hypervisor, full-virt + QEMU, default, Windows guests). FreeBSD: bhyve (immature). Commercial: VMware ESXi (Type 1, free with paid extras, best live migration). Dev: VirtualBox (Type 2, consumer).

**HashiCorp tooling**: Packer (build images from templates, multi-platform, JSON config), Vagrant (wrapper over VirtualBox/VMware/Docker — disposable dev environments mirroring production, not itself a hypervisor).

## Worked Example
**Build a reproducible AWS AMI with Packer (infrastructure as code).** Instead of launching an instance, hand-tuning it, and snapshotting (no audit trail, not repeatable), write `custom_ami.json`: a **builder** `amazon-ebs` specifies the source AMI, region, instance type, VPC subnet, and `associate_public_ip_address: true` (Packer reaches the instance over SSH); a **provisioner** of type `shell` points to `customize_ami.sh`. Run `packer build custom_ami.json`. Packer then: (1) auto-creates a key pair + security group, (2) launches the instance and waits for network access, (3) scp's and runs your provisioning script (add users, install/harden software), (4) calls EC2 `CreateImage` to bake the AMI, (5) terminates the instance and prints the AMI ID. Commit the template to git and you get transparency, repeatability, reversibility, and an audit trail — the same image builds identically for VMware/GCP/VirtualBox by swapping the builder. Use `-debug` to pause at each step, or the `null` builder to test provisioning without launching.

## Key Takeaways
1. A hypervisor shares hardware among isolated, possibly heterogeneous guest OSes; modern default is hardware-assisted virtualization — don't obsess over modes.
2. VMs (full OS, hypervisor, heavy, isolated) and containers (shared kernel, light, fast) are complementary — run containers on VMs for density.
3. Xen (paravirtual, dom0/domU, `xl`) and KVM (kernel-as-hypervisor, guests are processes, `virsh`) are the Linux leaders; both install via `virt-install`.
4. Live migration moves running VMs between hosts with no downtime — key for HA and maintenance.
5. Treat images as code with Packer (template → version control → reproducible multi-platform builds); avoid hand-tuned golden images.
6. VirtualBox/Vagrant for dev environments; ESXi for enterprise; bhyve still immature.

## Connects To
- **Ch 25**: containers (the OS-level virtualization alternative; containers-on-VMs).
- **Ch 9**: cloud computing (built on virtualization; instances are VMs; Packer builds AMIs).
- **Ch 23**: configuration management (Packer provisioners run Chef/Ansible; infrastructure as code).
- **Ch 20**: storage (virtual block devices, file-backed vs dedicated-disk VBDs).
