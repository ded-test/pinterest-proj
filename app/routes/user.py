from fastapi import APIRouter

app = APIRouter()


@app.post("/api/registration")
async def registration(db: AsyncSession = Depends(get_db_session))
    