"""
JewelCalc - Jewelry Billing & Customer Management System
A clean, streamlined Streamlit application for jewelry shops
"""
import streamlit as st
import pandas as pd
from database import Database
from utils import format_currency, generate_invoice_number, generate_account_number, validate_phone, calculate_item_totals
from pdf_generator import create_invoice_pdf, get_pdf_download_link
import os


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
    /* Hide Streamlit branding */
    [data-testid="stToolbar"] {visibility: hidden;}
    [data-testid="stDecoration"] {visibility: hidden;}
    [data-testid="stStatusWidget"] {visibility: hidden;}
    
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


# Initialize session state
def init_session_state():
    """Initialize session state variables"""
    if 'db_path' not in st.session_state:
        st.session_state.db_path = 'jewelcalc.db'
    
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
    st.info(f"Current DB: `{st.session_state.db_path}`")
    
    with st.expander("Change Database"):
        new_db = st.text_input("Database filename", value="jewelcalc.db")
        if st.button("Switch Database"):
            if new_db.endswith('.db'):
                st.session_state.db_path = new_db
                st.rerun()
            else:
                st.error("Database filename must end with .db")

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
                
                # PDF download
                if st.button(f"📄 Download PDF", key=f"pdf_{row['invoice_no']}"):
                    pdf_buffer = create_invoice_pdf(invoice, items_df, customer)
                    st.markdown(
                        get_pdf_download_link(pdf_buffer, f"{row['invoice_no']}.pdf"),
                        unsafe_allow_html=True
                    )
