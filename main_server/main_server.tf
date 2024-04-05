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
        name = "master_pro2"
        image_name = "ubuntu-22.04-LTS"
        flavor_name = "C4R8_10G"
        key_pair = "key"
        security_groups = ["default"]

        network {
        name = "acit"
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
            ]
        }

        provisioner "file" {
            source      = "/Users/tommytran/.config/openstack/clouds.yml" 
            destination = "/home/ubuntu/.config/openstack/clouds.yml"
        }

      

}