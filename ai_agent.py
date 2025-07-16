from db import leads_collection

def mock_llm_interact(email: str, query: str):
    lead = leads_collection.find_one({"email": email})
    if not lead:
        return {"response": "Lead not found."}
    
    if "follow" in query.lower():
        return {"response": f"Suggest follow-up → Email {lead['name']} at {lead['email']}."}
    elif "detail" in query.lower():
        return {"response": f"Name: {lead['name']}, Email: {lead['email']}, Status: {lead['status']}."}
    else:
        return {"response": "Ask about follow-up or details."}
