from pathlib import Path

import uvicorn


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[1]
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        app_dir=str(project_root),
        reload_dirs=[str(project_root / "src")],
    )
