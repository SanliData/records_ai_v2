# scripts/upap_capabilities_patch.ps1
# -*- coding: utf-8 -*-
$ErrorActionPreference = "Stop"

function Assert-RepoRoot {
    param([string]$Root)
    $mainPath = Join-Path $Root "backend\main.py"
    if (-not (Test-Path $mainPath)) {
        throw "Repo root not detected. Expected: $mainPath"
    }
}

function Ensure-Dir {
    param([string]$Path)
    if (-not (Test-Path $Path)) {
        New-Item -ItemType Directory -Path $Path | Out-Null
    }
}

function Write-Utf8NoBom {
    param(
        [string]$Path,
        [string]$Content
    )
    $dir = Split-Path $Path -Parent
    Ensure-Dir $dir

    # Write as UTF-8 without BOM using .NET
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path, $Content, $utf8NoBom)
}

function Get-Utf8BomStatus {
    param([string]$Path)
    if (-not (Test-Path $Path)) { return "MISSING" }
    $bytes = [System.IO.File]::ReadAllBytes($Path)
    if ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
        return "UTF8_BOM"
    }
    return "UTF8_NO_BOM_OR_OTHER"
}

function Add-Import-And-IncludeRouter {
    param(
        [string]$MainPath,
        [string]$ImportLine,
        [string]$IncludeLine
    )

    $text = [System.IO.File]::ReadAllText($MainPath, [System.Text.Encoding]::UTF8)

    if ($text -notmatch [regex]::Escape($ImportLine)) {
        # Insert imports after the last existing router import from backend.api.v1 if possible, else at top after standard imports.
        $lines = $text -split "`n", 0, "SimpleMatch"
        $insertAt = -1

        for ($i = 0; $i -lt $lines.Count; $i++) {
            if ($lines[$i] -match "from\s+backend\.api\.v1\..+\s+import\s+router\s+as\s+") {
                $insertAt = $i
            }
        }
        if ($insertAt -ge 0) {
            $newLines = @()
            for ($i = 0; $i -lt $lines.Count; $i++) {
                $newLines += $lines[$i]
                if ($i -eq $insertAt) {
                    $newLines += $ImportLine
                }
            }
            $text = ($newLines -join "`n")
        } else {
            # Fallback: prepend after first non-shebang/docstring block by finding first blank line after imports
            $text = $ImportLine + "`n" + $text
        }
    }

    if ($text -notmatch [regex]::Escape($IncludeLine)) {
        # Insert include_router near existing includes; try after upap_router include if present; else near end.
        $lines = $text -split "`n", 0, "SimpleMatch"

        $anchorIdx = -1
        for ($i = 0; $i -lt $lines.Count; $i++) {
            if ($lines[$i] -match "app\.include_router\(\s*upap_router\s*\)") {
                $anchorIdx = $i
            }
        }

        if ($anchorIdx -ge 0) {
            $newLines = @()
            for ($i = 0; $i -lt $lines.Count; $i++) {
                $newLines += $lines[$i]
                if ($i -eq $anchorIdx) {
                    $newLines += $IncludeLine
                }
            }
            $text = ($newLines -join "`n")
        } else {
            # Append at end with a safe newline
            if (-not $text.EndsWith("`n")) { $text += "`n" }
            $text += $IncludeLine + "`n"
        }
    }

    # Write back as UTF-8 no BOM
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($MainPath, $text, $utf8NoBom)
}

# -----------------------------
# Main
# -----------------------------
$root = (Get-Location).Path
Assert-RepoRoot -Root $root

# Paths
$apiDir = Join-Path $root "backend\api\v1"
$svcDir = Join-Path $root "backend\services\upap"
$storeDir = Join-Path $root "backend\storage\upap"
Ensure-Dir $apiDir
Ensure-Dir $svcDir
Ensure-Dir $storeDir

# 1) System Archive Store (file-based, minimal, atomic writes)
$systemArchiveStorePath = Join-Path $root "backend\services\upap\archive\system_archive_store.py"
$systemArchiveStore = @"
# -*- coding: utf-8 -*-
\"\"\"UPAP System Archive Store (v1)

File-based JSON store to keep a single canonical system record per product
and allow user records to reference that canonical record.

