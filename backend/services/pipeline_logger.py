"""
Pipeline Logger - Auditable Logging for AI Pipeline
Produces verifiable logs proving each step ran
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


class PipelineLogger:
    """
    Pipeline Logger
    
    Logs every step with:
    - preview_id
    - state
    - model_used
    - confidence
    - cost_estimate
    """
    
    def __init__(self, log_dir: Path = None):
        if log_dir is None:
            log_dir = Path("logs")
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "pipeline.log"
    
    def log_step(
        self,
        preview_id: str,
        state: str,
        step: str,
        data: Dict[str, Any]
    ):
        """
        Log pipeline step.
        
        Args:
            preview_id: Preview record ID
            state: Current state (e.g., "AI_ANALYZED")
            step: Step name (e.g., "LEVEL_1_START")
            data: Additional data (model_used, confidence, cost_estimate, etc.)
        """
        log_entry = {
            "preview_id": preview_id,
            "state": state,
            "step": step,
            "timestamp": datetime.utcnow().isoformat(),
            **data
        }
        
        # Write to file (NDJSON format)
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            logger.error(f"Failed to write pipeline log: {e}")
        
        # Also log to standard logger
        logger.info(f"[PIPELINE] {step}: {log_entry}")
    
    def get_logs(self, preview_id: str) -> list[Dict[str, Any]]:
        """Get all logs for a preview_id."""
        logs = []
        try:
            if not self.log_file.exists():
                return logs
            
            with open(self.log_file, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        entry = json.loads(line)
                        if entry.get("preview_id") == preview_id:
                            logs.append(entry)
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            logger.error(f"Failed to read pipeline logs: {e}")
        
        return logs


# Singleton
pipeline_logger = PipelineLogger()
