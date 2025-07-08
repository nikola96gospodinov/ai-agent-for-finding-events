from fastapi import FastAPI, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.services.agent.tasks import run_agent_task
from app.models.user_profile_model import UserProfile
from celery.result import AsyncResult
from app.services.auth import get_current_user_profile

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI Agent for Event Discovery",
    version="0.1.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Change to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}

@app.post("/run-agent")
async def run_agent_endpoint(
    only_highly_relevant: bool = Query(False, description="Event only highly relevant to the user or not"),
    user_profile: UserProfile = Depends(get_current_user_profile),
):
    task = run_agent_task.delay(dict(user_profile), only_highly_relevant)
    return {"task_id": task.id, "status": "Task submitted"}

@app.get("/task-status/{task_id}")
async def get_task_status(task_id: str):
    task_result = AsyncResult(task_id)
    if task_result.state == 'PENDING':
        return {"status": "pending"}
    elif task_result.state == 'SUCCESS':
        return {"status": "completed", "result": task_result.result}
    elif task_result.state == 'FAILURE':
        return {"status": "failed", "error": str(task_result.result)}
    else:
        return {"status": task_result.state}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)