from fastapi import APIRouter, BackgroundTasks, Query

from ..schemas import (
    ClientLogEntry,
    FeedbackPayload,
    FeedbackRequest,
    FeedbackResponse,
    LogsPayload,
    RecommendationsPayload,
    SettingsResponse,
    SettingsUpdate,
    SyncJobResponse,
    TropeExtractionResponse,
    TropeRecommendationsPayload,
)
from ..services.feedback_service import fetch_feedback, record_feedback
from ..services.log_service import fetch_logs, record_client_log
from ..services.settings_service import get_settings_snapshot, update_settings
from ..services.sync_service import get_last_job, get_recommendations, run_sync_job, start_sync_job
from ..services.trope_service import extract_tropes, get_trope_recommendations

router = APIRouter()


@router.get("/settings", response_model=SettingsResponse)
def read_settings() -> SettingsResponse:
    return get_settings_snapshot()


@router.post("/settings", response_model=SettingsResponse)
def write_settings(payload: SettingsUpdate) -> SettingsResponse:
    response = update_settings(payload)
    return response


@router.post("/abs/sync", response_model=SyncJobResponse)
def trigger_sync(background_tasks: BackgroundTasks) -> SyncJobResponse:
    job = start_sync_job()
    background_tasks.add_task(run_sync_job, job)
    return SyncJobResponse(
        id=job.id,
        job_type=job.job_type,
        status=job.status,
        message=job.message,
        started_at=job.started_at,
        finished_at=job.finished_at,
    )


@router.get("/abs/status", response_model=SyncJobResponse | None)
def get_sync_status() -> SyncJobResponse | None:
    job = get_last_job()
    if not job:
        return None
    return SyncJobResponse(
        id=job.id,
        job_type=job.job_type,
        status=job.status,
        message=job.message,
        started_at=job.started_at,
        finished_at=job.finished_at,
    )


@router.get("/recommendations", response_model=RecommendationsPayload)
def recommendations(limit: int = Query(10, ge=1, le=25)) -> RecommendationsPayload:
    items = get_recommendations(limit)
    return RecommendationsPayload(items=items)


@router.get("/logs", response_model=LogsPayload)
def read_logs(level: str | None = None, source: str | None = None) -> LogsPayload:
    return fetch_logs(level=level, source=source)


@router.post("/logs/client", response_model=dict)
def write_client_log(payload: ClientLogEntry) -> dict:
    entry = record_client_log(payload)
    return {"status": "recorded", "log": entry.dict()}


@router.post("/feedback", response_model=FeedbackResponse)
def submit_feedback(payload: FeedbackRequest) -> FeedbackResponse:
    return record_feedback(payload)


@router.get("/feedback", response_model=FeedbackPayload)
def list_feedback() -> FeedbackPayload:
    return fetch_feedback()


@router.post("/tropes/extract", response_model=TropeExtractionResponse)
def trigger_trope_extraction(background_tasks: BackgroundTasks) -> TropeExtractionResponse:
    background_tasks.add_task(extract_tropes, False)
    return TropeExtractionResponse(message="Trope extraction job queued")


@router.post("/tropes/refresh", response_model=TropeExtractionResponse)
def refresh_tropes(background_tasks: BackgroundTasks) -> TropeExtractionResponse:
    background_tasks.add_task(extract_tropes, True)
    return TropeExtractionResponse(message="Trope extraction refresh queued", status="queued")


@router.get("/discovery/trope-feed", response_model=TropeRecommendationsPayload)
def trope_feed(limit: int = Query(10, ge=1, le=25)) -> TropeRecommendationsPayload:
    items = get_trope_recommendations(limit)
    return TropeRecommendationsPayload(items=items)
