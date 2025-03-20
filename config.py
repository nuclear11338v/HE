# config.py
import os

class Config:
    BLOCKED_PORTS = [17500, 20002, 20003, 20001, 30000] + list(range(1, 10000))
    ADMIN_ID = 7858368373
    REQUIRED_CHANNEL = "@TEAM_X_OG"
    MAX_ATTACK_LIMIT = 5
    BINARY_PATH = "MAIN/M"
    MAX_CONCURRENT_ATTACKS = 3
    COOLDOWN_TIME = 300
    THREADS = 900
    ATTACK_DURATION = 120
    
    PHOTOS = {
        "blocked": "https://graph.org/file/057a1200cd3d634c7b9e9-e911111fa3878bdbfe.jpg",
        "attack": "https://graph.org/file/1d7bff88e397c4718a823-94458c3ccba7a67303.jpg",
        "error": "https://graph.org/file/b65cb457b2fbcdf1c54aa-0f0df3979e416079f9.jpg",
        "success": "https://graph.org/file/4aba392e9834d6218d5e7-982052722b67e814b3.jpg"
    }
    
    DATA_FILE = "data.json"
    LOGS_FILE = "logs.json"
    STATS_FILE = "stats.json"

    @classmethod
    def validate_files(cls):
        required = [cls.BINARY_PATH, cls.DATA_FILE, cls.LOGS_FILE]
        for f in required:
            if not os.path.exists(f):
                print(f"Critical error: {f} not found!")
                exit(1)

Config.validate_files()
