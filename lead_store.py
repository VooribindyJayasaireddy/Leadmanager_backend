from typing import List, Dict
from bson.objectid import ObjectId
from db import leads_collection

def create_lead(name: str, email: str, phone: str, status: str, source: str):
    lead = {
        "name": name,
        "email": email,
        "phone": phone,
        "status": status,
        "source": source
    }
    result = leads_collection.insert_one(lead)
    lead["_id"] = str(result.inserted_id)
    return lead

def update_lead(email: str, status: str):
    result = leads_collection.find_one_and_update(
        {"email": email},
        {"$set": {"status": status}},
        return_document=True
    )
    if result:
        result["_id"] = str(result["_id"])
        return {"message": "Lead updated", "lead": result}
    else:
        return {"error": "Lead not found"}

def delete_lead(email: str):
    result = leads_collection.delete_one({"email": email})
    if result.deleted_count:
        return {"message": "Lead deleted"}
    else:
        return {"error": "Lead not found"}
