# backend/core/router_bus.py
# UTF-8, English only

from fastapi import APIRouter

class RouterBus:
    """
    Central router collector.
    All sub-routers register into this bus.
    """
    def __init__(self):
        self._routers = []

    def register(self, router: APIRouter):
        """Register a router from /api/v1/..."""
        if router not in self._routers:
            self._routers.append(router)

    def build(self) -> APIRouter:
        """Combine all routers into one master router."""
        master = APIRouter()
        for r in self._routers:
            master.include_router(r)
        return master


router_bus = RouterBus()
