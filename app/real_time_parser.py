#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SIL Streaming Analyzer — Immediate Emit + Server Adapter (HTTP optional)
- 监控最新 .sil 文件，解析 HandStart / Action / Deal，实时输出/推送
- 双前缀: AutoHand2NoteDISPATCH / AutoMainDISPATCH
- /init 仅在信息完整时发送，并按 (GameNumber, WindowId) 去重
- 增加：座位映射规则 (Button=1, SmallBlind=9, BigBlind=8, 其余2..7)
"""

import os
import re
import time
import glob
import json
import datetime
from typing import Optional, Dict, Any, List, Tuple
from decimal import Decimal

# ================ 配置 ================
LOG_DIR = r"C:\Program Files\Hand2Note 4.1\logs"
PATTERN = "h2n-*.sil"

POLL_INTERVAL = 0.02
WINDOW_LIMIT  = 16384
HEARTBEAT_SEC = 10
DEBUG = False

USE_HTTP = True
SERVER_BASE_URL = "http://192.168.5.7:8080"
INIT_PATH   = "/init"
UPDATE_PATH = "/update"
NEWBOARD_PATH = "/newboard"

# ACTIONPOS_ZERO_BASE = True

EXTRA_HEADERS = {
    # "Authorization": "Bearer <token>"
}

DISPATCH_PREFIXES = ("AutoHand2NoteDISPATCH", "AutoMainDISPATCH")
DISPATCH_RE = r'(?:AutoHand2NoteDISPATCH|AutoMainDISPATCH)'

# ================ 正则 ================
RE_HAND_START_HEAD = re.compile(
    rf'{DISPATCH_RE}\s+Dynamic Message:\s*HandStartMessage:\s*hand\s*#(?P<GameNumber>\d+),\s*table=(?P<Table>\d+),\s*windowId=(?P<WindowId>\d+)',
    re.IGNORECASE
)
RE_JSON_BLOCK = re.compile(r'\{.*\}', re.DOTALL)

# RE_ACTION = re.compile(
#     rf'{DISPATCH_RE}\s+Dynamic Message:\s*ActionMessage:\s*Seat\s*#(?P<SeatNumber>\d+):\s*'
#     r'(?P<Action>CHECK|CALL|BET|RAISE|FOLD|ALL-?IN|CHECKS?|CALLS?|BETS?|RAISES?|FOLDS?)'
#     r'(?:\s+(?P<Amount>-?\d+))?'
#     r'(?:\s*,?\s*)'
#     r'.*?gameNumber\s*=\s*(?P<GameNumber>\d+)\s*,\s*windowId\s*=\s*(?P<WindowId>\d+)',
#     re.IGNORECASE | re.DOTALL
# )

RE_ACTION = re.compile(
    rf'{DISPATCH_RE}\s+Dynamic Message:\s*ActionMessage:\s*Seat\s*#(?P<SeatNumber>\d+):\s*'
    r'(?P<Action>CHECK|CALL|BET|RAISE|FOLD|ALL-?IN|CHECKS?|CALLS?|BETS?|RAISES?|FOLDS?)'
    r'(?:\s+(?P<Amount>-?\d+(?:[.,]\d+)?))?'
    r'(?:\s*,?\s*)'
    r'.*?gameNumber\s*=\s*(?P<GameNumber>\d+)\s*,\s*windowId\s*=\s*(?P<WindowId>\d+)',
    re.IGNORECASE | re.DOTALL
)

RE_DEAL = re.compile(
    rf'{DISPATCH_RE}\s+Dynamic Message:\s*DealMessage:\s*'
    r'(?P<Street>Flop|Turn|River)\((?P<Board>(?:[2-9TJQKA][shdc]){3,5})\)\s*'
    r'(?:hand\s*#(?P<GameNumber>\d+),\s*)?windowId\s*=\s*(?P<WindowId>\d+)\.?',
    re.IGNORECASE | re.DOTALL
)

RE_TRAILING_HOST = re.compile(r'(DESKTOP-[A-Za-z0-9\-]+|WIN-[A-Za-z0-9\-]+)$', re.IGNORECASE)

# ================ 状态缓存 ================
SEEN_INIT_KEYS: set[Tuple[Optional[int], Optional[int]]] = set()
STD_POS_MAPS: Dict[Tuple[int, int], Dict[int, int]] = {}

# ================ 工具函数 ================
def _clean_tail_host(s: str) -> str:
    return RE_TRAILING_HOST.sub('', s).strip()

def _normalize_action(s: str) -> str:
    s = s.upper()
    s = (s.replace("CHECKS", "CHECK").replace("CALLS", "CALL")
           .replace("BETS", "BET").replace("RAISES", "RAISE")
           .replace("FOLDS", "FOLD").replace("ALL IN", "ALL-IN"))
    return s

def _split_board_cards(board: str) -> List[str]:
    cards = []
    i = 0
    while i < len(board) - 1:
        rank = board[i]
        suit = board[i + 1]
        if suit.lower() in ('s', 'h', 'd', 'c'):
            cards.append(rank + suit)
            i += 2
        else:
            i += 1
    return cards

def _try_parse_json_block(raw: str):
    s = _clean_tail_host(raw)
    try:
        return json.loads(s)
    except Exception:
        return None

# ================ 座位映射 ================
def build_stdpos_map(msg: Dict[str, Any]) -> Dict[int, int]:
    """
    根据 HandStart 构建 SeatNumber -> 标准位置映射
    - Button = 1
    - 小盲 = 9
    - 大盲 = 8
    - 其余座位按逆时针从 2 开始编号
    """
    players = msg.get("Players") or []
    occ = sorted({int(p.get("SeatNumber")) for p in players if p.get("SeatNumber")})
    if not occ:
        return {}

    # 1. 找 Button
    btn = None
    for p in players:
        if p.get("IsDealer"):   # Hand2Note 的 Dealer = Button
            btn = int(p["SeatNumber"])
            break
    if not btn:
        btn = occ[0]

    # 2. 找 SB / BB
    sb = None
    bb = None
    for p in players:
        seat = int(p.get("SeatNumber"))
        blind = p.get("PostedBlind", {})
        if isinstance(blind, dict):
            t = blind.get("Type")
            if t == 1:   # 小盲
                sb = seat
            elif t == 2: # 大盲
                bb = seat

    # 3. 建立映射
    mapping: Dict[int, int] = {btn: 1}
    if bb: mapping[bb] = 8
    if sb: mapping[sb] = 9

    # 4. 分配其余 (逆时针，越靠近 Button 位置编号越小)
    cur = btn
    pos = 2
    while True:
        cur = cur - 1 if cur > 1 else 8
        if cur == btn:
            break
        if cur in occ and cur not in mapping:
            mapping[cur] = pos
            pos += 1
    return mapping

# ================ 三类解析 ================
def parse_hand_start(text: str) -> Optional[Dict[str, Any]]:
    m = RE_HAND_START_HEAD.search(text)
    if not m:
        return None
    payload: Dict[str, Any] = {
        "Type": "HandStart",
        "GameNumber": int(m.group("GameNumber")),
        "WindowId": int(m.group("WindowId")),
        "Table": m.group("Table"),
    }
    j = RE_JSON_BLOCK.search(text)
    if j:
        raw = j.group(0)
        obj = _try_parse_json_block(raw)
        if isinstance(obj, dict):
            payload.update(obj)
        else:
            payload["RawJson"] = raw

    # 建立并缓存座位映射
    key = (payload["GameNumber"], payload["WindowId"])
    STD_POS_MAPS[key] = build_stdpos_map(payload)
    return payload

def _parse_amount_decimal(amount: Optional[str]) -> Decimal:
    """解析金额为 Decimal，支持 7 / 7.5 / 7,5 / -1.25；失败返回 0"""
    if not amount:
        return Decimal("0")
    s = amount.strip().replace(",", ".")
    try:
        return Decimal(s)
    except InvalidOperation:
        return Decimal("0")

def parse_action(text: str) -> Optional[Dict[str, Any]]:
    m = RE_ACTION.search(text)
    if not m:
        return None
    action = _normalize_action(m.group("Action"))
    amount = m.group("Amount")
    print ("========:", amount)
    payload = {
        "Type": "Action",
        "GameNumber": int(m.group("GameNumber")),
        "WindowId": int(m.group("WindowId")),
        "SeatNumber": int(m.group("SeatNumber")),
        "Action": action,
        "Amount": float(amount) if amount else 0
    }
    return payload

def parse_deal(text: str) -> Optional[Dict[str, Any]]:
    m = RE_DEAL.search(text)
    if not m:
        return None
    board = m.group("Board")
    payload = {
        "Type": "Deal",
        "WindowId": int(m.group("WindowId")),
        "Street": m.group("Street").capitalize(),
        "Board": board,
        "Cards": _split_board_cards(board),
    }
    gn = m.group("GameNumber")
    if gn:
        payload["GameNumber"] = int(gn)
    return payload

# ================ 完整性判定 ================
def handstart_is_complete(msg: Dict[str, Any]) -> bool:
    if isinstance(msg.get("Players"), list) and len(msg["Players"]) > 0:
        return True
    table = msg.get("Table")
    if isinstance(table, dict):
        stakes = table.get("Stakes") or {}
        bb = stakes.get("BigBlind", 0) or 0
        ante = stakes.get("Ante", 0) or 0
        if bb > 0 or ante > 0:
            return True
    return False

# ================ 文件追随 ================
def pick_latest_file(log_dir: str, pattern: str) -> Optional[str]:
    files = glob.glob(os.path.join(log_dir, pattern))
    if not files:
        return None
    files.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return files[0]

def follow_file(path: str, poll_interval: float = POLL_INTERVAL):
    f = open(path, "rb", buffering=0)
    try:
        f.seek(0, os.SEEK_END)
        while True:
            chunk = f.read(16384)
            if chunk:
                yield chunk
            else:
                time.sleep(poll_interval)
                try:
                    st_size = os.path.getsize(path)
                except FileNotFoundError:
                    time.sleep(poll_interval); continue
                if st_size < f.tell():
                    f.seek(0, os.SEEK_END)
    finally:
        f.close()

def follow_latest_file_immediate_switch(log_dir: str, pattern: str, poll_interval: float = POLL_INTERVAL):
    current_path = None
    current_iter = None
    while True:
        latest = pick_latest_file(log_dir, pattern)
        if latest and latest != current_path:
            current_path = latest
            print(f"[INFO] {datetime.datetime.now()} 正在处理文件: {current_path}", flush=True)
            current_iter = follow_file(current_path, poll_interval=poll_interval)
        if current_iter is None:
            time.sleep(poll_interval); continue
        try:
            yield next(current_iter)
        except StopIteration:
            current_iter = None
        except Exception:
            time.sleep(poll_interval)

# ================ 适配层 ================
def to_init_payload(msg: Dict[str, Any]) -> Dict[str, Any]:
    playquantity = 0
    bb = 0
    anti = 0
    initstack = [0.0] * 10   # 下标 0~9
    player_ids = [0] * 10

    table = msg.get("Table")
    stakes = table.get("Stakes") or {}
    bb = float(stakes.get("BigBlind") or 0)
    anti = float(stakes.get("Ante") or 0)

    key = (msg.get("GameNumber"), msg.get("WindowId"))
    stdmap = STD_POS_MAPS.get(key, {})

    my_name = msg.get("UserUsername", 0)
    mypos = -1

    players = msg.get("Players") or []
    playquantity = len(players)
    for p in players:
        seat = int(p.get("SeatNumber") or 0)
        stdpos = stdmap.get(seat, seat)
        if 1 <= stdpos <= 9:
            idx = stdpos
            initstack[idx] = float(p.get("InitialStackSize") or 0)
            uid = p.get("Username", 0)
            player_ids[idx] = int(uid)
            if uid == my_name:
                mypos = idx
            else:
                print (type(uid), type(my_name))
                print (uid, my_name)

    hand = ""
    
    return {
        "playquantity": playquantity,
        "bb": bb,
        "anti": anti,
        "hand": hand,
        "mypos": mypos,
        "initstack": initstack,
        "player_ids": player_ids
    }

def to_update_payload(msg: Dict[str, Any]) -> Dict[str, Any]:
    seat = int(msg.get("SeatNumber") or 0)
    key = (msg.get("GameNumber"), msg.get("WindowId"))
    stdmap = STD_POS_MAPS.get(key, {})

    if not stdmap:
        print(f"[WARN] 收到 Action 但没有 HandStart (Game={key[0]}, Window={key[1]}), 使用 SeatNumber 临时映射", flush=True)
        return {}

    stdpos = stdmap.get(seat, seat)

    actionpos = stdpos

    return {
        "actionpos": actionpos,
        "action": str(msg.get("Action", "")),
        "value": float(msg.get("Amount", 0) or 0)
    }

def to_newboard_payload(msg: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deal → /newboard
    - Flop: 发送前三张公共牌（3张）
    - Turn/River: 只发送本轮新发的那一张
    """
    street = str(msg.get("Street", "")).capitalize()
    board = str(msg.get("Board", ""))       # 例如 "AhKsQc" / "AhKsQcTd" / "AhKsQcTd2d"
    cards = msg.get("Cards") or _split_board_cards(board)

    if street == "Flop":
        out = "".join(cards[:3]) if cards else board[:6]
    elif street in ("Turn", "River"):
        out = cards[-1] if cards else ""
    else:
        # 兜底：按之前的行为发全量
        out = board

    return {"board": out}

