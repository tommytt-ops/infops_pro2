import subprocess
import json
import subprocess
import os

def run_setup_palybook():
    playbook_dir = "../ansible"
    os.chdir(playbook_dir)

    result = subprocess.run('ansible-playbook kubespray_setup.ansible.yml -i "localhost,"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode == 0:
        print("Playbook applied")
    else:
        print("Playbook failed")
        print(result.stderr)


def all_server_list():
    ip_list = []  

    command = "openstack --os-cloud=openstack server list --format json"
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)

    if result.returncode == 0:
        try:
            server_data = json.loads(result.stdout)
            for server_json in server_data:
                
                network_info = server_json['Networks']
                
                if 'acit' in network_info and isinstance(network_info['acit'], list):
                    ip_list.extend(network_info['acit'])
           
            if len(ip_list) > 1:
                ip_list = ip_list[:-1]

        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
    else:
        print(f"Command failed with error: {result.stderr}")

    return ip_list

def apply_terraform():
    terraform_directory = '../cluster_nodes'
    os.chdir(terraform_directory)  

    subprocess.run("terraform init", shell=True, check=True)

    result = subprocess.run("echo yes | terraform apply", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode == 0:
        print("Terraform apply was successful")
        print(result.stdout)
    else:
        print("Terraform apply failed")
        print(result.stderr)

def kubespray_run(ip_list):
    # Prepare the IP addresses as a space-separated string
    ips_formatted = ' '.join(ip_list)

    # Command executions with error handling
    commands = [
        ("cp -rfp inventory/sample inventory/mycluster", "Copying inventory"),
        (f"declare -a IPS=({ips_formatted})", "Declaring IP array"),
        ("CONFIG_FILE=inventory/mycluster/hosts.yaml python3 contrib/inventory_builder/inventory.py ${IPS[@]}", "Running inventory builder"),
        ('echo "ubuntu ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/ubuntu', "Setting sudoers for ubuntu"),
        ("""ansible all -m shell -a "echo 'ubuntu ALL=(ALL) NOPASSWD:ALL' | sudo tee /etc/sudoers.d/ubuntu" -i inventory/mycluster/hosts.yml --user ubuntu""", "Applying sudoers change via Ansible"),
        ("""ansible all -m shell -a "echo 'net.ipv4.ip_forward=1' | sudo tee -a /etc/sysctl.conf" -i inventory/mycluster/hosts.yml --user ubuntu""", "Enabling IP forwarding"),
        ("""ansible all -m shell -a "sudo sed -i '/ swap / s/^\(.*\)$/#\1/g' /etc/fstab && sudo swapoff -a" -i inventory/mycluster/hosts.yml --user ubuntu""", "Disabling swap and updating fstab"),
    ]

    for command, description in commands:
        result = subprocess.run(command, shell=True, executable='/bin/bash', stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            
            print(f"Error during {description}: {result.stderr.strip()}")
            return  
        else:
            
            print(f"{description} executed successfully.")

   


    



