from datetime import datetime

# Simple centralized log function
def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")