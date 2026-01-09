from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from database import init_db, get_db, Job
from datetime import datetime
import crawler
import uvicorn
from typing import List
from pydantic import BaseModel

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
def on_startup():
    init_db()

class JobSchema(BaseModel):
    title: str
    company: str
    link: str
    location: str
    date_posted: str
    crawled_at: datetime

    class Config:
        orm_mode = True

@app.get("/")
def read_root():
    from fastapi.responses import FileResponse
    return FileResponse('static/index.html')

@app.get("/api/jobs", response_model=List[JobSchema])
def get_jobs(db: Session = Depends(get_db)):
    return db.query(Job).order_by(Job.crawled_at.desc()).all()

@app.post("/api/crawl")
def trigger_crawl(background_tasks: BackgroundTasks):
    background_tasks.add_task(crawler.run_crawlers)
    return {"message": "Crawl started in background"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
