import asyncio

from app.services.agent.agent import agent
from app.services.avatars import user_profile_main, user_profile_creative, user_profile_sports, user_profile_family, user_profile_student, user_profile_main_other

if __name__ == "__main__":
    asyncio.run(agent(user_profile_main))
