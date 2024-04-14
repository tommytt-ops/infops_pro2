import os
from kubespray_utils import run_setup_palybook, all_server_list


if __name__ == "__main__":

    run_setup_palybook()

    kubespray_dir="/home/ubuntu/kubespray"
    os.chdir(kubespray_dir)

    print(all_server_list())

    



