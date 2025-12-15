$base = "backend/services/upap"

$stages = @(
    @{ file = "$base/auth/auth_stage.py";     name = "auth" },
    @{ file = "$base/upload/upload_stage.py";   name = "upload" },
    @{ file = "$base/process/process_stage.py";  name = "process" },
    @{ file = "$base/archive/archive_stage.py";  name = "archive" },
    @{ file = "$base/publish/publish_stage.py";  name = "publish" }
)

foreach ($s in $stages) {

    $f = $s.file
    $stageName = $s.name

    Write-Host "Patching $f ..." -ForegroundColor Cyan

    if (-Not (Test-Path $f)) {
        Write-Host "File not found: $f" -ForegroundColor Red
        continue
    }

    $content = Get-Content $f -Raw

    # Add name attribute if missing
    if ($content -notmatch "name\s*=") {
        $content = $content -replace "(class\s+\w+\s*\([^\)]*\)\s*:)", "`$1`r`n    name = '$stageName'"
    }

    # Add validate_input if missing
    if ($content -notmatch "def\s+validate_input") {
        $validateInput = @"
    def validate_input(self, context: dict) -> None:
        if not isinstance(context, dict):
            raise ValueError("Context must be a dict")
"@
        $content += "`r`n$validateInput"
    }

    # Add validate_output if missing
    if ($content -notmatch "def\s+validate_output") {
        $validateOutput = @"
    def validate_output(self, result: dict) -> None:
        if not isinstance(result, dict):
            raise ValueError("Stage output must be a dict")
"@
        $content += "`r`n$validateOutput"
    }

    # Save patched file
    Set-Content -Path $f -Value $content -Encoding UTF8
    Write-Host "Patched successfully." -ForegroundColor Green
}

Write-Host "`nALL STAGES PATCHED. Now run:" -ForegroundColor Yellow
Write-Host "python -m backend.services.upap.engine.upap_validation" -ForegroundColor Yellow
