from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models import RedfishResponse
from app.redfish_client import RedfishClient
from app.state import telemetry
from app.database import save_telemetry, get_recent_telemetry
from app.anomaly import AnomalyDetector
from app.health import ServerHealthAnalyzer
from app.predictive import PredictiveMaintenance


class SimulationRequest(BaseModel):
    mode: str


router = APIRouter(prefix="/api/redfish", tags=["Redfish"])
client = RedfishClient()
anomaly_detector = AnomalyDetector()
health_analyzer = ServerHealthAnalyzer()
predictive_analyzer = PredictiveMaintenance()


@router.get("/root", response_model=RedfishResponse)
def get_root():
    try:
        data = client.get_root()
        return RedfishResponse(endpoint="/redfish/v1/", data=data)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc))


@router.get("/systems", response_model=RedfishResponse)
def get_systems():
    try:
        data = client.get_systems()
        return RedfishResponse(endpoint="/redfish/v1/Systems", data=data)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc))


@router.get("/chassis", response_model=RedfishResponse)
def get_chassis():
    try:
        data = client.get_chassis()
        return RedfishResponse(endpoint="/redfish/v1/Chassis", data=data)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc))


@router.get("/managers", response_model=RedfishResponse)
def get_managers():
    try:
        data = client.get_managers()
        return RedfishResponse(endpoint="/redfish/v1/Managers", data=data)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc))


@router.get("/telemetry")
def get_telemetry():
    try:
        return telemetry.collect()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc))


@router.post("/monitoring/collect")
def collect_telemetry():
    try:
        data = telemetry.collect()
        save_telemetry(data)

        return {
            "status": "saved",
            "data": data,
        }
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc))


@router.get("/monitoring/history")
def telemetry_history(limit: int = 100):
    try:
        limit = min(max(limit, 1), 1000)
        data = get_recent_telemetry(limit)

        return {
            "count": len(data),
            "data": data,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/monitoring/anomalies")
def detect_anomalies():
    try:
        return anomaly_detector.detect()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/monitoring/health")
def server_health():
    try:
        return health_analyzer.analyze()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/monitoring/predictive")
def get_predictive_maintenance():
    try:
        return predictive_analyzer.analyze()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/monitoring/simulation")
def set_simulation_mode(request: SimulationRequest):
    try:
        telemetry.set_simulation_mode(request.mode)

        return {
            "status": "updated",
            "mode": request.mode,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))