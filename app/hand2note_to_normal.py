# -*- coding: utf-8 -*-
import re
import pprint
import os
import DBOperater
import Constant

class HandsTransformer:
    ACTION_MAP = {
        "folds" : "fold",
        "calls" : "call",
        "checks": "check",
        "bets"  : "raise",
        "raises": "raise"
    }

    def __init__(self, bb, ante, straddle):
        self.m_bb = bb
        self.m_ante = ante
        self.m_straddle = straddle
        self.m_idx = 1

    def process_one_hand(self, ifile, hands_idx):
        while True:
            line = ifile.readline()
            if not line:
                return None
            if line.startswith("PokerStars"):
                result = re.match("PokerStars Hand.*\(¥(.*)/¥.* - (.*) UTC", line)
                bb = 2 * int(result.group(1))
                time_str = result.group(2)
                if bb != self.m_bb:
                    print "bb is not equal to target bb, bb : ", bb
                    return None
                break
        first_line = line
        line = ifile.readline()
        result = re.match(".*#([1-9]) is the button.*", line)
        dealer_pos = int(result.group(1))
        player_info = []
        while True:
            line = ifile.readline()
            result = re.match("Seat ([1-9]): ([0-9]*) \(¥([0-9\.]*) in chips\).*", line)
            if result:
                seat = int(result.group(1))
                player_id = result.group(2)
                chips = float(result.group(3))
                if seat == dealer_pos:
                    dealer_idx = len(player_info)
                player_info.append([seat, player_id, chips])
            else:
                break
        while True:
            line = ifile.readline()
            if line.startswith("*** HOLE CARDS ***"):
                break
        player_id_to_pos = {}
        # pprint.pprint(player_info)
        pos_idx = 1
        player_quantity = len(player_info)
        for idx in range(dealer_idx, -1, -1):
            seat, player_id, chips = player_info[idx]
            player_id_to_pos[player_id] = pos_idx
            pos_idx += 1
        for idx in range(len(player_info) - 1, dealer_idx, -1):
            seat, player_id, chips = player_info[idx]
            player_id_to_pos[player_id] = pos_idx
            pos_idx += 1
        # pprint.pprint(player_id_to_pos)
        straddle_player_id = 0
        for seat, player_id, chips in player_info:
            if player_id_to_pos[player_id] == player_quantity:
                player_id_to_pos[player_id] = 9
                sb_player_id = player_id
            elif player_id_to_pos[player_id] == player_quantity - 1:
                player_id_to_pos[player_id] = 8
                bb_player_id = player_id
            elif player_id_to_pos[player_id] == player_quantity - 2:
                straddle_player_id = player_id
        if straddle_player_id == 0:
            print "straddle player id is 0"
            print line
            print first_line
            return None
        stack = [0] * 10
        for seat, player_id, chips in player_info:
            stack[player_id_to_pos[player_id]] = float(chips)

        board = ""
        turn_actions = {}
        while True:
            # print "deal turn : ", line
            if not line or "SHOW DOWN" in line:
                break
            for turn_str in ["HOLE CARDS", "FLOP", "TURN", "RIVER"]:
                if turn_str in line:
                    break
            else:
                line = ifile.readline().strip()
                continue
            if turn_str == "HOLE CARDS":
                turn_str = "PREFLOP"
            elif turn_str == "FLOP":
                result = re.match(".*\[(.*)\].*", line)
                board = result.group(1)
            elif turn_str == "TURN" or turn_str == "RIVER":
                result = re.match(".*\[([ATJQK23456789][sdch])\].*", line)
                board += " " + result.group(1)
            bets_his = {}
            curent_turn_actions = []
            raise_value = 0
            if turn_str == "PREFLOP":
                raise_value = self.m_bb * 2
                if stack[player_quantity - 2] < self.m_bb * 2:
                    raise_value = stack[player_quantity - 2]
                bets_his[sb_player_id] = self.m_bb / 2
                bets_his[bb_player_id] = self.m_bb
                bets_his[straddle_player_id] = self.m_bb * 2
            while True:
                line = ifile.readline()
                line = line.strip()
                # print "inner line : ", line
                for action in ["folds", "calls", "checks", "raises", "bets"]:
                    if action in line:
                        # print "????????????"
                        value = 0
                        if action == "bets":
                            result = re.match("(.*): bets ¥([0-9\.]*).*", line)
                            player_id = result.group(1)
                            value = float(result.group(2))
                            bets_his[player_id] = value
                            raise_value = value
                        elif action == "raises":
                            result = re.match("(.*): raises ¥([0-9\.]*) to ¥([0-9\.]*).*", line)
                            player_id = result.group(1)
                            target_bet_value = float(result.group(3))
                            value = target_bet_value - bets_his.get(player_id, 0)
                            bets_his[player_id] = target_bet_value
                            raise_value = target_bet_value
                        elif action == "calls":
                            result = re.match("(.*): calls ¥([0-9\.]*).*", line)
                            player_id = result.group(1)
                            value = float(result.group(2))
                            bets_his[player_id] = raise_value
                        else:
                            result = re.match("(.*):.*", line)
                            player_id = result.group(1)
                        curent_turn_actions.append([player_id_to_pos[player_id], self.ACTION_MAP[action], round(value, 2)])
                        break
                    elif "Dealt to" in line:
                        break
                else:
                    # print "????????????uuuu"
                    break
            board = board.replace("A", "1")
            if curent_turn_actions:
                turn_actions[turn_str] = curent_turn_actions
            # line = ifile.readline().strip()

        private_cards = [None] * 10
        if "SHOW DOWN" in line:
            while True:
                line = ifile.readline()
                result = re.match("(.*): shows \[([ATJQK23456789][sdch] [ATJQK23456789][sdch])\].*", line)
                if result:
                    player_id = result.group(1)
                    cards = result.group(2)
                    cards = cards.replace("A", "1")
                    private_cards[player_id_to_pos[player_id]] = cards
                else:
                    break
        line = line.strip()
        while line:
            line = ifile.readline().strip()
        name_list = [0] * 10
        id_list = [0] * 10
        for player_id, pos in player_id_to_pos.items():
            name_list[pos] = player_id
            id_list[pos] = player_id
        hands_json = {}
        hands_json["_id"] = time_str + " " + str(hands_idx)
        hands_json["data"] = {}
        hands_json["data"]["NAME"] = name_list
        hands_json["data"]["BB"] = self.m_bb
        hands_json["data"]["PVCARD"] = private_cards
        hands_json["data"]["STACK"] = stack
        hands_json["data"]["BETDATA"] = turn_actions
        hands_json["data"]["PLAYQUANTITY"] = player_quantity
        hands_json["data"]["ante"] = self.m_ante
        hands_json["data"]["ID"] = id_list
        hands_json["data"]["BOARD"] = board
        return hands_json

    def write_to_db(self, hands_json):
        DBOperater.ReplaceOne(Constant.HANDSDB, "flh", {"_id": hands_json["_id"]}, hands_json, True)

    def process_all(self, fname):
        print "fname : ", fname
        ifile = open(fname)
        while True:
            hands_json = self.process_one_hand(ifile, self.m_idx)
            if hands_json:
                self.m_idx += 1
                self.write_to_db(hands_json)
            else:
                break
        print "finish"

    def process_directory(self, dir_name):
        files = os.listdir(dir_name)
        for fname in files:
            # if "2022_6_20" not in fname:
            #     continue
            self.process_all(dir_name + "/" + fname)
        print "m_idx : ", self.m_idx
        print "file number : ", len(files)

def test():
    transformer = HandsTransformer(2, 1, True)
    # transformer.process_all("C:\Hand2NoteHh\PokerMaster\PokerMaster_2022_6_21_PMS_87792185.txt")
    # transformer.process_directory("C:\Hand2NoteHh\PokerMaster")
    transformer.process_directory("/home/zoul15/pcshareddir/download/PokerMaster")

if __name__ == "__main__":
    test()