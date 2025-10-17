"""
JewelCalc - Jewelry Billing & Customer Management System
A clean, streamlined Streamlit application for jewelry shops
"""
import streamlit as st
import pandas as pd
from database import Database
from utils import format_currency, generate_invoice_number, generate_account_number, validate_phone, calculate_item_totals
from pdf_generator import create_invoice_pdf, get_pdf_download_link, create_thermal_invoice_pdf
import os
import hashlib
import platform


# Page configuration
st.set_page_config(
    page_title="JewelCalc",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    /* Hide Streamlit branding and header */
    [data-testid="stToolbar"] {visibility: hidden;}
    [data-testid="stDecoration"] {visibility: hidden;}
    [data-testid="stStatusWidget"] {visibility: hidden;}
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Remove top padding to prevent blocking navigation buttons */
    .block-container {
        padding-top: 1rem;
    }
    
    /* Custom header */
    .main-header {
        background: linear-gradient(90deg, #e0f7fa 0%, #f5f7fa 100%);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        text-align: center;
    }
    .main-header h1 {
        color: #1565c0;
        margin: 0;
        font-size: 2.5rem;
    }
    
    /* Cards */
    .card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    
    /* Success/Error styling */
    .stSuccess {
        background-color: #d4edda;
        border-color: #c3e6cb;
        color: #155724;
    }
    </style>
""", unsafe_allow_html=True)


def get_device_id():
    """Generate a unique device identifier based on system information"""
    try:
        # Get system information to create a unique device ID
        system_info = f"{platform.node()}-{platform.system()}-{platform.machine()}"
        # Create a hash of the system info (MD5 is sufficient for non-cryptographic device ID)
        device_hash = hashlib.md5(system_info.encode()).hexdigest()[:8]
        return device_hash
    except Exception:
        # Fallback to a simple identifier if system info is unavailable
        return "default"


def get_device_specific_db_path():
    """Get device-specific database path to ensure local storage per device"""
    device_id = get_device_id()
    return f"jewelcalc_{device_id}.db"


# Initialize session state
def init_session_state():
    """Initialize session state variables"""
    if 'db_path' not in st.session_state:
        # Use device-specific database path for local storage
        st.session_state.db_path = get_device_specific_db_path()
    
    if 'metal_settings' not in st.session_state:
        st.session_state.metal_settings = {
            'Gold 24K': {'rate': 6500.0, 'wastage': 5.0, 'making': 10.0},
            'Gold 22K': {'rate': 6000.0, 'wastage': 6.0, 'making': 12.0},
            'Gold 18K': {'rate': 5500.0, 'wastage': 7.0, 'making': 14.0},
            'Silver': {'rate': 75.0, 'wastage': 3.0, 'making': 8.0}
        }
    
    if 'cgst' not in st.session_state:
        st.session_state.cgst = 1.5
    
    if 'sgst' not in st.session_state:
        st.session_state.sgst = 1.5
    
    if 'current_invoice_items' not in st.session_state:
        st.session_state.current_invoice_items = []
    
    if 'selected_customer_id' not in st.session_state:
        st.session_state.selected_customer_id = None
    
    if 'discount' not in st.session_state:
        st.session_state.discount = 0.0


init_session_state()

# Initialize database
db = Database(st.session_state.db_path)

# Header
st.markdown('<div class="main-header"><h1>💎 JewelCalc</h1></div>', unsafe_allow_html=True)

# Sidebar - Database Management
with st.sidebar:
    st.markdown("### 🗄️ Database Management")
    
    # Show current database with device identifier
    device_id = get_device_id()
    st.info(f"📱 Device ID: `{device_id}`")
    st.info(f"💾 Current DB: `{st.session_state.db_path}`")
    
    with st.expander("⚙️ Database Operations", expanded=False):
        # Change database
        st.markdown("**Switch Database**")
        st.info("💡 By default, each device uses its own database. You can switch to a shared database if needed.")
        new_db = st.text_input("Database filename", value=st.session_state.db_path, 
                               help="Enter a .db filename. Use device-specific name for local storage or a common name to share data.")
        if st.button("Switch Database"):
            # Validate database filename to prevent path traversal
            if new_db.endswith('.db') and os.path.basename(new_db) == new_db and '/' not in new_db and '\\' not in new_db:
                st.session_state.db_path = new_db
                st.rerun()
            else:
                st.error("Database filename must end with .db and contain no path separators")
        
        st.markdown("---")
        
        # Export/Import Database
        st.markdown("**Backup & Restore**")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Backup DB"):
                import shutil
                from datetime import datetime
                backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                db.export_database(backup_name)
                st.success(f"Backup saved: {backup_name}")
        
        with col2:
            restore_file = st.file_uploader("📂 Restore DB", type=['db'], key="db_restore")
            if restore_file is not None:
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp_file:
                    tmp_file.write(restore_file.read())
                    tmp_path = tmp_file.name
                
                if st.button("Confirm Restore"):
                    try:
                        db.import_database(tmp_path)
                        st.success("Database restored successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

# Main tabs
tab1, tab2, tab3, tab4 = st.tabs(["⚙️ Settings", "👥 Customers", "📝 Create Invoice", "📋 View Invoices"])

# ============================================================================
# TAB 1: SETTINGS
# ============================================================================
with tab1:
    st.markdown("### ⚙️ Base Settings")
    
    st.markdown("#### Metal Settings")
    
    # Edit metal settings
    metals_data = []
    for metal, settings in st.session_state.metal_settings.items():
        metals_data.append({
            'Metal': metal,
            'Rate (per gram)': settings['rate'],
            'Wastage %': settings['wastage'],
            'Making %': settings['making']
        })
    
    df_metals = pd.DataFrame(metals_data)
    edited_metals = st.data_editor(
        df_metals,
        num_rows="dynamic",
        use_container_width=True,
        key="metals_editor"
    )
    
    st.markdown("#### Tax Settings")
    col1, col2 = st.columns(2)
    with col1:
        cgst = st.number_input("CGST %", value=st.session_state.cgst, min_value=0.0, format="%.2f")
    with col2:
        sgst = st.number_input("SGST %", value=st.session_state.sgst, min_value=0.0, format="%.2f")
    
    if st.button("💾 Save Settings", use_container_width=True):
        # Update metal settings
        new_settings = {}
        for _, row in edited_metals.iterrows():
            if row['Metal']:
                new_settings[row['Metal']] = {
                    'rate': float(row['Rate (per gram)']),
                    'wastage': float(row['Wastage %']),
                    'making': float(row['Making %'])
                }
        st.session_state.metal_settings = new_settings
        st.session_state.cgst = cgst
        st.session_state.sgst = sgst
        st.success("✅ Settings saved successfully!")
    
    # Reset All Data Section
    st.markdown("---")
    st.markdown("#### 🔄 Reset Database")
    st.warning("⚠️ **Danger Zone**: This will delete ALL data including customers, invoices, and settings!")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        if 'confirm_reset' not in st.session_state:
            st.session_state.confirm_reset = False
        
        if st.button("🗑️ Reset All Data", type="secondary"):
            st.session_state.confirm_reset = True
    
    with col2:
        if st.session_state.confirm_reset:
            st.error("⚠️ Are you absolutely sure? This action CANNOT be undone!")
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                if st.button("✅ YES, DELETE EVERYTHING", type="primary"):
                    try:
                        # Delete the database file (validate it's in current directory)
                        db_path = st.session_state.db_path
                        if os.path.basename(db_path) == db_path and os.path.exists(db_path):
                            os.remove(db_path)
                        
                        # Reset session state to defaults
                        st.session_state.metal_settings = {
                            'Gold 24K': {'rate': 6500.0, 'wastage': 5.0, 'making': 10.0},
                            'Gold 22K': {'rate': 6000.0, 'wastage': 6.0, 'making': 12.0},
                            'Gold 18K': {'rate': 5500.0, 'wastage': 7.0, 'making': 14.0},
                            'Silver': {'rate': 75.0, 'wastage': 3.0, 'making': 8.0}
                        }
                        st.session_state.cgst = 1.5
                        st.session_state.sgst = 1.5
                        st.session_state.current_invoice_items = []
                        st.session_state.selected_customer_id = None
                        st.session_state.discount = 0.0
                        st.session_state.confirm_reset = False
                        
                        st.success("✅ All data has been reset! The page will reload...")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error resetting data: {str(e)}")
            
            with col_b:
                if st.button("❌ Cancel"):
                    st.session_state.confirm_reset = False
                    st.rerun()


# ============================================================================
# TAB 2: CUSTOMERS
# ============================================================================
with tab2:
    st.markdown("### 👥 Customer Management")
    
    # Action selector
    action = st.radio("Action", ["Add Customer", "Edit Customer", "Delete Customer"], horizontal=True)
    
    customers_df = db.get_customers()
    
    if action == "Add Customer":
        st.markdown("#### Add New Customer")
        
        col1, col2 = st.columns(2)
        with col1:
            existing_accounts = customers_df['account_no'].tolist() if not customers_df.empty else []
            new_account = generate_account_number(existing_accounts)
            account_no = st.text_input("Account Number", value=new_account)
            name = st.text_input("Customer Name *")
        
        with col2:
            phone = st.text_input("Phone Number * (10 digits)")
            address = st.text_area("Address")
        
        if st.button("➕ Add Customer", use_container_width=True):
            if not name or not phone:
                st.error("Name and phone are required")
            elif not validate_phone(phone):
                st.error("Phone must be exactly 10 digits")
            else:
                try:
                    db.add_customer(account_no, name, phone, address)
                    st.success(f"✅ Customer added successfully! Account: {account_no}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    elif action == "Edit Customer":
        if customers_df.empty:
            st.info("No customers found. Add a customer first.")
        else:
            st.markdown("#### Edit Customer")
            
            customer_options = {f"{row['name']} ({row['phone']})": row['id'] 
                              for _, row in customers_df.iterrows()}
            
            selected = st.selectbox("Select Customer", options=list(customer_options.keys()))
            
            if selected:
                customer_id = customer_options[selected]
                customer = db.get_customer_by_id(customer_id)
                
                col1, col2 = st.columns(2)
                with col1:
                    account_no = st.text_input("Account Number", value=customer['account_no'])
                    name = st.text_input("Customer Name", value=customer['name'])
                
                with col2:
                    phone = st.text_input("Phone Number", value=customer['phone'])
                    address = st.text_area("Address", value=customer.get('address', ''))
                
                if st.button("💾 Update Customer", use_container_width=True):
                    if not name or not phone:
                        st.error("Name and phone are required")
                    elif not validate_phone(phone):
                        st.error("Phone must be exactly 10 digits")
                    else:
                        try:
                            db.update_customer(customer_id, account_no, name, phone, address)
                            st.success("✅ Customer updated successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
    
    else:  # Delete Customer
        if customers_df.empty:
            st.info("No customers found.")
        else:
            st.markdown("#### Delete Customer")
            st.warning("⚠️ This will delete the customer and all their invoices!")
            
            customer_options = {f"{row['name']} ({row['phone']})": row['id'] 
                              for _, row in customers_df.iterrows()}
            
            selected = st.selectbox("Select Customer to Delete", options=list(customer_options.keys()))
            
            if selected:
                customer_id = customer_options[selected]
                confirm = st.checkbox("I confirm I want to delete this customer")
                
                if confirm and st.button("🗑️ Delete Customer", use_container_width=True):
                    db.delete_customer(customer_id)
                    st.success("✅ Customer deleted successfully!")
                    st.rerun()
    
    # Import/Export Customers
    st.markdown("---")
    st.markdown("#### Import/Export Customers")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Export Customers (CSV)"):
            csv_data = db.export_customers_csv()
            st.download_button(
                label="💾 Download CSV",
                data=csv_data,
                file_name="customers_export.csv",
                mime="text/csv"
            )
    
    with col2:
        uploaded_customers = st.file_uploader("📤 Import Customers (CSV)", type=['csv'], key="import_customers")
        if uploaded_customers is not None:
            csv_content = uploaded_customers.read().decode('utf-8')
            if st.button("Confirm Import Customers"):
                imported, errors = db.import_customers_csv(csv_content)
                if imported > 0:
                    st.success(f"✅ Imported {imported} customers")
                if errors:
                    st.warning(f"⚠️ {len(errors)} errors occurred")
                    for error in errors[:5]:  # Show first 5 errors
                        st.error(error)
                st.rerun()
    
    # Show all customers
    st.markdown("#### All Customers")
    if not customers_df.empty:
        search = st.text_input("🔍 Search customers", "")
        if search:
            mask = (customers_df['name'].str.contains(search, case=False) | 
                   customers_df['phone'].str.contains(search, case=False))
            customers_df = customers_df[mask]
        
        st.dataframe(customers_df, use_container_width=True, hide_index=True)
    else:
        st.info("No customers yet. Add your first customer above!")


# ============================================================================
# TAB 3: CREATE INVOICE
# ============================================================================
with tab3:
    st.markdown("### 📝 Create Invoice")
    
    customers_df = db.get_customers()
    
    if customers_df.empty:
        st.warning("⚠️ No customers found. Please add a customer first in the Customers tab.")
    else:
        # Customer selection
        customer_options = {f"{row['name']} ({row['phone']})": row['id'] 
                          for _, row in customers_df.iterrows()}
        
        selected_customer = st.selectbox(
            "Select Customer *",
            options=[""] + list(customer_options.keys())
        )
        
        if selected_customer:
            st.session_state.selected_customer_id = customer_options[selected_customer]
            
            # New invoice button
            col1, col2, col3 = st.columns([1, 1, 6])
            with col1:
                if st.button("🆕 New Invoice"):
                    st.session_state.current_invoice_items = []
                    st.session_state.discount = 0.0
                    st.rerun()
            
            st.markdown("#### Add Items")
            
            # Item entry form
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                metal = st.selectbox("Metal *", options=list(st.session_state.metal_settings.keys()))
            
            with col2:
                weight = st.number_input("Weight (grams) *", min_value=0.0, format="%.3f")
            
            settings = st.session_state.metal_settings[metal]
            
            with col3:
                rate = st.number_input("Rate/gram", value=settings['rate'], format="%.2f")
            
            with col4:
                wastage = st.number_input("Wastage %", value=settings['wastage'], format="%.2f")
            
            col5, col6, col7 = st.columns([1, 1, 2])
            
            with col5:
                making = st.number_input("Making %", value=settings['making'], format="%.2f")
            
            # Calculate totals
            if weight > 0 and rate > 0:
                totals = calculate_item_totals(weight, rate, wastage, making)
                
                with col6:
                    st.metric("Item Value", format_currency(totals['item_value']))
                
                with col7:
                    st.metric("Line Total", format_currency(totals['line_total']))
                
                if st.button("➕ Add Item to Invoice", use_container_width=True):
                    item = {
                        'metal': metal,
                        'weight': weight,
                        'rate': rate,
                        'wastage_percent': wastage,
                        'making_percent': making,
                        'item_value': totals['item_value'],
                        'wastage_amount': totals['wastage_amount'],
                        'making_amount': totals['making_amount'],
                        'line_total': totals['line_total']
                    }
                    st.session_state.current_invoice_items.append(item)
                    st.success("✅ Item added!")
                    st.rerun()
            
            # Show current items
            if st.session_state.current_invoice_items:
                st.markdown("#### Current Invoice Items")
                
                items_display = []
                for i, item in enumerate(st.session_state.current_invoice_items):
                    items_display.append({
                        'No.': i + 1,
                        'Metal': item['metal'],
                        'Weight': f"{item['weight']:.3f}g",
                        'Rate': format_currency(item['rate']),
                        'Wastage': format_currency(item['wastage_amount']),
                        'Making': format_currency(item['making_amount']),
                        'Total': format_currency(item['line_total'])
                    })
                
                st.dataframe(pd.DataFrame(items_display), use_container_width=True, hide_index=True)
                
                # Remove item button
                if st.button("🗑️ Remove Last Item"):
                    st.session_state.current_invoice_items.pop()
                    st.rerun()
                
                # Invoice summary
                st.markdown("#### Invoice Summary")
                
                subtotal = sum(item['line_total'] for item in st.session_state.current_invoice_items)
                
                col1, col2 = st.columns(2)
                with col1:
                    discount_pct = st.number_input("Discount %", min_value=0.0, value=st.session_state.discount, format="%.2f")
                    st.session_state.discount = discount_pct
                
                discount_amt = subtotal * (discount_pct / 100)
                taxable_amount = subtotal - discount_amt
                cgst_amt = taxable_amount * (st.session_state.cgst / 100)
                sgst_amt = taxable_amount * (st.session_state.sgst / 100)
                total = taxable_amount + cgst_amt + sgst_amt
                
                # Display summary
                st.markdown("---")
                col1, col2 = st.columns(2)
                with col2:
                    st.markdown(f"**Subtotal:** {format_currency(subtotal)}")
                    if discount_pct > 0:
                        st.markdown(f"**Discount ({discount_pct}%):** -{format_currency(discount_amt)}")
                        st.markdown(f"**Taxable Amount:** {format_currency(taxable_amount)}")
                    st.markdown(f"**CGST ({st.session_state.cgst}%):** {format_currency(cgst_amt)}")
                    st.markdown(f"**SGST ({st.session_state.sgst}%):** {format_currency(sgst_amt)}")
                    st.markdown(f"### **Total:** {format_currency(total)}")
                
                # Save invoice
                if st.button("💾 Save Invoice", use_container_width=True):
                    try:
                        invoice_no = generate_invoice_number()
                        db.save_invoice(
                            st.session_state.selected_customer_id,
                            invoice_no,
                            st.session_state.current_invoice_items,
                            st.session_state.cgst,
                            st.session_state.sgst,
                            discount_pct
                        )
                        st.success(f"✅ Invoice saved! Invoice No: **{invoice_no}**")
                        st.session_state.current_invoice_items = []
                        st.session_state.discount = 0.0
                        st.balloons()
                    except Exception as e:
                        st.error(f"Error saving invoice: {str(e)}")


# ============================================================================
# TAB 4: VIEW INVOICES
# ============================================================================
with tab4:
    st.markdown("### 📋 View Invoices")
    
    invoices_df = db.get_invoices()
    
    if invoices_df.empty:
        st.info("No invoices yet. Create your first invoice in the Create Invoice tab!")
    else:
        # Import/Export Invoices
        st.markdown("#### Import/Export Invoices")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Export All Invoices (JSON)"):
                json_data = db.export_invoices_json()
                st.download_button(
                    label="💾 Download JSON",
                    data=json_data,
                    file_name="invoices_export.json",
                    mime="application/json"
                )
        
        with col2:
            uploaded_invoices = st.file_uploader("📤 Import Invoices (JSON)", type=['json'], key="import_invoices")
            if uploaded_invoices is not None:
                json_content = uploaded_invoices.read().decode('utf-8')
                if st.button("Confirm Import Invoices"):
                    imported, errors = db.import_invoices_json(json_content)
                    if imported > 0:
                        st.success(f"✅ Imported {imported} invoices")
                    if errors:
                        st.warning(f"⚠️ {len(errors)} errors occurred")
                        for error in errors[:5]:
                            st.error(error)
                    st.rerun()
        
        st.markdown("---")
        
        # Search
        search = st.text_input("🔍 Search invoices", "")
        if search:
            mask = (invoices_df['invoice_no'].str.contains(search, case=False) | 
                   invoices_df['customer_name'].str.contains(search, case=False, na=False) |
                   invoices_df['customer_phone'].str.contains(search, case=False, na=False))
            invoices_df = invoices_df[mask]
        
        # Display invoices
        for _, row in invoices_df.iterrows():
            with st.expander(
                f"📄 {row['invoice_no']} | {row['customer_name']} | {format_currency(row['total'])} | {row['date']}"
            ):
                invoice, items_df, customer = db.get_invoice_by_number(row['invoice_no'])
                
                # Customer info
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Customer:** {customer['name']}")
                    st.markdown(f"**Phone:** {customer['phone']}")
                with col2:
                    st.markdown(f"**Account:** {customer['account_no']}")
                    st.markdown(f"**Date:** {invoice['date']}")
                
                st.markdown("---")
                
                # Items table
                st.markdown("**Items:**")
                items_display = []
                for _, item in items_df.iterrows():
                    items_display.append({
                        'No.': int(item['item_no']),
                        'Metal': item['metal'],
                        'Weight': f"{item['weight']:.3f}g",
                        'Rate': format_currency(item['rate']),
                        'Item Value': format_currency(item['item_value']),
                        'Wastage': format_currency(item['wastage_amount']),
                        'Making': format_currency(item['making_amount']),
                        'Total': format_currency(item['line_total'])
                    })
                
                st.dataframe(pd.DataFrame(items_display), use_container_width=True, hide_index=True)
                
                # Summary
                st.markdown("---")
                col1, col2 = st.columns(2)
                with col2:
                    st.markdown(f"**Subtotal:** {format_currency(invoice['subtotal'])}")
                    if invoice['discount_percent'] > 0:
                        st.markdown(f"**Discount ({invoice['discount_percent']}%):** -{format_currency(invoice['discount_amount'])}")
                    st.markdown(f"**CGST ({invoice['cgst_percent']}%):** {format_currency(invoice['cgst_amount'])}")
                    st.markdown(f"**SGST ({invoice['sgst_percent']}%):** {format_currency(invoice['sgst_amount'])}")
                    st.markdown(f"### **Total:** {format_currency(invoice['total'])}")
                
                st.markdown("---")
                
                # Action buttons
                col1, col2, col3, col4 = st.columns(4)
                
                # PDF download (direct download)
                with col1:
                    pdf_buffer = create_invoice_pdf(invoice, items_df, customer)
                    st.download_button(
                        label="📄 Download PDF",
                        data=pdf_buffer,
                        file_name=f"{row['invoice_no']}.pdf",
                        mime="application/pdf",
                        key=f"dl_{row['invoice_no']}"
                    )
                
                # Print (opens in new tab for printing to any connected printer)
                with col2:
                    pdf_buffer_print = create_invoice_pdf(invoice, items_df, customer)
                    import base64
                    b64 = base64.b64encode(pdf_buffer_print.read()).decode()
                    href = f'<a href="data:application/pdf;base64,{b64}" target="_blank">🖨️ PRINT</a>'
                    st.markdown(href, unsafe_allow_html=True)
                
                # Thermal print
                with col3:
                    from pdf_generator import create_thermal_invoice_pdf
                    thermal_buffer = create_thermal_invoice_pdf(invoice, items_df, customer)
                    st.download_button(
                        label="🧾 Thermal Print",
                        data=thermal_buffer,
                        file_name=f"{row['invoice_no']}_thermal.pdf",
                        mime="application/pdf",
                        key=f"thermal_{row['invoice_no']}"
                    )
                
                # Edit invoice button
                with col4:
                    if st.button("✏️ Edit Invoice", key=f"edit_{row['invoice_no']}"):
                        st.session_state.editing_invoice_id = invoice['id']
                        st.session_state.editing_invoice_no = row['invoice_no']
                        st.rerun()
                
                # Edit invoice form
                if st.session_state.get('editing_invoice_id') == invoice['id']:
                    st.markdown("---")
                    st.markdown("### ✏️ Edit Invoice")
                    
                    # Load items into editable list - use session state to persist changes
                    if 'temp_edit_items' not in st.session_state or st.session_state.get('temp_edit_items_invoice_id') != invoice['id']:
                        edit_items = []
                        for _, item in items_df.iterrows():
                            edit_items.append({
                                'metal': item['metal'],
                                'weight': float(item['weight']),
                                'rate': float(item['rate']),
                                'wastage_percent': float(item['wastage_percent']),
                                'making_percent': float(item['making_percent']),
                                'item_value': float(item['item_value']),
                                'wastage_amount': float(item['wastage_amount']),
                                'making_amount': float(item['making_amount']),
                                'line_total': float(item['line_total'])
                            })
                        st.session_state.temp_edit_items = edit_items
                        st.session_state.temp_edit_items_invoice_id = invoice['id']
                    else:
                        edit_items = st.session_state.temp_edit_items
                    
                    # Display editable items
                    st.markdown("**Current Items:**")
                    items_edit_display = []
                    for i, item in enumerate(edit_items):
                        items_edit_display.append({
                            'No.': i + 1,
                            'Metal': item['metal'],
                            'Weight': f"{item['weight']:.3f}g",
                            'Rate': format_currency(item['rate']),
                            'Total': format_currency(item['line_total'])
                        })
                    st.dataframe(pd.DataFrame(items_edit_display), use_container_width=True, hide_index=True)
                    
                    # Add new item to edit
                    st.markdown("**Add/Modify Items:**")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        edit_metal = st.selectbox("Metal", options=list(st.session_state.metal_settings.keys()), key=f"edit_metal_{invoice['id']}")
                    
                    with col2:
                        edit_weight = st.number_input("Weight (g)", min_value=0.0, format="%.3f", key=f"edit_weight_{invoice['id']}")
                    
                    edit_settings = st.session_state.metal_settings[edit_metal]
                    
                    with col3:
                        edit_rate = st.number_input("Rate/g", value=edit_settings['rate'], format="%.2f", key=f"edit_rate_{invoice['id']}")
                    
                    with col4:
                        edit_wastage = st.number_input("Wastage %", value=edit_settings['wastage'], format="%.2f", key=f"edit_wastage_{invoice['id']}")
                    
                    edit_making = st.number_input("Making %", value=edit_settings['making'], format="%.2f", key=f"edit_making_{invoice['id']}")
                    
                    if st.button("➕ Add Item", key=f"add_edit_item_{invoice['id']}"):
                        if edit_weight > 0:
                            totals = calculate_item_totals(edit_weight, edit_rate, edit_wastage, edit_making)
                            edit_items.append({
                                'metal': edit_metal,
                                'weight': edit_weight,
                                'rate': edit_rate,
                                'wastage_percent': edit_wastage,
                                'making_percent': edit_making,
                                'item_value': totals['item_value'],
                                'wastage_amount': totals['wastage_amount'],
                                'making_amount': totals['making_amount'],
                                'line_total': totals['line_total']
                            })
                            st.session_state.temp_edit_items = edit_items
                            st.rerun()
                    
                    if st.button("🗑️ Remove Last Item", key=f"remove_edit_item_{invoice['id']}"):
                        if edit_items:
                            edit_items.pop()
                            st.session_state.temp_edit_items = edit_items
                            st.rerun()
                    
                    # Update discount
                    edit_discount = st.number_input(
                        "Discount %", 
                        min_value=0.0, 
                        value=float(invoice['discount_percent']), 
                        format="%.2f",
                        key=f"edit_discount_{invoice['id']}"
                    )
                    
                    # Save changes
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("💾 Save Changes", key=f"save_edit_{invoice['id']}"):
                            try:
                                db.update_invoice(
                                    invoice['id'],
                                    edit_items,
                                    invoice['cgst_percent'],
                                    invoice['sgst_percent'],
                                    edit_discount
                                )
                                st.success("✅ Invoice updated successfully!")
                                del st.session_state.editing_invoice_id
                                del st.session_state.editing_invoice_no
                                if 'temp_edit_items' in st.session_state:
                                    del st.session_state.temp_edit_items
                                if 'temp_edit_items_invoice_id' in st.session_state:
                                    del st.session_state.temp_edit_items_invoice_id
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error updating invoice: {str(e)}")
                    
                    with col2:
                        if st.button("❌ Cancel Edit", key=f"cancel_edit_{invoice['id']}"):
                            del st.session_state.editing_invoice_id
                            del st.session_state.editing_invoice_no
                            if 'temp_edit_items' in st.session_state:
                                del st.session_state.temp_edit_items
                            if 'temp_edit_items_invoice_id' in st.session_state:
                                del st.session_state.temp_edit_items_invoice_id
                            st.rerun()
