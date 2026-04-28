from fastapi import FastAPI

from api.routers import llm,search

app = FastAPI(title="Evviva API")


app.include_router(llm.router)
app.include_router(search.router)


@app.get("/")
def root():
    return {
        "status": "online",
        "project": "evviva",
    }
