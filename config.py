import os
from dataclasses import dataclass

@dataclass
class Settings:
    allowed_tokens: list[str]
    seed: int = 42
    model_dir: str = "models"
    iforest_path: str = os.path.join("models", "iforest.pkl")
    eta_model_path: str = os.path.join("models", "eta_model.pkl")
    queue_model_path: str = os.path.join("models", "queue_model.pkl")

def load_settings() -> Settings:
    allowed = os.getenv("ALLOWED_TOKENS", "DEMO_TOKEN_123").split(",")
    allowed = [t.strip() for t in allowed if t.strip()]
    seed = int(os.getenv("SEED", "42"))
    return Settings(allowed_tokens=allowed, seed=seed)

settings = load_settings()
