"""Launch script for the FastAPI application.

This script serves as the entry point to run the FastAPI server.
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        factory=False,  # app_factory 방식이면 True
        log_level="info",
    )
