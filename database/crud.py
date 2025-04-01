from database.init_db import async_session, User
from sqlalchemy.orm import attributes

import datetime


async def chek_user(user_id: int):
    async with async_session() as session:
        user = await session.get(User, user_id)
        if user is None:
            user = User(user_id=user_id, achievements={})
            session.add(user)
            await session.commit()

async def chek_today_achievement(user_id: int):
    async with async_session() as session:
        user = await session.get(User, user_id)
    user_achievements = user.achievements
    current_date = datetime.datetime.now().date().isoformat()
    if current_date in user_achievements:
        return False
    return True

async def add_achievement_to_db(user_id: int, achievement: str):
    current_date = datetime.datetime.now().date().isoformat()
    async with async_session() as session:
        user = await session.get(User, user_id)
        user.achievements[current_date] = achievement
        attributes.flag_modified(user, 'achievements')
        await session.commit()

async def get_today_achievement(user_id: int):
    current_date = datetime.datetime.now().date().isoformat()
    async with async_session() as session:
        user = await session.get(User, user_id)
    today_achievement = user.achievements.get(current_date, False)
    return today_achievement

async def get_statistics(user_id: int):
    async with async_session() as session:
        user = await session.get(User, user_id)
    return user.achievements
