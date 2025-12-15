# -*- coding: utf-8 -*-
"""
StageInterface
Base class for all UPAP pipeline stages.

Each stage must:
- validate_input(payload)
- run(context)
"""

from typing import Any, Dict
from abc import ABC, abstractmethod


class StageInterface(ABC):
    """
    Abstract interface for all pipeline stages.

    Each stage must:
    - Validate its expected input keys
    - Accept a dictionary as input (`context`)
    - Return a dictionary as output for the next stage
    """

    name: str = "UnnamedStage"

    @abstractmethod
    def validate_input(self, payload: Dict[str, Any]) -> None:
        """
        Validate required inputs for this stage.
        Should raise ValueError if required keys are missing or invalid.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__}.validate_input() must be implemented"
        )

    @abstractmethod
    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the business logic of the stage.
        Must return: dict (context for the next stage)
        """
        raise NotImplementedError(
            f"{self.__class__.__name__}.run() must be implemented"
        )
