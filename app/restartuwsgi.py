import time
import os

if __name__ == "__main__":
    while True:
        os.system("systemctl restart uwsgi")
        time.sleep(600)
