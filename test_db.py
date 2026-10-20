import asyncio
from fastapi import status, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from database import init_db, async_session, User, Task

async def run_test():
    await init_db()

    async with async_session() as session:
        stmt = select(Task).where(Task.id == 1)
        result = await session.execute(stmt)
        task = result.scalar_one_or_none()
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Not found"
            )
        await session.delete(task)
        await session.commit()
    
    print("Success! Testing script ended up great.")

if __name__ == "__main__":
    asyncio.run(run_test())
