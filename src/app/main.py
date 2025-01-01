import sys

from fastapi import FastAPI

from .routers import card_router


# if "database.orm" not in sys.modules:
#     # ensure the orm is started:
#     import database.orm as orm

#     orm.start_mappers()


app = FastAPI()
app.include_router(card_router.router)
