import hand2note_to_normal
import os
import time
import requests

class SyncPlayerID:
    def __init__(self, dirname):
        self.m_dirname = dirname

    def get_newest_fname(self):
        files = os.listdir(self.m_dirname)
        if not files:
            return None
        files = sorted(files, key=lambda x:-os.path.getmtime(os.path.join(self.m_dirname, x)))
        return files[0]

    def sync_once(self):
        fname = self.get_newest_fname()
        path = os.path.join(self.m_dirname, fname)
        ifile = open(path)
        last_space = 0
        cnt = 0
        for line in ifile:
            if not line.strip():
                last_space = cnt
            cnt += 1
        ifile.close()

        print fname
        if not fname:
            return
        transformer = hand2note_to_normal.HandsTransformer(2, 1, True)
        ifile = open(path)
        for i in range(last_space):
            ifile.readline()
        hands_json = transformer.process_one_hand(ifile, 0)
        if hands_json:
            id_vec = list()
            for v in hands_json["data"]["ID"]:
                if v != 0:
                    id_vec.append(v)
            url = "http://192.168.0.21:8080/update_player_id/" + "_".join(id_vec)
            requests.get(url)

    def start(self):
        pass

def sync_main():
    sync_engine = SyncPlayerID("C:\Hand2NoteHh\PokerMaster")
    while True:
        sync_engine.sync_once()
        time.sleep(10)

if __name__=="__main__":
    sync_main()