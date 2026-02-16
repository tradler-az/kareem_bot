from datetime import datetime

def log_command(command, result):
    with open("logs/history.log", "a") as f:
        f.write(f"{datetime.now()} | {command} | {result}\n")