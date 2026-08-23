import os
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=os.getenv("SLL_HOST", "0.0.0.0"),
        port=int(os.getenv("SLL_PORT", "8787")),
        reload=os.getenv("SLL_RELOAD", "0") in {"1", "true", "True"},
    )
