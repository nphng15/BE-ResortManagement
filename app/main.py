from fastapi import FastAPI
from app.routers.customer import cart, history, zalopay
from app.routers.public import resorts, search, roomtypes, auth
from app.routers.partner import partner
from app.routers.admin import withdraw, partner_approval, account_management

app = FastAPI()

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
