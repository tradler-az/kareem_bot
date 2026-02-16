"""Task Planner"""
class Planner:
    def __init__(self): self.plans = {}
    def create(self, goal, steps): i = len(self.plans); self.plans[i] = {'goal': goal, 'steps': steps, 'pos': 0}; return i
    def next(self, pid): p = self.plans.get(pid); return p['steps'][p['pos']] if p and p['pos'] < len(p['steps']) else None
_p = Planner()
def get_planner(): return _p
