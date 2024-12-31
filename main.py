from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import hashlib
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# התחברות ל-MongoDB
MONGO_URI = os.getenv('mongodb+srv://url:<db_url>@cluster0.unhrr.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
client = AsyncIOMotorClient(MONGO_URI)
db = client.url_shortener
urls_collection = db.urls

class URL(BaseModel):
    long_url: str

@app.post("/shorten")
async def shorten_url(url: URL):
    short_id = hashlib.md5(url.long_url.encode()).hexdigest()[:6]
    
    # שמירה במסד הנתונים
    await urls_collection.update_one(
        {"_id": short_id},
        {"$set": {"long_url": url.long_url}},
        upsert=True
    )
    
    return {"short_url": f"https://your-domain.vercel.app/{short_id}"}

@app.get("/{short_id}")
async def redirect_to_url(short_id: str):
    url_data = await urls_collection.find_one({"_id": short_id})
    if not url_data:
        raise HTTPException(status_code=404, detail="URL not found")
    return RedirectResponse(url_data["long_url"])
