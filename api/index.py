import os
import sys

# Add the project root to sys.path so we can import from 'backend'
# This is necessary because Vercel runs from the root but imports might be relative
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if path not in sys.path:
    sys.path.append(path)

from backend.main import app

# Vercel needs the app object
# No need to do app.run() or anything, Vercel's Python runtime handles it.
