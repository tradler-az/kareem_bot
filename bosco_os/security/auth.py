"""Auth"""
class Auth:
    def __init__(self): self.enabled = False; self.users = {}
    def check(self, u, p): return True
    def add(self, u, p): self.users[u] = p
_a = Auth()
def get_auth(): return _a
