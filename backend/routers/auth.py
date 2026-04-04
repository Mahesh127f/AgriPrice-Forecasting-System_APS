from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

_users = [{"id":1,"name":"Ramesh Kumar","email":"ramesh@example.com","password":"farmer123","state":"Uttar Pradesh","district":"Agra","role":"farmer"}]
_nuid = 2

class LoginReq(BaseModel):
    email: str
    password: str

class RegisterReq(BaseModel):
    name: str
    email: str
    password: str
    state: str
    district: str

@router.post("/login")
async def login(req: LoginReq):
    user = next((u for u in _users if u["email"]==req.email and u["password"]==req.password), None)
    if not user:
        raise HTTPException(401,"Invalid credentials")
    return {"token": f"mock_token_{user['id']}", "user": {k:v for k,v in user.items() if k!="password"}}

@router.post("/register")
async def register(req: RegisterReq):
    global _nuid
    if any(u["email"]==req.email for u in _users):
        raise HTTPException(400,"Email already registered")
    user = {"id":_nuid,"name":req.name,"email":req.email,"password":req.password,
            "state":req.state,"district":req.district,"role":"farmer"}
    _users.append(user)
    _nuid += 1
    return {"token":f"mock_token_{user['id']}", "user":{k:v for k,v in user.items() if k!="password"}}

@router.get("/me")
async def me(token: str = ""):
    if not token.startswith("mock_token_"):
        raise HTTPException(401,"Invalid token")
    uid = int(token.replace("mock_token_",""))
    user = next((u for u in _users if u["id"]==uid), None)
    if not user:
        raise HTTPException(404,"User not found")
    return {k:v for k,v in user.items() if k!="password"}
