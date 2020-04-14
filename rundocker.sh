#!/bin/bash
sudo docker run -v /mnt/mfs/users/zoul15/pccppdocker/build/pokerweb/app:/app \
-p 80:80  --net=host  pustudy/pmserver:1

