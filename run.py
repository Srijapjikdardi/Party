"""
PartyPe - One-command startup script.
Run: python run.py
"""
import uvicorn
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print("=" * 50)
    print("🎉 PartyPe API Server Starting...")
    print(f"   URL: http://localhost:{port}")
    print(f"   API: http://localhost:{port}/api")
    print(f"   Docs: http://localhost:{port}/docs")
    print("=" * 50)
    print("\n📧 Demo Accounts:")
    print("   Diner:    demo@partype.com / demo123")
    print("   Merchant: merchant@partype.com / merchant123")
    print("   Waiter:   waiter@partype.com / waiter123")
    print("\n🔄 Server reloads on file changes (development mode)")
    print("   Press Ctrl+C to stop\n")

    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        reload_dirs=["backend", "frontend"],
    )
