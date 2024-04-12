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
  count = 5
  name  = "boot_volume${count.index+1}"
  size  = 20
  image_id = "6094568b-0d16-48a5-bc10-66645c361d4a"
}

resource "openstack_blockstorage_volume_v3" "ceph_volume" {
  count = 5
  name  = "ceph_volume${count.index+1}"
  size  = 20
}

resource "openstack_compute_instance_v2" "master_instance" {
  count = 5
  name          = "Node${count.index+1}"
  flavor_name   = "css.2c6r.20g"
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
  count = 5
  instance_id = openstack_compute_instance_v2.master_instance[count.index].id
  volume_id   = openstack_blockstorage_volume_v3.ceph_volume[count.index].id
}

data "template_file" "ansible_inventory" {
  template = file("${path.module}/inventory.tpl")

  vars = {
    ips = [for instance in openstack_compute_instance_v2.master_instance : instance.access_ip_v4]
  }
}

resource "local_file" "inventory" {
  content  = data.template_file.ansible_inventory.rendered
  filename = "${path.module}/ansible_inventory.ini"
}

output "ansible_inventory" {
  value = data.template_file.ansible_inventory.rendered
}

 