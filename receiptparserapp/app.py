# app.py (Final Polished and Corrected Version)
import streamlit as st
import pandas as pd
from PIL import Image
from datetime import datetime
import plotly.express as px

import database as db
import ocr_utils
import data_extraction
from models import Receipt
import algorithms

st.set_page_config(page_title="Receipt Parser Pro", page_icon="🧾", layout="wide")

def process_and_save_file(uploaded_file):
    """Processes any supported file type, dispatches to the correct parser, and saves."""
    try:
        # Step 1: Process file to get either an Image or a string
        content = ocr_utils.process_file(uploaded_file)
        
        if isinstance(content, Image.Image):
            # Step 2a: If it's an image, use the vision parser
            parsed_data = data_extraction.parse_receipt_with_vision(content)
        elif isinstance(content, str):
            # Step 2b: If it's text, use the text parser
            parsed_data = data_extraction.parse_receipt_with_text(content)
        else:
            st.warning(f"Could not process file '{uploaded_file.name}'. It might be empty or corrupted.")
            return False

        # Step 3: Save the result for manual correction
        receipt_obj = Receipt(**parsed_data)
        db.insert_receipt(receipt_obj)
        return True
    except Exception as e:
        st.error(f"Failed to process '{uploaded_file.name}': {e}")
        return False

