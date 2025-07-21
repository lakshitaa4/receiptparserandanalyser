
# Receipt Parser & Analyst

A full-stack AI-powered web application that lets users upload receipt images, extract structured information using vision models or OCR, and visualize expense trends using custom analytics — all with clean backend logic and manual algorithm implementations.

---

## Features

- **AI-Powered Parsing:** Gemini Vision API (google-generativeai) or fallback OCR (Tesseract)
- **File Upload & Ingestion:** Supports `.jpg`, `.jpeg`, `.png`, `.pdf`, `.txt`
- **Manual Search & Filtering:** Vendor, date range, amount range
- **Custom Algorithms:** Aggregations, vendor trends, and time-series
- **Editable UI:** Edit and correct receipt data in-app
- **Database Management:** Edit, delete, clear all receipts
- **Export:** Download filtered data as CSV or JSON
- **Analytics Dashboard:** Spend distributions, vendor breakdown, monthly trends

---

## Tech Stack

| Layer         | Technology                                 |
|-------------- |--------------------------------------------|
| UI / Frontend | Streamlit, Plotly Charts                   |
| AI Parsing    | Gemini Vision API (google-generativeai)    |
| OCR Fallback  | pytesseract, pdf2image, Pillow             |
| Data Models   | Pydantic                                   |
| Database      | SQLite3 (sqlite3 stdlib)                   |
| Charts        | Plotly, Streamlit native                   |
| Backend Logic | Native Python: search/aggregate|

---

## Folder Structure
```
receiptparserapp/
├── app.py                # Main Streamlit UI
├── database.py           # DB CRUD logic
├── data_extraction.py    # Gemini Vision & OCR parsing logic
├── ocr_utils.py          # OCR fallback with Tesseract
├── algorithms.py         # Manual search, and aggregation logic
├── models.py             # Pydantic Receipt schema
├── requirements.txt      # Dependencies
└── README.md             # This file
```

---

## Setup Instructions

### 1. Clone the Repository
```sh
git clone https://github.com/lakshitaa4/receiptparserandanalyser.git
cd receiptparserapp
```

### 2. Install Tesseract & Poppler
- **Tesseract:**
  - Download and install from: https://github.com/tesseract-ocr/tesseract/wiki
  - Add the install folder (e.g., `C:\Program Files\Tesseract-OCR`) to your Windows PATH.
- **Poppler:**
  - Download Windows binaries from: https://github.com/oschwartz10612/poppler-windows/releases/
  - Unzip and add the `bin` folder to your PATH.

### 3. Create and Activate a Python Virtual Environment
```sh
python -m venv venv
# On Windows:
.\venv\Scripts\activate
```

### 4. Install Requirements
```sh
pip install -r requirements.txt
```

---

## Usage

### Start the App
```sh
streamlit run app.py
```

### Using the App
- Upload receipt files in the sidebar
- Click "Process Uploaded Files" to extract and store data
- Use filters and analytics on the main dashboard
- Export filtered data as CSV or JSON
- Use the sidebar button to clear all receipts if needed

---

## Algorithms (Built From Scratch

- **Search & Filtering:** Keyword search on vendor, date and amount range filters
- **Aggregation:** Sum, Mean, Median, Mode
- **Monthly Spend:** With 3-month moving average
- **Vendor Spend Frequency:**

All implemented using native Python (no pandas for core logic).

---

## Data Schema
```python
class Receipt(BaseModel):
    vendor: Optional[str]
    transaction_date: Optional[date]
    amount: Optional[float]
    category: Optional[str]
    raw_text: str
    currency: Optional[str]
```

---

## Bonus Features

-  Export receipts to CSV/JSON
-  Manual editing of receipt data
-  Visual delete toggles + bulk deletion
-  Currency-aware display
-  Rolling monthly averages in charts

---

## Future Work

-  Real-time Currency Conversion (ExchangeRate-API, OpenExchangeRates, Fixer.io)
-  Multi-language OCR (langdetect, pytesseract multilingual)
-  Hybrid Parsing Mode (AI + Regex fallback)
-  Authentication & Multi-user Storage
-  Testing & Validation (with real receipts)
---

## Author
Lakshita Soni  
[LinkedIn](https://www.linkedin.com/in/lakshita-soni-b3268b2a5/) · [GitHub](https://github.com/lakshitaa4/)

---

## License
MIT License

---

## Credits
- [Streamlit](https://streamlit.io/)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- [Poppler](https://poppler.freedesktop.org/)
- [Google Gemini](https://ai.google.dev/)
- [Pandas](https://pandas.pydata.org/)
- [Pydantic](https://docs.pydantic.dev/)
- [Plotly](https://plotly.com/python/)
