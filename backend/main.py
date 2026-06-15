from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database import init_db
from routers import flags, configs, evaluate, sse

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing Database...")
    await init_db()
    print("Database initialized.")
    yield
    print("Shutting down server...")

app = FastAPI(
    title="Feature Flag Engine",
    version="1.0.0",
    lifespan=lifespan
)

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"], # In production, restrict this to your frontend domain
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(flags.router)
app.include_router(configs.router)
app.include_router(evaluate.router)
app.include_router(sse.router)

@app.get("/")
async def root():
    return {"status": "online", "message": "Feature Flag Engine is running."}