def format_for_api(msg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    t = msg.get("Type")
    if t == "HandStart":
        if not handstart_is_complete(msg):
            return None
        g = msg.get("GameNumber")
        w = msg.get("WindowId")
        key = (g, w)
        if key in SEEN_INIT_KEYS:
            return None
        SEEN_INIT_KEYS.add(key)
        return {"endpoint": "init", "path": INIT_PATH, "body": to_init_payload(msg)}

    g = msg.get("GameNumber"); w = msg.get("WindowId")
    key = (g, w)
    # 👉 没有进行 init，就丢弃 update
    if key not in SEEN_INIT_KEYS:
        print(f"[WARN] 丢弃 {t}：未发送过 Init (Game={g}, Window={w})", flush=True)
        return None

    if t == "Action":
        return {"endpoint": "update", "path": UPDATE_PATH, "body": to_update_payload(msg)}

    if t == "Deal":
        return {"endpoint": "newboard", "path": NEWBOARD_PATH, "body": to_newboard_payload(msg)}

    return None

def send_to_server(endpoint_path: str, body: Dict[str, Any]) -> bool:
    if not USE_HTTP:
        return False
    try:
        import requests
    except Exception as e:
        print(f"[WARN] requests 未安装: {e}", flush=True)
        return False
    url = SERVER_BASE_URL.rstrip("/") + endpoint_path
    try:
        resp = requests.post(url, json=body, headers=EXTRA_HEADERS, timeout=30.0)
        if 200 <= resp.status_code < 300:
            print(f"[INFO] 成功发送到 {url}, 响应: {resp.text.strip()}", flush=True)
            return True
        else:
            print(f"[WARN] HTTP {resp.status_code} {url} 失败: {resp.text[:200]}", flush=True)
            return False
    except Exception as e:
        print(f"[WARN] HTTP 请求异常 {url}: {e}", flush=True)
        return False

# ================ 核心循环 ================
def run_immediate_emit(log_dir: str, pattern: str,
                       poll_interval: float = POLL_INTERVAL,
                       window_limit: int = WINDOW_LIMIT,
                       heartbeat_sec: int = HEARTBEAT_SEC):
    byte_iter = follow_latest_file_immediate_switch(log_dir, pattern, poll_interval=poll_interval)
    window = bytearray()
    last_emit_pos = 0
    last_heartbeat = time.time()

    def ascii_append_and_prune(bs: bytes):
        nonlocal window, last_emit_pos
        for b in bs:
            if 32 <= b < 127:
                window.append(b)
            elif b in (10, 13):
                window.append(b)
            else:
                window.append(32)
        if len(window) > window_limit:
            drop = len(window) - window_limit
            window = window[drop:]
            last_emit_pos = max(0, last_emit_pos - drop)

    def try_match_from(text: str, start_idx: int):
        sub = text[start_idx:]
        if not any(pref in sub for pref in DISPATCH_PREFIXES):
            return None, start_idx
        candidate_starts = [start_idx + m.start() for m in re.finditer(DISPATCH_RE, sub)]
        for begin in candidate_starts:
            snippet = _clean_tail_host(text[begin:])
            for parser, regex in ((parse_action, RE_ACTION),
                                  (parse_deal,   RE_DEAL),
                                  (parse_hand_start, RE_HAND_START_HEAD)):
                m = regex.search(snippet)
                if m:
                    payload = parser(snippet)
                    if payload:
                        end_consume = begin + max(len(m.group(0)), 120)
                        return payload, end_consume
        return None, start_idx

    for chunk in byte_iter:
        now = time.time()
        if now - last_heartbeat >= heartbeat_sec:
            curr = pick_latest_file(LOG_DIR, PATTERN)
            print(f"[HEARTBEAT] {datetime.datetime.now()} 程序运行中, 当前文件: {curr}", flush=True)
            last_heartbeat = now

        ascii_append_and_prune(chunk)
        if not window:
            continue

        text = window.decode('ascii', errors='ignore')
        payload, consumed_to = try_match_from(text, last_emit_pos)
        emitted = 0
        while payload and emitted < 8:
            api = format_for_api(payload)
            if api:
                print ("=============new message===============")
                print(json.dumps(payload, ensure_ascii=False), flush=True)
                print(json.dumps(api, ensure_ascii=False), flush=True)
                sent = send_to_server(api["path"], api["body"])
                # if not sent:
                    
                
            last_emit_pos = consumed_to
            payload, consumed_to = try_match_from(text, last_emit_pos)
            emitted += 1

        if DEBUG and emitted == 0 and any(pref in text[last_emit_pos:] for pref in DISPATCH_PREFIXES):
            idxs = [text.find(p, last_emit_pos) for p in DISPATCH_PREFIXES]
            idxs = [i for i in idxs if i != -1]
            if idxs:
                start = min(idxs)
                preview = text[start:start+200]
                print(f"[DEBUG-RAW] …{preview}", flush=True)
                last_emit_pos = start + max(len(preview), 120)

def main():
    run_immediate_emit(
        log_dir=LOG_DIR,
        pattern=PATTERN,
        poll_interval=POLL_INTERVAL,
        window_limit=WINDOW_LIMIT,
        heartbeat_sec=HEARTBEAT_SEC
    )

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
