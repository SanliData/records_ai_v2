"""
Root entrypoint wrapper for Cloud Run buildpacks.
This file allows the Python buildpack to detect the application entrypoint.
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Import and run the actual application
from backend.main import app

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)



