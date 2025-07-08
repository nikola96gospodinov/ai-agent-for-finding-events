from fastapi import FastAPI, Query, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.services.agent.tasks import run_agent_task
from app.models.user_profile_model import UserProfile
from celery.result import AsyncResult
from app.services.auth import get_current_user_profile, get_current_user, auth_service
from typing import Dict, Any

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
    user: Dict[str, Any] = Depends(get_current_user),
    user_profile: UserProfile = Depends(get_current_user_profile),
):
    # Check if user has exceeded their monthly run limit
    user_id = user.get('id')
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID not found in token")
    
    can_run = await auth_service.check_user_run_limit(user_id)
    if not can_run:
        raise HTTPException(
            status_code=429, 
            detail="Monthly run limit exceeded. You can only run the agent 2 times per calendar month."
        )
    
    # Record the run before starting the task
    run_recorded = await auth_service.record_user_run(user_id)
    if not run_recorded:
        raise HTTPException(
            status_code=500, 
            detail="Failed to record run. Please try again."
        )
    
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