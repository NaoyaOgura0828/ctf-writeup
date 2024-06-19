from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
security = HTTPBasic()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user.name)
    if db_user:
        raise HTTPException(status_code=400, detail="User already registered")
    return crud.create_user(db=db, user=user)

# It's different in real environ!
@app.post("/freeswitch")
def freeswitch(request: Request, credentials: Annotated[HTTPBasicCredentials, Depends(security)], db: Session = Depends(get_db)):
    
    # ACL and CRED check here!
    users = crud.get_all_user(db)
    users_xml = ""
    for user in users:
        users_xml += f"""
            <user id="{user.name}">
                <params>
                    <param name="password" value="{user.password}"/>
                </params>
            </user>
        """

    freeswitch_xml = f"""
<document type="freeswitch/xml">
    <section name="directory">
        <domain name="iinevoip">
            {users_xml}
        </domain>
    </section>
</document>
"""
    return Response(content=freeswitch_xml, media_type="application/xml")

app.mount("/", StaticFiles(directory="./login_system/frontend/build", html=True), name="static")