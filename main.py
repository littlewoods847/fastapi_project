from fastapi import FastAPI, Depends, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Float
from database import SessionLocal, engine, Base

# 1. Define the Database Model
class DBItem(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    price = Column(Float)

# 2. Create the Database Tables
Base.metadata.create_all(bind=engine)

# 3. CREATE THE APP
app = FastAPI()

# 4. Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# 5. Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- ROUTES ---

@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    items = db.query(DBItem).all()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"items": items}
    )

@app.post("/add-item/")
def add_item(search: str = Form(...), db: Session = Depends(get_db)):
    new_item = DBItem(name=search, price=0.0)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return f'<div class="item">{new_item.name} - ${new_item.price}</div>'

@app.get("/test/")
def test():
    return HTMLResponse(content="<div style='padding:20px; background:green; color:white; border-radius:8px;'><h3>✅ Working!</h3><p>HTMX is functional</p></div>")

@app.get("/settings/")
def settings(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="partials/settings.html"
    )

@app.get("/add-form/")
def add_form(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="partials/add_form.html"
    )

@app.get("/edit-form/")
def edit_form(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="partials/edit_form.html"
    )

@app.get("/delete-form/")
def delete_form(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="partials/delete_form.html"
    )

@app.get("/list-items/")
def list_items(request: Request, db: Session = Depends(get_db)):
    items = db.query(DBItem).all()
    return templates.TemplateResponse(
        request=request,
        name="partials/item_list.html",
        context={"items": items}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)