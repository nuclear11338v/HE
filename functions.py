# functions.py
import json
import subprocess
import threading
import os
import time
from datetime import datetime
import random
from config import Config

class AttackManager:
    _semaphore = threading.Semaphore(Config.MAX_CONCURRENT_ATTACKS)
    
    @classmethod
    def run_attack(cls, ip, port, duration, user_id):
        with cls._semaphore:
            try:
                process = subprocess.Popen(
                    [Config.BINARY_PATH, ip, str(port), str(duration), str(Config.THREADS)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                return True
            except Exception as e:
                print(f"Attack failed: {e}")
                return False

class DataManager:
    @staticmethod
    def load_data():
        try:
            with open(Config.DATA_FILE, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "users": {},
                "admins": [str(Config.ADMIN_ID)],
                "attacks": [],
                "stats": {
                    "total_attacks": 0,
                    "blocked_attempts": 0
                }
            }

    @staticmethod
    def save_data(data):
        with open(Config.DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def update_user(user_id, updates):
        data = DataManager.load_data()
        user_id = str(user_id)
        if user_id not in data['users']:
            data['users'][user_id] = {
                "approved": False,
                "attack_count": 0,
                "limit": Config.MAX_ATTACK_LIMIT,
                "last_attack": None,
                "cooldown": Config.COOLDOWN_TIME
            }
        data['users'][user_id].update(updates)
        DataManager.save_data(data)
        return data['users'][user_id]

    @staticmethod
    def get_all_users():
        data = DataManager.load_data()
        return [uid for uid, user in data['users'].items() if user.get('approved')]

class FormatHelper:
    @staticmethod
    def style_text(text):
        style_map = {
            'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ',
            'f': 'ғ', 'g': 'ɢ', 'h': 'ʜ', 'i': 'ɪ', 'j': 'ᴊ',
            'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ', 'o': 'ᴏ',
            'p': 'ᴘ', 'q': 'ǫ', 'r': 'ʀ', 's': 's', 't': 'ᴛ',
            'u': 'ᴜ', 'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x', 'y': 'ʏ',
            'z': 'ᴢ'
        }
        return ''.join([style_map.get(c.lower(), c) for c in text])

    @staticmethod
    def format_caption(header, items):
        lines = [f"╔═ {header} ═╗"]
        for i, (key, value) in enumerate(items):
            prefix = "├" if i < len(items)-1 else "└"
            lines.append(f"{prefix}── {key}: {value}")
        lines.append("╚══════════════╝")
        return '\n'.join(lines)

class BroadcastManager:
    @staticmethod
    def send_broadcast(message, bot):
        users = DataManager.get_all_users()
        success = 0
        failed = 0
        
        for user_id in users:
            try:
                bot.send_message(user_id, message)
                success += 1
            except Exception as e:
                print(f"Failed to send to {user_id}: {e}")
                failed += 1
            time.sleep(0.1)
        
        return success, failed