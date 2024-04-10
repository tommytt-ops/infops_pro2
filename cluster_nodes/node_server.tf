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
  count = 3
  name  = "boot_volume${count.index}"
  size  = 40
  image_id = "6094568b-0d16-48a5-bc10-66645c361d4a"
}

resource "openstack_blockstorage_volume_v3" "ceph_volume" {
  count = 3
  name  = "ceph_volume${count.index}"
  size  = 30
}

resource "openstack_compute_instance_v2" "master_instance" {
  count = 3
  name          = "Node${count.index}"
  flavor_name   = "C4R8_10G"
  key_pair      = "Ansible"
  security_groups = ["default"]

  block_device {
    uuid                = openstack_blockstorage_volume_v3.boot_volume[count.index].id
    source_type         = "volume"
    destination_type    = "volume"
    boot_index          = 0
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
  count = 3

  instance_id = openstack_compute_instance_v2.master_instance[count.index].id
  volume_id   = openstack_blockstorage_volume_v3.ceph_volume[count.index].id
}