def main():
    st.title("🧾 Receipt Parser & Manager")
    st.write("Configure your AI, then upload any receipt file (.jpg, .png, .pdf, .txt).")
    db.init_db()

    with st.sidebar:
        st.header("⚙️ AI Configuration")
        api_key = st.text_input("Enter your Gemini API Key", type="password")
        model_name = st.selectbox("Select Vision Model", ("gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.5-flash"))
        
        if api_key:
            try:
                data_extraction.configure_model(api_key, model_name)
                st.success("AI model configured.")
                st.session_state['ai_ready'] = True
            except Exception as e:
                st.error(f"AI Config Failed: {e}")
                st.session_state['ai_ready'] = False
        else:
            st.session_state['ai_ready'] = False

        st.header("Upload & Process")
        ai_is_ready = st.session_state.get('ai_ready', False)
        if not ai_is_ready: st.warning("Enter API key to enable uploads.")
        
        # FIX: Add .pdf and .txt back to the list of accepted types
        uploaded_files = st.file_uploader(
            "Choose receipt files", 
            type=["jpg", "png", "jpeg", "pdf", "txt"], 
            accept_multiple_files=True, 
            disabled=not ai_is_ready
        )

        if st.button("Process Uploaded Files", disabled=not ai_is_ready):
            if uploaded_files:
                success_count, fail_count = 0, 0
                with st.spinner("Analyzing files with AI..."):
                    for file in uploaded_files:
                        if process_and_save_file(file): success_count += 1
                        else: fail_count += 1
                st.success(f"Processing complete! Success: {success_count}, Failed: {fail_count}.")
                if success_count > 0: st.rerun()
                    
        st.markdown("---")
        st.header("Database Actions")
        if st.button("Clear All Receipts⚠️", key="clear_all_button"):
            if 'confirm_delete_all' not in st.session_state: st.session_state.confirm_delete_all = True
            else: del st.session_state.confirm_delete_all
        
        if 'confirm_delete_all' in st.session_state:
            st.warning("This will delete all receipts permanently. Are you sure?")
            if st.button("Yes, Delete Everything", key="confirm_delete_all_button"):
                db.delete_all_receipts()
                del st.session_state.confirm_delete_all
                st.success("All receipts have been deleted.")
                st.rerun()

    # --- Data Grid for Editing and Deleting ---
    st.header("Manage Your Receipts")
    receipts_data = db.get_all_receipts()

    if not receipts_data:
        st.info("The database is empty. Upload some receipts to get started.")
        return

    df = pd.DataFrame(receipts_data)
    df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce').dt.date
    df.dropna(subset=['id'], inplace=True)

    if 'original_df' not in st.session_state:
        st.session_state.original_df = df.copy()

    df.insert(0, "delete", False)
    
    edited_df = st.data_editor(
        df, hide_index=True, key="data_editor",
        column_config={
            "delete": st.column_config.CheckboxColumn("Delete"),
            "id": st.column_config.NumberColumn("ID", disabled=True),
            "vendor": st.column_config.TextColumn("Vendor", required=True),
            "transaction_date": st.column_config.DateColumn("Date", required=True),
            "amount": st.column_config.NumberColumn("Amount", format="%.2f", required=True),
            "currency": st.column_config.TextColumn("Currency"),
            # FIX: Added the missing category configuration
            "category": st.column_config.TextColumn("Category")
        }
    )

    # --- Action Buttons (Save, Delete, Export) ---
    st.markdown("---")
    col1, col2, col3 = st.columns([1.5, 2, 1.5])

    with col1:
        # FIX: Using a more robust method to check for changes
        if not edited_df.drop(columns=['delete']).equals(st.session_state.original_df):
            if st.button("Save Changes", key="save_changes_button"):
                for idx in edited_df.index:
                    original_row = st.session_state.original_df.loc[idx]
                    edited_row = edited_df.loc[idx]
                    if not original_row.equals(edited_row.drop('delete')):
                        receipt_id = int(edited_row['id'])
                        updates = edited_row.drop(['id', 'delete']).to_dict()
                        db.update_receipt(receipt_id, updates)
                st.success("Changes saved!")
                st.session_state.original_df = edited_df.drop(columns=['delete']).copy()
                st.rerun()

    with col2:
        selected_to_delete = edited_df[edited_df.delete]
        if not selected_to_delete.empty:
            if st.button(f"Delete {len(selected_to_delete)} Selected Receipts🗑️", key="delete_selected_button"):
                db.delete_receipts_by_ids(selected_to_delete["id"].tolist())
                st.session_state.original_df = edited_df[~edited_df.delete].drop(columns=['delete']).copy()
                st.rerun()

    with col3:
        export_df = edited_df.drop(columns=['delete'])
        csv = export_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export View to CSV", data=csv,
            file_name='receipts_summary.csv', mime='text/csv', key='download_csv_button'
        )

    st.markdown("---")

    # --- Analytics Dashboard ---
    st.header("Analytics Dashboard")
    analytics_df = edited_df.drop(columns=['delete']).copy()
    analytics_df['amount'] = pd.to_numeric(analytics_df['amount'], errors='coerce').fillna(0)
    
    # ... (Analytics logic is now robust and correct)
    spend_by_currency = analytics_df.groupby('currency')['amount'].sum()
    st.subheader("Total Spend by Currency")
    if not spend_by_currency.empty:
        cols = st.columns(len(spend_by_currency))
        for i, (currency, total) in enumerate(spend_by_currency.items()):
            cols[i].metric(label=f"Total Spend ({currency})", value=f"{total:,.2f}")
    else:
        st.metric("Total Spend", "$0.00")

    records = analytics_df.to_dict('records')
    st.caption("Charts below aggregate all amounts regardless of currency.")
    
    aggregates = algorithms.calculate_aggregates(records)
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Spend (Aggregated)", f"${aggregates['total_spend']:.2f}")
    c2.metric("Average Spend", f"${aggregates['mean']:.2f}")
    c3.metric("Receipt Count", len(records))

    chart1, chart2 = st.columns(2)
    with chart1:
        st.subheader("Spend by Vendor")
        vendor_spend = algorithms.get_vendor_frequency(records)
        if vendor_spend:
            pie_df = pd.DataFrame(list(vendor_spend.items()), columns=['Vendor', 'Amount'])
            fig = px.pie(pie_df, names='Vendor', values='Amount', hole=.3, title="Spending Distribution")
            st.plotly_chart(fig, use_container_width=True)

    with chart2:
        st.subheader("Monthly Spend Trend")
        monthly_spend = algorithms.get_monthly_spend(records)
        if monthly_spend:
            line_df = pd.DataFrame(list(monthly_spend.items()), columns=['Month', 'Amount'])
            if len(line_df) >= 3:
                line_df['3-Month Moving Avg'] = line_df['Amount'].rolling(window=3).mean()
            st.line_chart(line_df.set_index('Month'))

if __name__ == "__main__":
    main()