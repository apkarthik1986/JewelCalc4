# JewelCalc.py
# JewelCalc — Jewellery billing & customer manager (fixed: ie_new_metal Streamlit state bug)
import streamlit as st
import sqlite3
import pandas as pd
import random
import string
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import base64
from datetime import datetime
import re
import os

# Hide Streamlit style elements
hide_default_format = """
    <style>
    #[data-testid="stToolbar"] {visibility: hidden !important;}
    #[data-testid="stDecoration"] {visibility: hidden !important;}
    [data-testid="stStatusWidget"] {visibility: hidden !important;}
    [data-testid="stHeader"] {visibility: hidden !important;}
    [data-testid="stSidebarNav"] {visibility: visible !important;}
    [data-testid="stFooter"] {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    </style>
"""
st.markdown(hide_default_format, unsafe_allow_html=True)


# ---- UI THEME ----
st.set_page_config(page_title="JewelCalc", page_icon="💎", layout="wide", initial_sidebar_state="expanded")
st.markdown(
    """
    <style>
    .jewel-title-bar {
        position: fixed;
        top: 0;
        left: 0; right: 0;
        width: 100vw;
        z-index: 1002;
        background: linear-gradient(90deg, #e0f7fa 0%, #f5f7fa 100%);
        padding: 18px 0 10px 0;
        font-size: 2.3rem;
        font-weight: 800;
        letter-spacing: 0.04em;
        color: #1565c0;
        text-align: center;
        border-bottom: 2.5px solid #b2ebf2;
        box-shadow: 0 4px 24px 0 #0002;
        font-family: 'Segoe UI', SegoeUI, "Helvetica Neue", Arial, sans-serif;
    }
    .jewel-tab-bar-fixed {
        position: fixed;
        top: 40px;
        left: 0; right: 0;
        width: 100vw;
        z-index: 1001;
        background: linear-gradient(90deg,#f3e5f5 0%,#e1f5fe 100%);
        border-bottom: 2px solid #e1bee7;
        padding-bottom: 20;
        padding-top: 20px;      /* <-- Add this line */
        height: 64px;
        display: flex;
        justify-content: center;
        align-items: flex-start;
    }
    .jewel-tab-bar-fixed .element-container {margin-bottom:0 !important;}
    .jewel-btn {
        min-width: 140px;
        padding: 7px 18px 7px 18px;
        margin: 0px 6px 0px 6px;
        font-size: 1.08rem;
        font-weight: 700;
        color: #01579b;
        background: linear-gradient(90deg, #b3e5fc 0%, #ffd180 100%);
        border-radius: 12px 12px 0 0;
        border-bottom: 3px solid transparent;
        border: none;
        cursor: pointer;
        transition: all 0.18s;
        text-align: center;
        outline: none;
    }
    .jewel-btn.selected, .jewel-btn:focus {
        color: #4a148c;
        background: linear-gradient(90deg, #fffde7 0%, #e1bee7 100%);
        border-bottom: 4px solid #43a047;
        box-shadow: 0px 4px 18px #e1bee7;
    }
    .jewel-space {height:174px;}
    .main .block-container {padding-top:0;}
    </style>
    """,
    unsafe_allow_html=True,
)
st.markdown('<div class="jewel-title-bar">💎 JewelCalc</div>', unsafe_allow_html=True)

tab_labels = [
    "🔧 Base Settings",
    "👥 Customers",
    "🧾 Invoice Entry",
    "📋 Invoices"
]
if "selected_tab" not in st.session_state:
    st.session_state["selected_tab"] = 0

# Fixed tab bar (native Streamlit columns + CSS)
st.markdown('<div class="jewel-tab-bar-fixed">', unsafe_allow_html=True)
tab_cols = st.columns(len(tab_labels), gap="small")
for i, label in enumerate(tab_labels):
    btn_class = "jewel-btn" + (" selected" if st.session_state["selected_tab"] == i else "")
    if tab_cols[i].button(label, key=f"tabbtn_{i}", use_container_width=True):
        st.session_state["selected_tab"] = i
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<div class="jewel-space"></div>', unsafe_allow_html=True)
selected_tab = st.session_state["selected_tab"]

# ---- DB Selection ----
if "db_path" not in st.session_state:
    st.session_state["db_path"] = "customers.db"
if "db_confirm_overwrite" not in st.session_state:
    st.session_state["db_confirm_overwrite"] = False
if "db_pending_create" not in st.session_state:
    st.session_state["db_pending_create"] = None

