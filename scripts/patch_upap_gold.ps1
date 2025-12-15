$stages = @(
    "backend/services/upap/auth/auth_stage.py",
    "backend/services/upap/upload/upload_stage.py",
    "backend/services/upap/process/process_stage.py",
    "backend/services/upap/archive/archive_stage.py",
    "backend/services/upap/publish/publish_stage.py"
)

Write-Host "=== APPLYING GOLD STANDARD PATCH TO UPAP STAGES ===" -ForegroundColor Cyan

foreach ($path in $stages) {

    if (-not (Test-Path $path)) {
        Write-Host "Skipping (not found): $path" -ForegroundColor Yellow
        continue
    }

    Write-Host "Patching: $path" -ForegroundColor Green

    $text = Get-Content $path -Raw

    # Add StageInterface inheritance if missing
    if ($text -notmatch "class .*StageInterface") {
        $text = $text -replace "class (\w+Stage)\(", "from backend.services.upap.engine.stage_interface import StageInterface\n\nclass `$1(StageInterface)("
    }

    # Add name attribute if missing
    if ($text -notmatch "name\s*=") {
        $text = $text -replace "class (\w+Stage\S*)\:", "class `$1:\n    name = '`$1'`n"
    }

    # Standardize run signature (context dict)
    $text = $text -replace "def run\([^\)]*\)", "def run(self, context: dict) -> dict"

    # Add universal validate_input() if missing
    if ($text -notmatch "def validate_input") {
        $validate = @"
    def validate_input(self, context: dict) -> None:
        if not isinstance(context, dict):
            raise ValueError("Stage context must be a dict")
"@
        $text += "`n$validate"
    }

    Set-Content -Path $path -Value $text -Encoding UTF8
}

Write-Host "`nALL STAGES PATCHED TO GOLD STANDARD." -ForegroundColor Cyan
Write-Host "Now run:" -ForegroundColor Cyan
Write-Host "python -m backend.services.upap.engine.upap_validation" -ForegroundColor Cyan
