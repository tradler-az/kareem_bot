"""
Bosco Core - Arc Reactor Visual Interface
JARVIS-style arc reactor visualization
"""

import math
import time


class ArcReactor:
    """JARVIS-style arc reactor visualization"""
    
    def __init__(self):
        self.status = "idle"
        self.phase = 0
        self.status_colors = {
            "idle": "blue",
            "listening": "green",
            "processing": "yellow",
            "speaking": "cyan",
            "error": "red",
        }
    
    def draw(self):
        """Draw ASCII arc reactor"""
        self.phase += 0.1
        pulse = int(math.sin(self.phase) * 2)
        chars = [' ', '.', 'o', 'O', '@']
        size = 15
        output = []
        
        for y in range(-size, size + 1):
            row = ""
            for x in range(-size * 2, size * 2 + 1):
                dist = math.sqrt(x**2 + y**2)
                if dist < size - 2 + pulse:
                    char_idx = min(int(dist / size * len(chars)), len(chars) - 1)
                    row += chars[char_idx]
                else:
                    row += " "
            output.append(row)
        
        status = "●" if self.status == "idle" else "◉"
        print("\033[2J\033[H")
        print("\033[96m" + "=" * 50)
        print("          BOSCO CORE - ARC REACTOR")
        print("=" * 40 + "\033[0m")
        for row in output:
            print(f"{row.center(50)}")
        print(f"Status: \033[96m{status}\033[0m {self.status.upper()}")
        time.sleep(0.1)
    
    def set_status(self, status: str):
        self.status = status


_arc_reactor = ArcReactor()


def set_status(status: str):
    _arc_reactor.set_status(status)


if __name__ == "__main__":
    for status in ["idle", "listening", "processing", "speaking"]:
        _arc_reactor.set_status(status)
        for _ in range(10):
            _arc_reactor.draw()

