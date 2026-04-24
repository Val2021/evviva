from fastapi import FastAPI

from api.routers import llm

app = FastAPI(title="Evviva API")


app.include_router(llm.router)


@app.get("/")
def root():
    return {
        "status": "online",
        "project": "evviva",
    }
