import redis.asyncio as redis
import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi_limiter import FastAPILimiter
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from src.conf.messages import DB_CONFIG_ERROR, DB_CONNECT_ERROR, WELCOME_MESSAGE

from src.database.connect_db import get_db
from src.routes.auth import router as auth_router
from src.routes.fotos import router as foto_router
from src.routes.comments import router as comment_router
from src.routes.ratings import router as rating_router
from src.routes.transform_post import router as trans_router
from src.routes.tags import router as tag_router
from src.routes.users import router as users_router
from src.conf.config import settings

app = FastAPI()


@app.get("/", name="Project root")
def read_root():
    """
    The read_root function returns a dictionary with the key &quot;message&quot; and value WELCOMES_MESSAGE.
        This is used to display a welcome message when the user visits the root of our API.
    
    :return: A dictionary
    """
    return {"message": WELCOME_MESSAGE}


@app.on_event("startup")
async def startup():
    """
    The startup function is called when the application starts up.
    It's a good place to initialize things that are used by the app, like caches or databases.
    
    :return: A coroutine, so we need to wrap it in asyncio
    """
    redis_cache = await redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        password=settings.redis_password,
        db=0,
        encoding="utf-8",
        decode_responses=True
    )
    await FastAPILimiter.init(redis_cache)


@app.get("/api/healthchecker")
def healthchecker(db: Session = Depends(get_db)):
    """
    The healthchecker function is used to check the health of the database.
    It returns a welcome message if it can connect to the database, and an error message otherwise.
    
    :param db: Session: Pass the database session to the function
    :return: A dict with a message
    """
    try:
        result = db.execute(text("SELECT 1")).fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail=DB_CONFIG_ERROR)
        return {"message": WELCOME_MESSAGE}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=DB_CONNECT_ERROR)


app.include_router(auth_router, prefix='/api')
app.include_router(users_router, prefix='/api')
app.include_router(foto_router, prefix='/api')
app.include_router(trans_router, prefix='/api')
app.include_router(tag_router, prefix='/api')
app.include_router(comment_router, prefix='/api')
app.include_router(rating_router, prefix='/api')


if __name__ == '__main__':
    uvicorn.run(app='main:app', host='localhost', port=8000, reload=True)