current_db_file = st.session_state["db_path"]
with st.sidebar:
    st.markdown(
        """<div style="font-size:1.2rem;font-weight:700;color:#00838f;margin-bottom:10px;">
        🗄️ Database Management
        </div>""",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<span style='font-size:1.03rem;color:#0277bd;'>Current DB:</span> <span style='font-size:1.03rem;background:#e1f5fe;border-radius:5px;padding:2px 12px;margin-left:4px;'>{current_db_file}</span>",
        unsafe_allow_html=True,
    )

    db_file_create = st.text_input("New DB file name (with .db)", value="jewelcalc.db", key="db_file_create_input")
    if st.button("Create DB File"):
        if not db_file_create.endswith(".db"):
            st.error("File name must end with .db")
        elif os.path.exists(db_file_create):
            st.session_state["db_pending_create"] = db_file_create
            st.session_state["db_confirm_overwrite"] = True
        else:
            open(db_file_create, "w").close()
            st.session_state["db_path"] = db_file_create
            for k in list(st.session_state.keys()):
                if k not in ("db_path", "db_confirm_overwrite", "db_pending_create"):
                    del st.session_state[k]
            st.rerun()

    if st.session_state.get("db_confirm_overwrite", False) and st.session_state.get("db_pending_create"):
        st.warning(f"File `{st.session_state['db_pending_create']}` already exists.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Replace Existing DB File?"):
                open(st.session_state["db_pending_create"], "w").close()
                st.session_state["db_path"] = st.session_state["db_pending_create"]
                st.session_state["db_confirm_overwrite"] = False
                st.session_state["db_pending_create"] = None
                for k in list(st.session_state.keys()):
                    if k not in ("db_path", "db_confirm_overwrite", "db_pending_create"):
                        del st.session_state[k]
                st.rerun()
        with col2:
            if st.button("Cancel Overwrite"):
                st.session_state["db_confirm_overwrite"] = False
                st.session_state["db_pending_create"] = None

    db_file_use = st.text_input("Use Existing DB file (with .db)", value=current_db_file, key="db_file_use_input")
    if st.button("Use DB File"):
        if not db_file_use.endswith(".db"):
            st.error("File name must end with .db")
        elif not os.path.exists(db_file_use):
            st.error("File does not exist.")
        else:
            st.session_state["db_path"] = db_file_use
            for k in list(st.session_state.keys()):
                if k not in ("db_path", "db_confirm_overwrite", "db_pending_create"):
                    del st.session_state[k]
            st.rerun()

DB_PATH = st.session_state["db_path"]

# ---- Session State Defaults ----
if "base_settings" not in st.session_state:
    st.session_state["base_settings"] = {
        "Gold 24K": {"rate": 6500.0, "wastage": 5.0, "making": 10.0},
        "Gold 22K": {"rate": 6000.0, "wastage": 6.0, "making": 12.0},
        "Gold 18K": {"rate": 5500.0, "wastage": 7.0, "making": 14.0},
        "Silver": {"rate": 75.0, "wastage": 3.0, "making": 8.0}
    }
if "base_cgst" not in st.session_state:
    st.session_state["base_cgst"] = 1.5
if "base_sgst" not in st.session_state:
    st.session_state["base_sgst"] = 1.5
if "discount" not in st.session_state:
    st.session_state["discount"] = 0.0
