from pathlib import Path
import sys

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers import card_router
import core.db.orm as orm

orm.start_mappers()

PATH_STATIC = Path(__file__).parent / "static"


app = FastAPI()
app.include_router(card_router.router)
app.mount("/static", StaticFiles(directory=PATH_STATIC), name="static")


if __name__ == "__main__":
    import uvicorn
    import core.utils.logging_utils as logging_utils

    logging_utils.setup_logging()
    sys.excepthook = logging_utils.global_exception_hook

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
