import sys

from fastapi import FastAPI

from app.routers import card_router

app = FastAPI()
app.include_router(card_router.router)


if __name__ == "__main__":
    import uvicorn
    import core.db.orm as orm
    import core.utils.logging_utils as logging_utils

    logging_utils.setup_logging()
    sys.excepthook = logging_utils.global_exception_hook
    orm.start_mappers()

    uvicorn.run(app, host="localhost", port=8000)
