from pathlib import Path
import sys

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers import card_router

PATH_STATIC = Path(__file__).parent / "static"

app = FastAPI()
app.include_router(card_router.router)
app.mount("/static", StaticFiles(directory=PATH_STATIC), name="static")


if __name__ == "__main__":
    import uvicorn
    import core.db.orm as orm
    import core.utils.logging_utils as logging_utils

    logging_utils.setup_logging()
    sys.excepthook = logging_utils.global_exception_hook
    orm.start_mappers()

    uvicorn.run(app, host="localhost", port=8000)
