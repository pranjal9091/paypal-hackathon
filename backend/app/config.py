import os
from pydantic import BaseModel
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

class Settings(BaseModel):
    paypal_env: str = os.getenv("PAYPAL_ENV", "sandbox")
    paypal_client_id: str = os.getenv("PAYPAL_CLIENT_ID", "")
    paypal_client_secret: str = os.getenv("PAYPAL_CLIENT_SECRET", "")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./outcome_exchange.db")
    llm_provider: str = os.getenv("LLM_PROVIDER", "mock")
    llm_api_key: str = os.getenv("LLM_API_KEY", "")
    llm_model: str = os.getenv("LLM_MODEL", "gemini-2.5-flash")
    api_host: str = os.getenv("API_HOST", "127.0.0.1")
    api_port: int = int(os.getenv("API_PORT", "8000"))

    @property
    def has_real_paypal_credentials(self) -> bool:
        cid = self.paypal_client_id.strip()
        sec = self.paypal_client_secret.strip()
        return bool(cid and sec and cid != "your_sandbox_client_id_here")

    @property
    def paypal_base_url(self) -> str:
        if self.paypal_env.lower() == "production":
            return "https://api-m.paypal.com"
        return "https://api-m.sandbox.paypal.com"

settings = Settings()
