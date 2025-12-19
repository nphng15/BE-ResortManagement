from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.customer import cart, history, zalopay
from app.routers.public import resorts, search, roomtypes, auth
from app.routers.partner import partner
from app.routers.admin import withdraw, partner_approval, account_management

app = FastAPI()

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

# Admin routes
app.include_router(withdraw.router)
app.include_router(partner_approval.router)
app.include_router(account_management.router)
