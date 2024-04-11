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

resource "openstack_compute_instance_v2" "master_instance" {
        name = "Node_Ansible"
        image_name = "ubuntu-22.04-LTS"
        flavor_name = "C4R8_10G"
        key_pair = "key"
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

        resource "openstack_blockstorage_volume_v3" "boot_volume" {
            count = 3
            name  = "boot_volume${count.index}"
            size  = 40
            image_id = "6094568b-0d16-48a5-bc10-66645c361d4a"
        }

        connection {
         type = "ssh"
         user = "ubuntu"
         private_key = "${file("~/.ssh/id_rsa")}"
         host = self.access_ip_v4
        }

          provisioner "remote-exec" {
         inline = [
                "sudo mkdir /home/ubuntu/.config",
                "sudo mkdir /home/ubuntu/.config/openstack",
                "sudo chown ubuntu: /home/ubuntu/.config/openstack",
                "sudo apt install -y python3-openstackclient", 
            ]
        }

        provisioner "file" {
            source      = "/Users/tommytran/.config/openstack/clouds.yml" 
            destination = "/home/ubuntu/.config/openstack/clouds.yml"
        }

        provisioner "remote-exec" {
         inline = [
                "openstack --os-cloud=openstack keypair delete masterKey",
                "openstack --os-cloud=openstack keypair create --public-key ~/.ssh/id_rsa.pub masterKey",       
            ]
        }

       

      

}