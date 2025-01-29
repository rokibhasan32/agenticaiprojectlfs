# config.py
import os

# Groq API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")
GROQ_API_URL = os.getenv("GROQ_API_URL", "https://api.groq.com/openai/v1/chat/completions")

# PhiData API Configuration
PHI_API_KEY = os.getenv("PHI_API_KEY", "phi-Pz6G6HhgJoQgfMxsd_mR_ncURCnIV04zHhzdNivArUg")

# Llama model name
LLAMA_MODEL = "llama-3.3-70b-versatile"

# Library Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///library.db")