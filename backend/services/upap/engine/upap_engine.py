from backend.services.upap.archive.archive_stage import ArchiveStage
from backend.services.upap.publish.publish_stage import PublishStage
import os


class UPAPEngine:
    """
    UPAP Pipeline Engine - FROZEN PUBLIC CONTRACT
    
    Public Methods (DO NOT MODIFY WITHOUT ARCHITECT REVIEW):
    - run_stage(stage_name: str, context: dict) -> dict
    - run_archive(record_id: str) -> dict
    - run_publish(record_id: str) -> dict
    
    See UPAP_ENGINE_CONTRACT.md for full contract documentation.
    """
    
    def __init__(self):
        self.stages = {}

        # ZORUNLU ÇEKİRDEK
        self.register_stage(ArchiveStage())
        self.register_stage(PublishStage())

        # OPSİYONEL (ENV ile)
        if os.getenv("UPAP_ENABLE_OCR") == "true":
            from backend.services.upap.ocr.ocr_stage import OCRStage
            self.register_stage(OCRStage())

        if os.getenv("UPAP_ENABLE_AI") == "true":
            from backend.services.upap.ai.ai_stage import AIStage
            self.register_stage(AIStage())

    def register_stage(self, stage):
        """
        INTERNAL USE ONLY - Do not call from routers.
        Register a stage for pipeline execution.
        """
        if not hasattr(stage, "name"):
            raise RuntimeError(f"{stage.__class__.__name__} missing .name")
        self.stages[stage.name] = stage

    def run_stage(self, stage_name: str, context: dict):
        """
        PUBLIC METHOD - Execute a single registered stage.
        
        Args:
            stage_name: Must match registered stage .name attribute
            context: Stage-specific context dictionary
            
        Returns:
            Stage output dictionary
            
        Raises:
            RuntimeError: If stage not registered
        """
        if stage_name not in self.stages:
            raise RuntimeError(f"Stage not registered: {stage_name}")
        return self.stages[stage_name].run(context)

    def run_archive(self, record_id: str):
        """
        PUBLIC METHOD - Execute archive stage (convenience method).
        
        Args:
            record_id: String UUID of record to archive
            
        Returns:
            {"status": "ok", "stage": "archive", "record_id": ...}
        """
        return self.run_stage("archivestage", {"record_id": record_id})

    def run_publish(self, record_id: str):
        """
        PUBLIC METHOD - Execute publish stage (convenience method).
        
        Args:
            record_id: String UUID of record to publish
            
        Returns:
            {"status": "ok", "stage": "publish", "record_id": ...}
        """
        return self.run_stage("publishstage", {"record_id": record_id})


# SINGLETON
upap_engine = UPAPEngine()
