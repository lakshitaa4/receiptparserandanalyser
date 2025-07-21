# data_extraction.py (Gemini Vision Version)

import google.generativeai as genai
from PIL import Image
import json
from typing import Dict, Any, Optional
from datetime import datetime

model = None
VENDOR_CATEGORIES = {"walmart": "Groceries", "target": "General Merchandise", "starbucks": "Food & Drink"}

# --- NEW VISION-ENABLED PROMPT ---
VISION_PROMPT = """
You are an expert financial assistant. Analyze the following receipt image and extract the key information.
If there is no currency symbol, figure out from the context where the store is located and then convert the amount to USD using the latest exchange rates. It is important to ensure the amount is accurate. Must check the currency symbol first.
Return the data ONLY as a valid JSON object with the keys "vendor", "transaction_date", and "amount".
- vendor: The name of the store.
- transaction_date: The main date of the purchase in YYYY-MM-DD format.
- amount: The final total amount paid.
- currency: The 3-letter currency symbol like $, €, ₹, etc. 
If a value cannot be found, it should be null.
"""

def configure_model(api_key: str, model_name: str):
    global model
    try:
        genai.configure(api_key=api_key)
        # We must use a model that supports vision, like gemini-1.5-flash
        model = genai.GenerativeModel(model_name)
    except Exception as e:
        raise RuntimeError(f"Failed to configure Gemini model: {e}")

def map_category(vendor: Optional[str]) -> Optional[str]:
    if not vendor: return "Other"
    for known_vendor, category in VENDOR_CATEGORIES.items():
        if known_vendor in vendor.lower(): return category
    return "Other"

def parse_receipt_with_vision(image: Image.Image) -> Dict[str, Any]:
    """
    Parses an image of a receipt directly using the Gemini Vision model.
    """
    if not model:
        raise RuntimeError("AI model is not configured.")

    try:
        # The model can take a list of inputs: a prompt and an image
        response = model.generate_content([VISION_PROMPT, image])
        print(response.text)  # Debugging output
        
        # Clean and parse the JSON response
        json_str = response.text.strip().lstrip("```json").rstrip("```").strip()
        parsed_json = json.loads(json_str)

        # --- Post-processing ---
        date_val = parsed_json.get("transaction_date")
        amount_val = parsed_json.get("amount")
        vendor = parsed_json.get("vendor")
        currency = parsed_json.get("currency", "USD")

        final_data = {
            "vendor": vendor,
            "transaction_date": datetime.strptime(date_val, "%Y-%m-%d").date() if date_val else None,
            "amount": float(amount_val) if amount_val is not None else None,
            "raw_text": f"Parsed from image of {vendor or 'unknown vendor'}", # No raw text, so we create a placeholder
            "category": map_category(vendor),
            "currency": currency
        }
        return final_data
    except Exception as e:
        print(f"Vision AI parsing failed: {e}")
        # Return empty dict for manual entry
        return {
            "vendor": None, "transaction_date": None, "amount": None,
            "raw_text": "AI vision parsing failed.", "category": "Other"
        }