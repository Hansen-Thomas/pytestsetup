from fastapi import FastAPI

from app.routers import card_router

app = FastAPI()
app.include_router(card_router.router)


if __name__ == "__main__":
    import uvicorn

    import core.db.orm as orm

    orm.start_mappers()

    uvicorn.run(app, host="localhost", port=8000)
