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

    ips_formatted = ' '.join(ip_list)

    result1 = subprocess.run("cp -rfp inventory/sample inventory/mycluster", shell=True, executable='/bin/bash', stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    command2 = f"declare -a IPS=({ips_formatted})"
    result2 = subprocess.run(command2, shell=True, executable='/bin/bash', stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    command3 = "CONFIG_FILE=inventory/mycluster/hosts.yaml python3 contrib/inventory_builder/inventory.py ${IPS[@]}"
    result3 = subprocess.run(command3, shell=True, executable='/bin/bash', stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    result4 = subprocess.run('echo "ubuntu ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/ubuntu', shell=True, executable='/bin/bash', stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    command5 = """ansible all -m shell -a "echo 'ubuntu ALL=(ALL) NOPASSWD:ALL' | sudo tee /etc/sudoers.d/ubuntu" -i inventory/mycluster/hosts.yml --user ubuntu"""
    result5 = subprocess.run(command5, shell=True, executable='/bin/bash', stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    command6 = """ansible all -m shell -a "echo 'net.ipv4.ip_forward=1' | sudo tee -a/etc/sysctl.conf" -i inventory/mycluster/hosts.yml --user ubuntu"""
    result6 = subprocess.run(command6, shell=True, executable='/bin/bash', stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    command7 = """ansible all -m shell -a "sudo sed -i '/ swap / s/^\(.*\)$/#\1/g' /etc/fstab && sudo swapoff -a" -i inventory/mycluster/hosts.yml --user ubuntu"""
    result7 = subprocess.run(command7, shell=True, executable='/bin/bash', stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result1 or result2 or result3 or result4 or result4 or result5 or result6 or result7 != 0:
        print("fail")


    



