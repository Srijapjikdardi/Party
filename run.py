"""
PartyPe - One-command startup script.
Run: python run.py
"""
import os
import sys
from pathlib import Path

import uvicorn

# backend/ is the import root for the `app` package (backend/app/...),
# not a package itself, so it goes on sys.path rather than being
# imported as `backend.app`.
sys.path.insert(0, str(Path(__file__).resolve().parent / "backend"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print("=" * 50)
    print("🎉 PartyPe API Server Starting...")
    print(f"   URL: http://localhost:{port}")
    print(f"   API (v1): http://localhost:{port}/api/v1")
    print(f"   API (legacy alias): http://localhost:{port}/api")
    print(f"   Docs: http://localhost:{port}/docs")
    print("=" * 50)
    print("\n📧 Demo Accounts:")
    print("   Diner:    demo@partype.com / demo123")
    print("   Merchant: merchant@partype.com / merchant123")
    print("   Waiter:   waiter@partype.com / waiter123")
    print("\n🔄 Server reloads on file changes (development mode)")
    print("   Press Ctrl+C to stop\n")

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        reload_dirs=["backend", "frontend"],
        app_dir="backend",
    )
