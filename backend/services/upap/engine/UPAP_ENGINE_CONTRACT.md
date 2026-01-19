# UPAP Engine Public Contract

## FROZEN INTERFACE (DO NOT MODIFY WITHOUT ARCHITECT REVIEW)

### Public Methods

#### `run_stage(stage_name: str, context: dict) -> dict`
- **Purpose**: Execute a single registered stage
- **Parameters**:
  - `stage_name`: Must match registered stage `.name` attribute
  - `context`: Stage-specific context dictionary
- **Returns**: Stage output dictionary
- **Raises**: `RuntimeError` if stage not registered

#### `run_archive(record_id: str) -> dict`
- **Purpose**: Execute archive stage (convenience method)
- **Parameters**: `record_id` (string UUID)
- **Returns**: `{"status": "ok", "stage": "archive", "record_id": ...}`
- **Implementation**: Calls `run_stage("archivestage", {"record_id": record_id})`

#### `run_publish(record_id: str) -> dict`
- **Purpose**: Execute publish stage (convenience method)
- **Parameters**: `record_id` (string UUID)
- **Returns**: `{"status": "ok", "stage": "publish", "record_id": ...}`
- **Implementation**: Calls `run_stage("publishstage", {"record_id": record_id})`

### Registered Stages (Default)

- `"archivestage"` - ArchiveStage (always registered)
- `"publishstage"` - PublishStage (always registered)
- `"ocr"` - OCRStage (if `UPAP_ENABLE_OCR=true`)
- `"ai"` - AIStage (if `UPAP_ENABLE_AI=true`)

### Non-Public (DO NOT CALL FROM ROUTERS)

- `register_stage()` - Internal use only
- `stages` - Internal dictionary
- Any other methods or attributes

### Router Contract

Routers MUST:
1. Call ONLY public methods listed above
2. NOT assume stage registration (check env vars)
3. NOT call internal engine methods
4. Handle `RuntimeError` for missing stages

### Stage Registration

Stages are registered at engine initialization. Routers cannot register stages.
