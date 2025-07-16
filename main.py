from fastapi import FastAPI, UploadFile, Form, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from lead_store import create_lead, delete_lead, update_lead
from utils.extractor import extract_from_file
from ai_agent import mock_llm_interact
from email_router import router as email_router
from db import leads_collection
import pandas as pd
import io
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from fastapi import Body

app = FastAPI()

# Register the email router
app.include_router(email_router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class InteractionRequest(BaseModel):
    email: str
    query: str

class UpdateLeadRequest(BaseModel):
    email: str
    status: str

class DeleteLeadRequest(BaseModel):
    email: str

class Lead(BaseModel):
    name: str
    email: str
    phone: int
    status: str
    source: str

@app.post("/upload-document")
async def upload_doc(file: UploadFile = File(...)):
    name, email = await extract_from_file(file)
    lead = create_lead(name, email, "N/A", "New", "Document")
    return lead

@app.post("/create-lead")
async def create_manual_lead(
    name: str = Form(...), email: str = Form(...), phone: int = Form(...)
):
    # Strip any extra whitespace like \t or \n
    lead = create_lead(name.strip(), email.strip(), phone, "New", "Manual")
    return lead


@app.get("/leads")
def get_leads():
    leads = list(leads_collection.find({}, {"_id": 0}))
    return leads

@app.post("/update-lead")
def update_lead(data: dict):
    email = data.get("email")
    status = data.get("status")
    result = leads_collection.update_one({"email": email}, {"$set": {"status": status}})
    return {"modified": result.modified_count}

@app.post("/delete-lead")
def delete_lead(data: dict = Body(...)):
    email = data.get("email")
    if not email:
        return {"error": "Email required"}
    result = leads_collection.delete_one({"email": email})
    return {"deleted": result.deleted_count}

@app.post("/interact")
def interact(data: InteractionRequest):
    lead = leads_collection.find_one({"email": data.email})
    if not lead:
        return {"response": "Lead not found"}

    q = data.query.lower()
    if "follow" in q:
        return {"response": f"Suggest follow-up → Email {lead['name']} at {lead['email']}."}
    elif "detail" in q:
        return {"response": f"Name: {lead['name']}, Email: {lead['email']}, Status: {lead['status']}."}
    else:
        return {"response": "Ask about follow-up or details."}

@app.get("/export-csv")
def export_csv():
    leads = list(leads_collection.find({}, {"_id": 0}))
    df = pd.DataFrame(leads)
    stream = io.StringIO()
    df.to_csv(stream, index=False)
    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=leads.csv"
    return response

@app.get("/export-excel")
def export_excel():
    leads = list(leads_collection.find({}, {"_id": 0}))
    df = pd.DataFrame(leads)
    stream = io.BytesIO()
    with pd.ExcelWriter(stream, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Leads')
    stream.seek(0)
    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=leads.xlsx"}
    )

@app.post("/add-lead")
def add_lead(lead: Lead):
    if leads_collection.find_one({"email": lead.email}):
        return {"error": "Lead already exists"}
    leads_collection.insert_one(lead.dict())
    return {"message": "Lead added"}