for key, default in {
    'invoice_items': [],
    'current_customer': None,
    'ie_new_rate': None,
    'ie_new_wast': None,
    'ie_new_making': None,
    'ie_new_weight': 0.0,
    'ie_new_metal': "Select Item",
    'add_account': None,
    'add_name': '',
    'add_phone': '',
    'add_address': '',
    'reset_form': False,
    'last_loaded_invoice': None,
    'discount': 0.0,
    'last_invoice_number': None,
    'last_generated_invoice_number': None
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# --- DB & Utility Functions (identical to previous full solutions) ---
def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)
def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_no TEXT,
            name TEXT,
            phone TEXT UNIQUE,
            address TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_no TEXT UNIQUE,
            customer_id INTEGER,
            date TEXT,
            cgst_percent REAL,
            sgst_percent REAL,
            subtotal REAL,
            cgst_amount REAL,
            sgst_amount REAL,
            discount REAL,
            total REAL,
            FOREIGN KEY(customer_id) REFERENCES customers(id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS invoice_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER,
            item_no INTEGER,
            metal TEXT,
            weight REAL,
            rate REAL,
            wastage_percent REAL,
            making_percent REAL,
            item_value REAL,
            wastage_amount REAL,
            making_amount REAL,
            line_total REAL,
            FOREIGN KEY(invoice_id) REFERENCES invoices(id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT,
            details TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute("PRAGMA table_info(invoices)")
    columns = [row[1] for row in c.fetchall()]
    if "discount" not in columns:
        c.execute("ALTER TABLE invoices ADD COLUMN discount REAL DEFAULT 0")
    conn.commit()
    conn.close()
def log_action(action, details):
    try:
        conn = get_conn()
        c = conn.cursor()
        c.execute('INSERT INTO audit_log (action, details) VALUES (?, ?)', (action, str(details)))
        conn.commit()
        conn.close()
    except Exception:
        pass
def to_currency(x):
    try:
        return f"₹{float(x):,.2f}"
    except Exception:
        return f"₹{x}"
def next_account_no():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT account_no FROM customers WHERE account_no LIKE 'CUS-%'")
    rows = c.fetchall()
    max_n = 0
    pattern = re.compile(r"CUS-(\d+)")
    for (acct,) in rows:
        m = pattern.match(acct or "")
        if m:
            try:
                n = int(m.group(1))
                if n > max_n:
                    max_n = n
            except:
                pass
    conn.close()
    return f"CUS-{(max_n + 1):05d}"
def add_customer(account_no, name, phone, address):
    conn = get_conn()
    c = conn.cursor()
    c.execute('INSERT INTO customers (account_no, name, phone, address) VALUES (?, ?, ?, ?)',
              (account_no, name, phone, address))
    conn.commit()
    conn.close()
    log_action("add_customer", f"{account_no}, {name}, {phone}")
    return True
def update_customer(customer_id, account_no, name, phone, address):
    conn = get_conn()
    c = conn.cursor()
    c.execute('UPDATE customers SET account_no=?, name=?, phone=?, address=? WHERE id=?',
              (account_no, name, phone, address, customer_id))
    conn.commit()
    conn.close()
    log_action("update_customer", f"{customer_id}, {account_no}, {name}, {phone}")
def delete_customer(customer_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT id FROM invoices WHERE customer_id=?', (customer_id,))
    invoice_ids = [r[0] for r in c.fetchall()]
    if invoice_ids:
        for iid in invoice_ids:
            c.execute('DELETE FROM invoice_items WHERE invoice_id=?', (iid,))
        c.executemany('DELETE FROM invoices WHERE id=?', [(iid,) for iid in invoice_ids])
    c.execute('DELETE FROM customers WHERE id=?', (customer_id,))
    conn.commit()
    conn.close()
    log_action("delete_customer", f"Deleted customer {customer_id} and related invoices {invoice_ids}")
def get_customers_df():
    conn = get_conn()
    df = pd.read_sql_query('SELECT id, account_no, name, phone, address FROM customers ORDER BY id DESC', conn)
    conn.close()
    return df
def get_customer_by_id(customer_id):
    conn = get_conn()
    df = pd.read_sql_query('SELECT id, account_no, name, phone, address FROM customers WHERE id=?', conn, params=(customer_id,))
    conn.close()
    return df
def generate_invoice_number():
    for _ in range(5):
        letters = ''.join(random.choices(string.ascii_uppercase, k=4))
        numbers = ''.join(random.choices(string.digits, k=6))
        inv_no = f"{letters}-{numbers}"
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT 1 FROM invoices WHERE invoice_no=?", (inv_no,))
        exists = c.fetchone()
        conn.close()
        if not exists:
            return inv_no
    raise Exception("Could not generate unique invoice number.")
def save_invoice(customer_id, cgst_percent, sgst_percent, items, discount=0.0, date_str=None, invoice_no=None):
    if not items:
        raise ValueError("No items provided for invoice.")
    subtotal = sum(float(it.get("line_total", 0) or 0) for it in items)
    discount_amount = subtotal * (float(discount) / 100)
    taxable_subtotal = subtotal - discount_amount
    cgst_amount = taxable_subtotal * (float(cgst_percent) / 100)
    sgst_amount = taxable_subtotal * (float(sgst_percent) / 100)
    total = taxable_subtotal + cgst_amount + sgst_amount
    if not invoice_no:
        invoice_no = generate_invoice_number()
    conn = get_conn()
    c = conn.cursor()
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('''
        INSERT INTO invoices (invoice_no, customer_id, date, cgst_percent, sgst_percent, subtotal, cgst_amount, sgst_amount, discount, total)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (invoice_no, customer_id, date_str, cgst_percent, sgst_percent, subtotal, cgst_amount, sgst_amount, float(discount), total))
    invoice_id = c.lastrowid
    for idx, it in enumerate(items, start=1):
        c.execute('''
            INSERT INTO invoice_items (
                invoice_id, item_no, metal, weight, rate, wastage_percent, making_percent,
                item_value, wastage_amount, making_amount, line_total
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (invoice_id, idx, it["metal"], it["weight"], it["rate"], it["wastage_percent"], it["making_percent"],
              it["item_value"], it["wastage_amount"], it["making_amount"], it["line_total"]))
    conn.commit()
    conn.close()
    log_action("save_invoice", f"Invoice {invoice_no} for customer {customer_id}")
    return invoice_no
def get_all_invoices_df():
    conn = get_conn()
    df = pd.read_sql_query('''
        SELECT inv.id as invoice_id, inv.invoice_no, inv.date, inv.subtotal, inv.cgst_amount, inv.sgst_amount, inv.discount, inv.total,
               c.name as customer_name, c.phone as customer_phone, c.account_no as account_no,
               inv.cgst_percent, inv.sgst_percent, inv.customer_id
        FROM invoices inv
        LEFT JOIN customers c ON inv.customer_id = c.id
        ORDER BY inv.date DESC
    ''', conn)
    conn.close()
    return df
def get_invoice_by_no(invoice_no):
    conn = get_conn()
    inv_df = pd.read_sql_query('SELECT * FROM invoices WHERE invoice_no=?', conn, params=(invoice_no,))
    if inv_df.empty:
        conn.close()
        return None, None, None
    invoice_row = inv_df.iloc[0].to_dict()
    items_df = pd.read_sql_query('SELECT * FROM invoice_items WHERE invoice_id=? ORDER BY item_no', conn,
                                 params=(invoice_row["id"],))
    cust_df = pd.read_sql_query('SELECT id, account_no, name, phone, address FROM customers WHERE id=?', conn, params=(invoice_row["customer_id"],))
    conn.close()
    return invoice_row, items_df, (cust_df.iloc[0].to_dict() if not cust_df.empty else None)
@st.cache_data
def create_invoice_pdf_from_no(invoice_no):
    invoice_row, items_df, customer = get_invoice_by_no(invoice_no)
    if invoice_row is None:
        return None
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    x_margin = 40
    y = height - 50
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, y, "JewelCalc Invoice")
    y -= 30
    c.setFont("Helvetica", 10)
    c.drawString(x_margin, y, f"Invoice No: {invoice_row['invoice_no']}")
    c.drawString(width - 250, y, f"Date: {invoice_row['date']}")
    y -= 18
    if customer:
        c.drawString(x_margin, y, f"Account No: {customer.get('account_no','')}")
        c.drawString(width - 250, y, f"Phone: {customer.get('phone','')}")
        y -= 16
        c.drawString(x_margin, y, f"Customer: {customer.get('name','')}")
        y -= 16
        c.drawString(x_margin, y, f"Address: {customer.get('address','')}")
        y -= 20
    c.setFont("Helvetica-Bold", 10)
    headers = ["No", "Metal", "Wt(g)", "Rate", "ItemVal", "Wastage", "Making", "LineTotal"]
    xs = [x_margin, x_margin+40, x_margin+110, x_margin+160, x_margin+220, x_margin+300, x_margin+360, x_margin+430]
    for i,h in enumerate(headers):
        c.drawString(xs[i], y, h)
    y -= 14
    c.setFont("Helvetica", 10)
    for _, row in items_df.iterrows():
        if y < 80:
            c.showPage()
            y = height - 50
        c.drawString(xs[0], y, str(int(row["item_no"])))
        c.drawString(xs[1], y, str(row["metal"]))
        c.drawRightString(xs[2]+30, y, f"{row['weight']:.2f}")
        c.drawRightString(xs[3]+40, y, f"{row['rate']:.2f}")
        c.drawRightString(xs[4]+60, y, f"{row['item_value']:.2f}")
        c.drawRightString(xs[5]+40, y, f"{row['wastage_amount']:.2f}")
        c.drawRightString(xs[6]+40, y, f"{row['making_amount']:.2f}")
        c.drawRightString(xs[7]+60, y, f"{row['line_total']:.2f}")
        y -= 14
    y -= 10
    c.setFont("Helvetica-Bold", 11)
    c.drawRightString(width - x_margin, y, f"Subtotal: ₹{invoice_row['subtotal']:.2f}")
    if invoice_row.get("discount", 0):
        discount_amt = invoice_row['subtotal'] * (invoice_row['discount'] / 100)
        y -= 16
        c.drawRightString(width - x_margin, y, f"Discount ({invoice_row['discount']:.2f}%): ₹{discount_amt:.2f}")
        y -= 16
        c.drawRightString(width - x_margin, y, f"Taxable subtotal: ₹{invoice_row['subtotal']-discount_amt:.2f}")
        y -= 16
    else:
        y -= 16
    c.drawRightString(width - x_margin, y, f"CGST ({invoice_row['cgst_percent']}%): ₹{invoice_row['cgst_amount']:.2f}")
    y -= 16
    c.drawRightString(width - x_margin, y, f"SGST ({invoice_row['sgst_percent']}%): ₹{invoice_row['sgst_amount']:.2f}")
    y -= 16
    c.setFont("Helvetica-Bold", 14)
    c.drawRightString(width - x_margin, y, f"Total: ₹{invoice_row['total']:.2f}")
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer
def get_pdf_download_link_from_buffer(pdf_buffer, filename="invoice.pdf"):
    b64 = base64.b64encode(pdf_buffer.read()).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}" target="_blank">📄 Download PDF</a>'
    return href

init_db()
if not st.session_state['add_account']:
    st.session_state['add_account'] = next_account_no()

# Helper to safely reset item-entry widget-managed keys and rerun
def reset_item_entry_widgets_and_rerun():
    # Remove keys so that on next run the widget will be re-initialized safely
    for k in ("ie_new_metal", "ie_new_rate", "ie_new_wast", "ie_new_making", "ie_new_weight"):
        if k in st.session_state:
            del st.session_state[k]
    st.rerun()

# ------------- BASE SETTINGS TAB -------------
if selected_tab == 0:
    st.markdown(
        "<div style='font-size:1.25rem;font-weight:700;color:#00695c;background:#e0f2f1;border-radius:8px;padding:10px 22px;margin-bottom:12px;'>Base Values (Metals, GST)</div>",
        unsafe_allow_html=True
    )
    metals = list(st.session_state["base_settings"].keys())
    base_df = pd.DataFrame([
        {"Metal": m,
         "Rate": st.session_state["base_settings"][m]["rate"],
         "Wastage %": st.session_state["base_settings"][m]["wastage"],
         "Making %": st.session_state["base_settings"][m]["making"]}
        for m in metals
    ])
    edited = st.data_editor(base_df, num_rows="dynamic", width=900, key="base_data_editor")
    st.write("CGST / SGST (default %)")
    cgst = st.number_input("CGST (%)", value=st.session_state["base_cgst"], format="%.2f", key="base_cgst_input")
    sgst = st.number_input("SGST (%)", value=st.session_state["base_sgst"], format="%.2f", key="base_sgst_input")
    if st.button("Save Base Settings", key="save_base_settings"):
        new_settings = {}
        for _, r in edited.iterrows():
            if not r["Metal"]:
                continue
            new_settings[r["Metal"]] = {"rate": float(r["Rate"]), "wastage": float(r["Wastage %"]), "making": float(r["Making %"])}
        st.session_state["base_settings"] = new_settings
        st.session_state["base_cgst"] = float(cgst)
        st.session_state["base_sgst"] = float(sgst)
        st.success("Base settings saved.")

# ------------- CUSTOMERS TAB -------------
elif selected_tab == 1:
    st.markdown(
        "<div style='font-size:1.2rem;font-weight:700;color:#6a1b9a;background:#ede7f6;border-radius:8px;padding:10px 22px;margin-bottom:10px;'>Customers — Add · Edit · Delete</div>",
        unsafe_allow_html=True
    )
    if st.session_state.get('reset_form'):
        st.session_state['add_account'] = next_account_no()
        st.session_state['add_name'] = ''
        st.session_state['add_phone'] = ''
        st.session_state['add_address'] = ''
        st.session_state['reset_form'] = False

    customers = get_customers_df()
    col1, col2 = st.columns([2,1])
    with col1:
        q = st.text_input("Search by name or phone", "", key="cust_search")
        filtered = customers[customers["name"].fillna("").str.contains(q, case=False) |
                             customers["phone"].fillna("").str.contains(q)] if q else customers
        st.dataframe(filtered, width=900)
    with col2:
        st.markdown(
            "<div style='font-size:1.09rem;font-weight:600;color:#6d4c41;margin-bottom:6px;'>Manage Customer</div>",
            unsafe_allow_html=True
        )
        mode = st.radio("Mode", ["Add New", "Edit Existing", "Delete Existing"], key="cust_mode")
        if mode == "Add New":
            account_no = st.text_input("Account No", value=st.session_state['add_account'], key="add_account")
            name = st.text_input("Name", value=st.session_state['add_name'], key="add_name")
            phone = st.text_input("Phone", value=st.session_state['add_phone'], key="add_phone")
            address = st.text_area("Address", value=st.session_state['add_address'], key="add_address")
            if st.button("Add Customer", key="add_customer_btn"):
                if not (account_no.strip() and name.strip() and phone.strip()):
                    st.error("Account No, Name and Phone are required.")
                elif not phone.strip().isdigit() or len(phone.strip()) != 10:
                    st.error("Phone number must be 10 digits.")
                else:
                    try:
                        add_customer(account_no.strip(), name.strip(), phone.strip(), address.strip())
                        st.success("Customer added.")
                        st.session_state['reset_form'] = True
                        st.session_state['invoice_items'] = []
                        st.session_state['current_customer'] = None
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("Phone already exists. Use Edit mode to modify existing customer.")
        elif mode == "Edit Existing":
            cust_opts = customers.apply(lambda r: (r["id"], f"{r['name']} ({r['phone']})"), axis=1).tolist()
            if cust_opts:
                id_map = {label: cid for cid, label in cust_opts}
                sel = st.selectbox("Select customer", options=[""] + [label for _,label in cust_opts], key="edit_select")
                if sel:
                    cid = id_map[sel]
                    cust = get_customer_by_id(cid).iloc[0]
                    account_no = st.text_input("Account No", value=cust["account_no"], key=f"edit_acc_{cid}")
                    name = st.text_input("Name", value=cust["name"], key=f"edit_name_{cid}")
                    phone = st.text_input("Phone", value=cust["phone"], key=f"edit_phone_{cid}")
                    address = st.text_area("Address", value=cust["address"], key=f"edit_addr_{cid}")
                    if st.button("Save Changes", key=f"save_cust_{cid}"):
                        if not (account_no.strip() and name.strip() and phone.strip()):
                            st.error("Account No, Name and Phone are required.")
                        elif not phone.strip().isdigit() or len(phone.strip()) != 10:
                            st.error("Phone number must be 10 digits.")
                        else:
                            try:
                                update_customer(cid, account_no.strip(), name.strip(), phone.strip(), address.strip())
                                st.success("Customer updated.")
                                st.rerun()
                            except sqlite3.IntegrityError:
                                st.error("Phone conflicts with another customer.")
            else:
                st.info("No customers to edit.")
        else:
            cust_opts = customers.apply(lambda r: (r["id"], f"{r['name']} ({r['phone']})"), axis=1).tolist()
            if cust_opts:
                id_map = {label: cid for cid, label in cust_opts}
                sel = st.selectbox("Select customer to delete", options=[""] + [label for _,label in cust_opts], key="delete_select")
                if sel:
                    cid = id_map[sel]
                    confirm = st.checkbox("Confirm deletion of this customer and all related invoices?", key=f"confirm_delete_{cid}")
                    if confirm and st.button("Delete Customer", key=f"delete_cust_{cid}"):
                        delete_customer(cid)
                        st.success("Customer & related invoices deleted.")
                        st.rerun()
            else:
                st.info("No customers to delete.")

# ------------- INVOICE ENTRY TAB -------------
elif selected_tab == 2:
    st.subheader("Invoice Entry — Add multiple items / Edit loaded invoice")

    col_new, _ = st.columns([1,7])
    with col_new:
        if st.button("🆕 New Invoice", key="new_invoice_btn"):
            st.session_state['invoice_items'] = []
            st.session_state['current_customer'] = None
            st.session_state['discount'] = 0.0
            st.session_state['ie_new_rate'] = None
            st.session_state['ie_new_wast'] = None
            st.session_state['ie_new_making'] = None
            st.session_state['ie_new_weight'] = 0.0
            # SAFE RESET: delete widget-managed keys and rerun so widgets reinitialize cleanly
            reset_item_entry_widgets_and_rerun()
            st.session_state['last_loaded_invoice'] = None

    customers = get_customers_df()
    if "last_entry_tab" not in st.session_state or st.session_state.get("last_entry_tab") is None or st.session_state.get("last_entry_tab") != st.session_state.get("db_path", "customers.db"):
        st.session_state["invoice_items"] = []
        st.session_state["current_customer"] = None
        st.session_state["discount"] = 0.0
        st.session_state["last_loaded_invoice"] = None
    st.session_state["last_entry_tab"] = st.session_state.get("db_path", "customers.db")

    def update_item_defaults():
        metal = st.session_state.get("ie_new_metal", "Select Item")
        base_settings = st.session_state.get("base_settings", {})
        if metal == "Select Item":
            st.session_state['ie_new_rate'] = None
            st.session_state['ie_new_wast'] = None
            st.session_state['ie_new_making'] = None
        else:
            settings = base_settings.get(metal, {"rate": 0, "wastage": 0, "making": 0})
            st.session_state['ie_new_rate'] = settings.get("rate", 0)
            st.session_state['ie_new_wast'] = settings.get("wastage", 0)
            st.session_state['ie_new_making'] = settings.get("making", 0)

    if st.session_state.get("last_loaded_invoice"):
        load_inv = st.session_state["last_loaded_invoice"]
        invoice_row, items_df, _ = get_invoice_by_no(load_inv)
        st.session_state["invoice_items"] = items_df[['metal','weight','rate','wastage_percent','making_percent','item_value','wastage_amount','making_amount','line_total']].fillna(0).to_dict('records')
        st.session_state["current_customer"] = invoice_row["customer_id"]
        st.session_state["discount"] = float(invoice_row.get("discount", 0.0) or 0.0)
        st.session_state["last_loaded_invoice"] = None  # Only prefill once

    if customers.empty:
        st.warning("No customers found. Please add a customer in the 'Customers' tab first.")
    else:
        cust_map = {f"{r['name']} ({r['phone']})": int(r["id"]) for _, r in customers.iterrows()}
        sel_default = None
        if st.session_state.get('current_customer'):
            for k,v in cust_map.items():
                if v == st.session_state['current_customer']:
                    sel_default = k
                    break
        cust_choice = st.selectbox("Select Customer", options=[""] + list(cust_map.keys()), index=(list(cust_map.keys()).index(sel_default) + 1) if sel_default else 0, key="ie_cust_select")
        if cust_choice == "":
            st.info("Select a customer to begin invoice.")
        else:
            customer_id = cust_map[cust_choice]
            if st.session_state.get('current_customer') != customer_id:
                st.session_state['invoice_items'] = []
                st.session_state['discount'] = 0.0
                st.session_state['current_customer'] = customer_id

            st.markdown("### Add Item")
            metal_options = ["Select Item"] + list(st.session_state["base_settings"].keys())
            metal = st.selectbox(
                "Metal",
                options=metal_options,
                index=metal_options.index(st.session_state.get("ie_new_metal", "Select Item")),
                key="ie_new_metal",
                on_change=update_item_defaults
            )
            if metal == "Select Item":
                st.info("Please select a metal to proceed.")
            else:
                rate = st.number_input("Rate (per g)", value=st.session_state.get('ie_new_rate', st.session_state['base_settings'][metal]['rate']), format="%.2f", key="ie_new_rate")
                weight = st.number_input("Weight (g)", min_value=0.0, value=st.session_state.get('ie_new_weight', 0.0), format="%.2f", key="ie_new_weight")
                wastage_percent = st.number_input("Wastage %", value=st.session_state.get('ie_new_wast', st.session_state['base_settings'][metal]['wastage']), format="%.2f", key="ie_new_wast")
                making_percent = st.number_input("Making %", value=st.session_state.get('ie_new_making', st.session_state['base_settings'][metal]['making']), format="%.2f", key="ie_new_making")

                item_value = float(weight or 0) * float(rate or 0)
                wastage_amount = item_value * float(wastage_percent or 0) / 100
                making_amount = item_value * float(making_percent or 0) / 100
                line_total = item_value + wastage_amount + making_amount

                st.write(f"Item Value: {to_currency(item_value)} | Wastage: {to_currency(wastage_amount)} | Making: {to_currency(making_amount)}")
                st.write(f"Line Total (Before GST): {to_currency(line_total)}")

                if st.button("➕ Add Item to Invoice", key="ie_add_item"):
                    if metal == "Select Item":
                        st.error("Please select a metal.")
                    elif weight <= 0 or rate <= 0:
                        st.error("Weight and Rate must be positive numbers.")
                    else:
                        st.session_state['invoice_items'].append({
                            "metal": metal,
                            "weight": float(weight),
                            "rate": float(rate),
                            "wastage_percent": float(wastage_percent),
                            "making_percent": float(making_percent),
                            "item_value": float(item_value),
                            "wastage_amount": float(wastage_amount),
                            "making_amount": float(making_amount),
                            "line_total": float(line_total)
                        })
                        st.success("Item added.")
                        # SAFE RESET: remove widget-managed keys then rerun so the selectbox resets safely
                        for k in ("ie_new_rate","ie_new_wast","ie_new_making","ie_new_weight"):
                            st.session_state.pop(k, None)
                        # remove ie_new_metal (widget-managed) and rerun so it is re-created on next run
                        st.session_state.pop("ie_new_metal", None)
                        st.rerun()

            st.markdown("### Current Items")
            if st.session_state.get("invoice_items"):
                df_items = pd.DataFrame(st.session_state["invoice_items"])
                edited_df = st.data_editor(df_items, num_rows="dynamic", width=900, key="invoice_items_editor")
                recalculated = []
                for _, row in edited_df.iterrows():
                    try:
                        item_value = float(row.get("weight",0) or 0) * float(row.get("rate",0) or 0)
                        wastage_amount = item_value * float(row.get("wastage_percent",0) or 0) / 100
                        making_amount = item_value * float(row.get("making_percent",0) or 0) / 100
                        line_total = item_value + wastage_amount + making_amount
                    except Exception:
                        item_value = wastage_amount = making_amount = line_total = 0.0
                    recalculated.append({
                        "metal": row.get("metal",""),
                        "weight": float(row.get("weight",0) or 0),
                        "rate": float(row.get("rate",0) or 0),
                        "wastage_percent": float(row.get("wastage_percent",0) or 0),
                        "making_percent": float(row.get("making_percent",0) or 0),
                        "item_value": item_value,
                        "wastage_amount": wastage_amount,
                        "making_amount": making_amount,
                        "line_total": line_total
                    })
                st.session_state["invoice_items"] = recalculated
            else:
                st.info("No items yet. Add items above.")

            cgst_percent = st.number_input("CGST (%)", value=st.session_state["base_cgst"], format="%.2f", key="ie_cgst")
            sgst_percent = st.number_input("SGST (%)", value=st.session_state["base_sgst"], format="%.2f", key="ie_sgst")
            discount_percent = st.number_input("Discount (%)", min_value=0.0, value=st.session_state.get("discount", 0.0), format="%.2f", key="ie_discount")
            st.session_state["discount"] = discount_percent

            subtotal = sum(it.get("line_total",0) or 0 for it in st.session_state.get("invoice_items", []))
            discount_amt = subtotal * (discount_percent/100)
            taxable_subtotal = subtotal - discount_amt
            cgst_amt = taxable_subtotal * (float(cgst_percent)/100)
            sgst_amt = taxable_subtotal * (float(sgst_percent)/100)
            total = taxable_subtotal + cgst_amt + sgst_amt

            st.markdown("### Invoice Preview (Before Saving)")
            st.write(f"Subtotal: {to_currency(subtotal)}")
            if discount_percent and discount_percent > 0:
                st.write(f"Discount ({discount_percent:.2f}%): {to_currency(discount_amt)}")
            st.write(f"Taxable Subtotal: {to_currency(taxable_subtotal)}")
            st.write(f"CGST: {to_currency(cgst_amt)}  SGST: {to_currency(sgst_amt)}")
            st.markdown(f"### Total (With GST): {to_currency(total)}")

            if st.button("💾 Save Invoice", key="ie_save_invoice"):
                if not st.session_state.get("invoice_items"):
                    st.error("Add at least one item before saving invoice.")
                else:
                    try:
                        invoice_no = save_invoice(customer_id, float(cgst_percent), float(sgst_percent), st.session_state["invoice_items"], discount=discount_percent)
                        st.success(f"Invoice saved. Invoice No: {invoice_no}")
                        st.session_state["invoice_items"] = []
                        st.session_state["current_customer"] = None
                        st.session_state["discount"] = 0.0
                        # SAFE RESET: remove widget-managed keys so they are re-initialized next run
                        for k in ("ie_new_rate","ie_new_wast","ie_new_making","ie_new_weight"):
                            st.session_state.pop(k, None)
                        st.session_state.pop("ie_new_metal", None)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to save invoice: {e}")

# ------------- INVOICES TAB -------------
elif selected_tab == 3:
    st.subheader("Invoices — List · Filter · View · PDF · Load to Entry")
    inv_df = get_all_invoices_df()
    if inv_df.empty:
        st.info("No invoices yet.")
    else:
        filter_val = st.text_input("Search (Invoice No, Customer name, Phone)", key="inv_search")
        if filter_val:
            mask = (
                inv_df["invoice_no"].astype(str).str.contains(filter_val, case=False, na=False) |
                inv_df["customer_name"].astype(str).str.contains(filter_val, case=False, na=False) |
                inv_df["customer_phone"].astype(str).str.contains(filter_val, case=False, na=False)
            )
            filtered_df = inv_df[mask]
        else:
            filtered_df = inv_df

        st.write("### All Invoices")
        for i, row in filtered_df.iterrows():
            with st.expander(f"Invoice: {row['invoice_no']} — {row['customer_name']} ({to_currency(row['total'])}) — {row['date']}", expanded=False):
                invoice_no = row['invoice_no']
                invoice_row, items_df, customer = get_invoice_by_no(invoice_no)

                st.write(f"Date: {invoice_row['date']}")
                st.write(f"Customer: {customer.get('name','') if customer else ''}")
                st.write(f"Phone: {customer.get('phone','') if customer else ''}")
                st.write(f"Account: {customer.get('account_no','') if customer else ''}")
                st.divider()
                if not items_df.empty:
                    items_df_display = items_df[['item_no','metal','weight','rate','item_value','wastage_amount','making_amount','line_total']].copy()
                    st.dataframe(items_df_display, width=900)
                    subtotal = items_df['line_total'].sum()
                    discount_percent = invoice_row.get("discount", 0)
                    discount_amt = subtotal * (discount_percent/100)
                    taxable_subtotal = subtotal - discount_amt
                    cgst_amount = taxable_subtotal * invoice_row['cgst_percent']/100
                    sgst_amount = taxable_subtotal * invoice_row['sgst_percent']/100
                    st.divider()
                    st.write(f"Subtotal: {to_currency(subtotal)}")
                    if discount_percent and discount_percent > 0:
                        st.write(f"Discount ({discount_percent:.2f}%): {to_currency(discount_amt)}")
                    st.write(f"Taxable Subtotal: {to_currency(taxable_subtotal)}")
                    st.write(f"CGST ({invoice_row['cgst_percent']}%): {to_currency(cgst_amount)}")
                    st.write(f"SGST ({invoice_row['sgst_percent']}%): {to_currency(sgst_amount)}")
                    st.markdown(f"### Total: {to_currency(row['total'])}")
                colA, colB = st.columns(2)
                with colA:
                    if st.button("📄 Generate / Download PDF", key=f"inv_pdf_{invoice_no}"):
                        pdf_buf = create_invoice_pdf_from_no(invoice_no)
                        if pdf_buf:
                            st.markdown(get_pdf_download_link_from_buffer(pdf_buf, f"{invoice_no}.pdf"), unsafe_allow_html=True)
                            log_action("download_pdf", f"{invoice_no}")
                        else:
                            st.error("Unable to generate PDF.")
                with colB:
                    if st.button("🧾 Load for Editing in Entry Tab", key=f"load_inv_{invoice_no}"):
                        st.session_state['last_loaded_invoice'] = invoice_no
                        st.rerun()
