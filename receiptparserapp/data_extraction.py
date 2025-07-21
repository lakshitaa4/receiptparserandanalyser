# data_extraction.py (Dual AI Capability: Vision and Text)

import google.generativeai as genai
from PIL import Image
import json
from typing import Dict, Any, Optional
from datetime import datetime

model = None
VENDOR_CATEGORIES = {"walmart": "Groceries", "target": "General Merchandise", "starbucks": "Food & Drink"}

# --- Prompt for Vision Model (Image Input) ---
VISION_PROMPT = """
Analyze the following receipt image and extract: "vendor", "transaction_date" (YYYY-MM-DD), "amount" (final total), and "currency" (3-letter code like USD, or symbol). Return ONLY a valid JSON object. If a value is missing, it should be null.
"""

# --- Prompt for Text Model (Text Input) ---
TEXT_PROMPT = """
Analyze the following raw text from a receipt and extract: "vendor", "transaction_date" (YYYY-MM-DD), "amount" (final total), and "currency" (3-letter code like USD, or symbol). Return ONLY a valid JSON object. If a value is missing, it should be null.
Here is the text:
---
{raw_text}
---
"""

def configure_model(api_key: str, model_name: str):
    global model
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        model.generate_content("test", generation_config={"max_output_tokens": 10})
    except Exception as e:
        raise RuntimeError(f"Failed to configure Gemini model. Check API key/model. Error: {e}")

def _process_parsed_json(parsed_json: dict, raw_text_placeholder: str) -> dict:
    """A helper function to process the JSON returned by the AI, avoiding code duplication."""
    date_val = parsed_json.get("transaction_date")
    amount_val = parsed_json.get("amount")
    vendor = parsed_json.get("vendor")
    currency = parsed_json.get("currency", "USD")

    return {
        "vendor": vendor,
        "transaction_date": datetime.strptime(date_val, "%Y-%m-%d").date() if date_val else None,
        "amount": float(amount_val) if amount_val is not None else None,
        "raw_text": raw_text_placeholder,
        "category": map_category(vendor),
        "currency": currency
    }

def map_category(vendor: Optional[str]) -> Optional[str]:
    if not vendor: return "Other"
    for known_vendor, category in VENDOR_CATEGORIES.items():
        if known_vendor in vendor.lower(): return category
    return "Other"

def parse_receipt_with_vision(image: Image.Image) -> Dict[str, Any]:
    """Parses an image using the Gemini Vision model."""
    if not model: raise RuntimeError("AI model not configured.")
    try:
        response = model.generate_content([VISION_PROMPT, image])
        json_str = response.text.strip().lstrip("```json").rstrip("```").strip()
        parsed_json = json.loads(json_str)
        return _process_parsed_json(parsed_json, f"Parsed from image of {parsed_json.get('vendor') or 'unknown'}")
    except Exception as e:
        print(f"Vision AI parsing failed: {e}")
        return {"raw_text": "AI vision parsing failed."}

def parse_receipt_with_text(text: str) -> Dict[str, Any]:
    """Parses a raw text string using the Gemini model."""
    if not model: raise RuntimeError("AI model not configured.")
    try:
        prompt = TEXT_PROMPT.format(raw_text=text)
        response = model.generate_content(prompt)
        json_str = response.text.strip().lstrip("```json").rstrip("```").strip()
        parsed_json = json.loads(json_str)
        return _process_parsed_json(parsed_json, text)
    except Exception as e:
        print(f"Text AI parsing failed: {e}")
        return {"raw_text": "AI text parsing failed."}