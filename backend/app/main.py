import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.database import Base, engine
from app.routes import contracts, verification, payments, buyer, mcp
from app.state_machine import StateMachineError
from app.paypal_client import PayPalClientError

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Outcome Exchange API",
    description="Buyer-Governed Multi-Agent AI Fulfillment with PayPal Authorization & Deterministic Verification",
    version="0.3.0"
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
@app.exception_handler(StateMachineError)
async def state_machine_error_handler(request: Request, exc: StateMachineError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "STATE_MACHINE_ERROR", "detail": exc.message}
    )

@app.exception_handler(PayPalClientError)
async def paypal_client_error_handler(request: Request, exc: PayPalClientError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "PAYPAL_API_ERROR", "detail": exc.message, "details": exc.details}
    )

# Include API routes
app.include_router(buyer.router)
app.include_router(mcp.router)
app.include_router(contracts.router)
app.include_router(verification.router)
app.include_router(payments.router)

# Mount static demo UI
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def serve_index():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Outcome Exchange API running. Visit /docs for Swagger UI."}

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Outcome Exchange Core Backend",
        "paypal_environment": settings.paypal_env,
        "paypal_live_configured": settings.has_real_paypal_credentials,
        "llm_provider": settings.llm_provider,
        "llm_live_configured": settings.has_real_llm_credentials,
        "database_connected": True,
        "version": "0.2.0"
    }
