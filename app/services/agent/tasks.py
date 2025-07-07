from app.core.celery_app import celery_app
from app.services.agent.agent import agent
from app.models.user_profile_model import UserProfile
import asyncio

@celery_app.task(name='app.services.agent.tasks.run_agent_task')
def run_agent_task(user_profile_dict, only_highly_relevant: bool = False):
    user_profile = UserProfile(**user_profile_dict)
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(agent(user_profile, only_highly_relevant)) 