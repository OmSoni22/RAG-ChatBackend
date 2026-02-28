from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .user_model import User

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user: User) -> User:
        self.session.add(user)
        await self.session.flush()  # Generate ID
        await self.session.refresh(user)  # Refresh object with new ID
        return user

    async def get_all(self):
        result = await self.session.execute(select(User))
        return result.scalars().all()
