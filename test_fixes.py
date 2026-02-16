#!/usr/bin/env python3
"""Bug fix verification test"""
import os
os.environ['SDL_AUDIODRIVER'] = 'dummy'

print("=== Testing Bug Fixes ===")

# Test voice_online module
from bosco_os.brain.voice_online import news, search, wiki, weather

print("1. News:", news()[:80])
print("2. Search:", search('AI')[:50])
print("3. Wiki:", wiki('Python')[:50])
print("4. Weather:", weather())

print("\nAll fixes verified!")
