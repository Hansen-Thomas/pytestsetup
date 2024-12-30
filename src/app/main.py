from fastapi import FastAPI

from .routers import card_router

app = FastAPI()
app.include_router(card_router.router)



def main():
    print("Hello from pytestsetup!")


if __name__ == "__main__":
    main()
