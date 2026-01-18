from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
UPLOAD_HTML = REPO_ROOT / "frontend" / "upload.html"

app = FastAPI(title="Records_AI_V2", version="2.0.0")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
async def root():
    return FileResponse(
        UPLOAD_HTML,
        media_type="text/html",
        headers={"Cache-Control": "no-store"}
    )

# Serve static frontend files
app.mount("/ui", StaticFiles(directory="frontend", html=True), name="ui")
