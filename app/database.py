from sqlalchemy.ext.asyncio import create_async_engine , AsyncSession
from sqlalchemy.orm import sessionmaker
from config import DB_URL





engine = create_async_engine(DB_URL)

AsyncSessionMaker = sessionmaker(engine , expire_on_commit=False , class_= AsyncSession)


async def setup_db():
    async with AsyncSessionMaker() as session:
        yield session