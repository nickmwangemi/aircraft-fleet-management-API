from fastapi import APIRouter, status
from celery.result import AsyncResult
from app.api.tasks.report_tasks import generate_flight_report

router = APIRouter()


@router.post("/generate", status_code=status.HTTP_202_ACCEPTED)
def trigger_report_generation():
    task = generate_flight_report.delay()
    return {"task_id": task.id, "status": "Task has been submitted."}


@router.get("/status/{task_id}")
def get_report_status(task_id: str):
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result,
    }
    return result
