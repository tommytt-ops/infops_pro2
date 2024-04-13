terraform {
  required_providers {
    openstack = {
      source = "terraform-provider-openstack/openstack"
    }
  }
}

provider "openstack" {
  cloud = "openstack"
}

resource "openstack_blockstorage_volume_v3" "boot_volume" {
  count     = 5
  name      = "boot_volume${count.index + 1}"
  size      = 20
  image_id  = "6094568b-0d16-48a5-bc10-66645c361d4a"
  volume_type      = "ceph_ssd"
}

resource "openstack_blockstorage_volume_v3" "ceph_volume" {
  count = 5
  name  = "ceph_volume${count.index + 1}"
  size  = 20
}

resource "openstack_compute_instance_v2" "master_instance" {
  count            = 5
  name             = "Node${count.index + 1}"
  flavor_name      = "css.2c6r.20g"
  key_pair         = "Ansible"
  security_groups  = ["default"]

  block_device {
    uuid                  = openstack_blockstorage_volume_v3.boot_volume[count.index].id
    source_type           = "volume"
    destination_type      = "volume"
    boot_index            = 0
    delete_on_termination = true
  }

  network {
    name = "acit"
  }

  connection {
    type        = "ssh"
    user        = "ubuntu"
    private_key = file("~/.ssh/id_rsa")
    host        = self.access_ip_v4
  }
}

resource "openstack_compute_volume_attach_v2" "ceph_volume_attach" {
  count        = 5
  instance_id  = openstack_compute_instance_v2.master_instance[count.index].id
  volume_id    = openstack_blockstorage_volume_v3.ceph_volume[count.index].id
}

locals {
  inventory_content = <<EOT
[all]
%{ for idx, ip in openstack_compute_instance_v2.master_instance.*.access_ip_v4 ~}
node${idx + 1} ansible_host=${ip} ansible_user=ubuntu
%{ endfor ~}

[kube-master]
node1
node2

[etcd]
node1
node2
node3

[kube-node]
node1
node2
node3
node4
node5

[k8s-cluster:children]
kube-master
kube-node

[calico-rr]

[vault]
node1
node2
node3
EOT
}

resource "local_file" "inventory" {
  content  = local.inventory_content
  filename = "${path.module}/ansible_inventory.ini"
}

output "inventory_content" {
  value = local.inventory_content
}
