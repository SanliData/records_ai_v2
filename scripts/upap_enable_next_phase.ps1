$base = "backend/api/v1"

$files = @(
  "$base/upap_recognition_router.py",
  "$base/upap_archive_system_router.py",
  "$base/upap_dashboard_summary_router.py"
)

foreach ($f in $files) {
  if (-Not (Test-Path $f)) {
    Write-Host "Creating $f"
@"
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def placeholder():
    return {"status": "not_implemented"}
"@ | Set-Content $f -Encoding utf8
  }
}

Write-Host "UPAP next-phase skeleton created."
