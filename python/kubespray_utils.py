import subprocess
import json
import subprocess
import os

def run_setup_palybook():
    playbook_dir = "../ansible"
    os.chdir(playbook_dir)

    result = subprocess.run("ansible-playbook -i  kubespray_setup.ansible.yml", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

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