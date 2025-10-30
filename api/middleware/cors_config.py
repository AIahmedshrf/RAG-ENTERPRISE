"""
CORS Configuration
"""

from fastapi.middleware.cors import CORSMiddleware
import os


def setup_cors(app):
    """إعداد CORS"""
    
    # Development origins
    origins_dev = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    
    # Production origins (من environment)
    origins_prod = os.getenv("ALLOWED_ORIGINS", "").split(",")
    
    all_origins = origins_dev + [o for o in origins_prod if o]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=all_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