This is intentionally minimal and domain-agnostic.
\"\"\"

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
import json
import os
import uuid


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _atomic_write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + \".tmp\")
    data = json.dumps(payload, ensure_ascii=False, indent=2)
    tmp.write_text(data, encoding=\"utf-8\")
    os.replace(str(tmp), str(path))


def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {\"system_records\": {}, \"user_records\": {}, \"meta\": {\"created_at\": _utc_now_iso()}}
    raw = path.read_text(encoding=\"utf-8\")
    return json.loads(raw) if raw.strip() else {\"system_records\": {}, \"user_records\": {}, \"meta\": {\"created_at\": _utc_now_iso()}}


@dataclass(frozen=True)
class SystemArchivePaths:
    base_dir: Path

    @property
    def archive_file(self) -> Path:
        return self.base_dir / \"system_archive.json\"


class SystemArchiveStore:
    def __init__(self, base_dir: str = \"backend/storage/upap\") -> None:
        self.paths = SystemArchivePaths(base_dir=Path(base_dir))

    def load(self) -> Dict[str, Any]:
        return _read_json(self.paths.archive_file)

    def save(self, data: Dict[str, Any]) -> None:
        _atomic_write_json(self.paths.archive_file, data)

    def ensure_system_record(
        self,
        fingerprint: str,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        \"\"\"Create or return an existing canonical system record by fingerprint.\"\"\"
        data = self.load()
        system_records = data.setdefault(\"system_records\", {})

        # Find existing by fingerprint
        for sr_id, sr in system_records.items():
            if sr.get(\"fingerprint\") == fingerprint:
                return sr

        system_record_id = str(uuid.uuid4())
        record = {
            \"system_record_id\": system_record_id,
            \"fingerprint\": fingerprint,
            \"payload\": payload,
            \"price_low\": None,
            \"price_high\": None,
            \"created_at\": _utc_now_iso(),
            \"updated_at\": _utc_now_iso(),
            \"variants\": [],
        }
        system_records[system_record_id] = record
        data[\"system_records\"] = system_records
        self.save(data)
        return record

    def link_user_record(
        self,
        user_key: str,
        system_record_id: str,
        condition: Optional[str],
        notes: Optional[str],
    ) -> Dict[str, Any]:
        \"\"\"Create or update a user record link (user-specific fields only).\"\"\"
        data = self.load()
        user_records = data.setdefault(\"user_records\", {})
        user_id = f\"{user_key}:{system_record_id}\"

        user_records[user_id] = {
            \"user_id\": user_key,
            \"system_record_id\": system_record_id,
            \"condition\": condition,
            \"notes\": notes,
            \"updated_at\": _utc_now_iso(),
        }
        data[\"user_records\"] = user_records
        self.save(data)
        return user_records[user_id]
"@
Write-Utf8NoBom -Path $systemArchiveStorePath -Content $systemArchiveStore

# 2) Recognition Candidate Router (stub, returns placeholders)
$recognitionRouterPath = Join-Path $root "backend\api\v1\upap_recognition_router.py"
$recognitionRouter = @"
# -*- coding: utf-8 -*-
\"\"\"UPAP Recognition Router (v1 stub)

Creates recognition candidates for a given record_id.
This is domain-agnostic and intentionally conservative (suggestions only).
\"\"\"

from __future__ import annotations

from typing import Any, Dict, List
from fastapi import APIRouter
from pydantic import BaseModel, Field


router = APIRouter(prefix=\"/upap\", tags=[\"upap\"])


class RecognitionCandidateRequest(BaseModel):
    record_id: str = Field(..., description=\"Record ID returned by /upap/upload\")


@router.post(\"/recognition/candidate\", summary=\"Create recognition candidates (stub)\")
async def recognition_candidate(req: RecognitionCandidateRequest) -> Dict[str, Any]:
    # Placeholder response. Future: check system archive, then external lookup providers.
    return {
        \"status\": \"ok\",
        \"stage\": \"recognition_candidate\",
        \"record_id\": req.record_id,
        \"possible_matches\": [],
        \"confidence\": 0.0,
        \"source\": \"none\",
    }
"@
Write-Utf8NoBom -Path $recognitionRouterPath -Content $recognitionRouter

# 3) System Archive Router (minimal canonical record + user link)
$archiveSystemRouterPath = Join-Path $root "backend\api\v1\upap_system_archive_router.py"
$archiveSystemRouter = @"
# -*- coding: utf-8 -*-
\"\"\"UPAP System Archive Router (v1)

Creates/returns a canonical system record and optionally links it to a user.
User-specific fields (condition, notes) live only in user records.
\"\"\"

from __future__ import annotations

from typing import Any, Dict, Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.services.upap.archive.system_archive_store import SystemArchiveStore


router = APIRouter(prefix=\"/upap\", tags=[\"upap\"])

_store = SystemArchiveStore(base_dir=\"backend/storage/upap\")


class SystemArchiveConfirmRequest(BaseModel):
    record_id: str = Field(..., description=\"Record ID returned by /upap/upload\")
    fingerprint: str = Field(..., description=\"Canonical fingerprint (domain-agnostic unique key)\")
    payload: Dict[str, Any] = Field(default_factory=dict, description=\"Canonical metadata payload\")
    user_key: Optional[str] = Field(default=None, description=\"Optional user key (e.g., email)\")
    condition: Optional[str] = Field(default=None, description=\"User-only condition\")
    notes: Optional[str] = Field(default=None, description=\"User-only notes\")


@router.post(\"/archive/system/confirm\", summary=\"Confirm into system archive (canonical)\")
async def system_archive_confirm(req: SystemArchiveConfirmRequest) -> Dict[str, Any]:
    system_record = _store.ensure_system_record(fingerprint=req.fingerprint, payload=req.payload)

    user_record = None
    if req.user_key:
        user_record = _store.link_user_record(
            user_key=req.user_key,
            system_record_id=system_record[\"system_record_id\"],
            condition=req.condition,
            notes=req.notes,
        )

    return {
        \"status\": \"ok\",
        \"stage\": \"system_archive_confirm\",
        \"record_id\": req.record_id,
        \"system_record\": system_record,
        \"user_record\": user_record,
    }


@router.get(\"/archive/system/summary\", summary=\"System archive summary\")
async def system_archive_summary() -> Dict[str, Any]:
    data = _store.load()
    sr = data.get(\"system_records\", {})
    ur = data.get(\"user_records\", {})
    return {
        \"status\": \"ok\",
        \"system_records\": len(sr),
        \"user_records\": len(ur),
    }
"@
Write-Utf8NoBom -Path $archiveSystemRouterPath -Content $archiveSystemRouter

# 4) Dashboard Summary Router (JSON)
$dashboardApiRouterPath = Join-Path $root "backend\api\v1\upap_dashboard_api_router.py"
$dashboardApiRouter = @"
# -*- coding: utf-8 -*-
\"\"\"UPAP Dashboard API Router (v1)

Provides JSON-only observability endpoints. UI is client responsibility.
\"\"\"

from __future__ import annotations

from typing import Any, Dict
from pathlib import Path

from fastapi import APIRouter

from backend.services.upap.archive.system_archive_store import SystemArchiveStore


router = APIRouter(prefix=\"/upap\", tags=[\"upap\"])

_store = SystemArchiveStore(base_dir=\"backend/storage/upap\")


def _count_uploads() -> int:
    # Best-effort: count files under ./uploads if present
    p = Path(\"uploads\")
    if not p.exists():
        return 0
    return sum(1 for _ in p.rglob(\"*\") if _.is_file())


@router.get(\"/dashboard/summary\", summary=\"UPAP dashboard summary (JSON)\")
async def dashboard_summary() -> Dict[str, Any]:
    archive = _store.load()
    system_records = len(archive.get(\"system_records\", {}))
    user_records = len(archive.get(\"user_records\", {}))

    return {
        \"status\": \"ok\",
        \"uploads_total_estimate\": _count_uploads(),
        \"system_records\": system_records,
        \"user_records\": user_records,
    }
"@
Write-Utf8NoBom -Path $dashboardApiRouterPath -Content $dashboardApiRouter

# 5) Wire routers into backend/main.py
$mainPath = Join-Path $root "backend\main.py"

Add-Import-And-IncludeRouter `
    -MainPath $mainPath `
    -ImportLine "from backend.api.v1.upap_recognition_router import router as upap_recognition_router" `
    -IncludeLine "app.include_router(upap_recognition_router)"

Add-Import-And-IncludeRouter `
    -MainPath $mainPath `
    -ImportLine "from backend.api.v1.upap_system_archive_router import router as upap_system_archive_router" `
    -IncludeLine "app.include_router(upap_system_archive_router)"

Add-Import-And-IncludeRouter `
    -MainPath $mainPath `
    -ImportLine "from backend.api.v1.upap_dashboard_api_router import router as upap_dashboard_api_router" `
    -IncludeLine "app.include_router(upap_dashboard_api_router)"

# 6) UTF-8 BOM report
$report = @(
    @{ path = $systemArchiveStorePath; bom = (Get-Utf8BomStatus $systemArchiveStorePath) }
    @{ path = $recognitionRouterPath; bom = (Get-Utf8BomStatus $recognitionRouterPath) }
    @{ path = $archiveSystemRouterPath; bom = (Get-Utf8BomStatus $archiveSystemRouterPath) }
    @{ path = $dashboardApiRouterPath; bom = (Get-Utf8BomStatus $dashboardApiRouterPath) }
    @{ path = $mainPath; bom = (Get-Utf8BomStatus $mainPath) }
) | ForEach-Object { "[BOM] $($_.bom)  $($_.path)" }

$report | ForEach-Object { Write-Host $_ }

Write-Host "DONE. Next: rebuild container and verify:"
Write-Host '  curl.exe -s "$BASE/openapi.json" | Select-String -Pattern ''"/upap/recognition/candidate"'',''"/upap/archive/system/confirm"'',''"/upap/dashboard/summary"'' -SimpleMatch'
"@
