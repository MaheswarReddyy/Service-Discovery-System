from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


# ==========================================
# APPLICATION CORS CONFIGURATION
# ==========================================
def configure_cors(app: FastAPI) -> None:
    # Allow local Vite frontend origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:4173",
            "http://127.0.0.1:4173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
