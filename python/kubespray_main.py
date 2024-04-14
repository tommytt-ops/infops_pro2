import os
from kubespray_utils import run_setup_palybook, all_server_list, apply_terraform, kubespray_run


if __name__ == "__main__":

    run_setup_palybook()

    apply_terraform()

    kubespray_dir="/home/ubuntu/kubespray"
    os.chdir(kubespray_dir)

    ip_list = all_server_list()
    kubespray_run(ip_list)

    



