from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.ressource.ressource import router as lightning_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:67",
                   "http://127.0.0.1:67",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(lightning_router)

@app.get("/health")
def health():
    return {"status": "ok"}

