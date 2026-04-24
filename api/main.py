from fastapi import FastAPI

app = FastAPI(title="Evviva API")


@app.get("/")
def root():
    return {
        "status": "online",
        "project": "evviva",
    }
