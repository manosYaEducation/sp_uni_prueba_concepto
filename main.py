from fastapi import FastAPI, HTTPException, Depends, Path, Body
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import jwt

app = FastAPI(title="Simulador API Monedero & GiftCard")

# Simulador base de datos en memoria
fake_db = {
    "users": {"loyalty": "loyalty"},
    "monederos": {},
    "giftcards": {},
    "campaigns": {}
}

SECRET_KEY = "mi_clave_secreta"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/authorize")

# -------------------- MODELOS --------------------
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int = 300

class LoginRequest(BaseModel):
    username: str
    password: str

class Monedero(BaseModel):
    name: str
    totalAmount: int
    availableAmount: int

class GiftCard(BaseModel):
    number: str
    balance: int
    state: str = "ACTIVE"
    expirationDate: Optional[str] = None

class BalanceTransfer(BaseModel):
    amount: int
    source: str
    destination: str

# -------------------- AUTH --------------------
@app.post("/auth/authorize", response_model=TokenResponse)
def authorize(data: LoginRequest):
    if fake_db["users"].get(data.username) != data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    expiration = datetime.utcnow() + timedelta(minutes=5)
    token = jwt.encode({"sub": data.username, "exp": expiration}, SECRET_KEY, algorithm=ALGORITHM)
    return TokenResponse(access_token=token, expires_in=300)

# -------------------- MONEDEROS --------------------
@app.get("/monederos", response_model=List[Monedero])
def list_monederos(token: str = Depends(oauth2_scheme)):
    return list(fake_db["monederos"].values())

@app.post("/monederos", response_model=Monedero)
def create_monedero(monedero: Monedero, token: str = Depends(oauth2_scheme)):
    if monedero.name in fake_db["monederos"]:
        raise HTTPException(status_code=400, detail="Monedero ya existe")
    fake_db["monederos"][monedero.name] = monedero
    return monedero

# -------------------- GIFTCARDS --------------------
@app.post("/giftcards", response_model=GiftCard)
def create_giftcard(giftcard: GiftCard, token: str = Depends(oauth2_scheme)):
    if giftcard.number in fake_db["giftcards"]:
        raise HTTPException(status_code=400, detail="GiftCard ya existe")
    fake_db["giftcards"][giftcard.number] = giftcard
    return giftcard

@app.get("/giftcards", response_model=List[GiftCard])
def list_giftcards(token: str = Depends(oauth2_scheme)):
    return list(fake_db["giftcards"].values())

# -------------------- TRANSFERENCIA --------------------
@app.post("/transfer", response_model=dict)
def transfer_balance(data: BalanceTransfer, token: str = Depends(oauth2_scheme)):
    origen = fake_db["monederos"].get(data.source) or fake_db["giftcards"].get(data.source)
    destino = fake_db["monederos"].get(data.destination) or fake_db["giftcards"].get(data.destination)

    if not origen or not destino:
        raise HTTPException(status_code=404, detail="Origen o destino no existe")

    if origen.availableAmount < data.amount:
        raise HTTPException(status_code=400, detail="Fondos insuficientes")

    origen.availableAmount -= data.amount
    destino.availableAmount += data.amount

    return {"status": "ok", "transferido": data.amount}

# -------------------- INICIO --------------------
@app.get("/")
def read_root():
    return {"mensaje": "Simulador de API de Monedero y GiftCard funcionando"}
