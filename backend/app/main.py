from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core import config

app = FastAPI(title="AfterBuy API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {"message": "AfterBuy backend is running"}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "services": {
            "api": "ok",
            "supabase": "configured" if config.SUPABASE_URL and config.SUPABASE_SERVICE_KEY else "not_configured",
            "openai": "configured" if config.OPENAI_API_KEY else "not_configured",
            "market_data_provider": "configured" if config.SERPAPI_API_KEY else "not_configured",
        },
    }
