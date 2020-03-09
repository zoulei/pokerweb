import time
import os

while True:
    os.system("bash rundocker.sh")
    time.sleep(600)
    os.system("bash /mnt/mfs/users/zoul15/pccppdocker/stop_containers.sh")
    os.system("bash /mnt/mfs/users/zoul15/pccppdocker/clean_containers.sh")
