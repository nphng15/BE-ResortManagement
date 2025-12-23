from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.routers.customer import cart, history, zalopay
from app.routers.public import resorts, search, roomtypes, auth
from app.routers.partner import partner, room_management
from app.routers.admin import withdraw, partner_approval, account_management

app = FastAPI()


class CatchAllExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as exc:
            print(f"Unhandled exception: {type(exc).__name__}: {exc}")
            import traceback
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"detail": f"Internal server error: {str(exc)}"},
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "*",
                    "Access-Control-Allow-Headers": "*",
                }
            )


# Add exception middleware first (runs last)
app.add_middleware(CatchAllExceptionMiddleware)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Trong production nên giới hạn domain cụ thể
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Backend is running"}

# Auth routes
app.include_router(auth.router)

# Public routes
app.include_router(search.router)
app.include_router(resorts.router)
app.include_router(roomtypes.router)

# Customer routes
app.include_router(cart.router)
app.include_router(history.router)
app.include_router(zalopay.router)

# Partner routes
app.include_router(partner.router)
app.include_router(room_management.router)

# Admin routes
app.include_router(withdraw.router)
app.include_router(partner_approval.router)
app.include_router(account_management.router)
