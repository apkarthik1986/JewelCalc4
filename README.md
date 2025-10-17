# JewelCalc 💎

**A clean, modern jewelry billing and customer management system built with Streamlit.**

JewelCalc is designed for jewelry shops to manage customers, create invoices with multiple items, apply taxes and discounts, and generate professional PDF bills. All data is stored locally on your device for complete privacy.

---

## ✨ Features

### Core Features
- **👥 Customer Management** - Add, edit, search, and delete customer records
- **📝 Invoice Creation** - Create multi-item invoices with automatic calculations
- **💰 Tax & Discount** - Built-in CGST/SGST calculation with discount support
- **📄 PDF Export** - Generate professional PDF invoices
- **🖨️ Print Support** - Direct printing and thermal printer (80mm) format
- **⚙️ Configurable Settings** - Customize metal rates, wastage, and making charges
- **🗄️ Database Management** - SQLite backend with backup/restore capability
- **🔐 Local Storage** - All data stored locally on your device (PC/mobile)

### Advanced Features
- **✏️ Invoice Editing** - Edit existing invoices, add/remove items
- **📥📤 Import/Export** - Export/import customers (CSV) and invoices (JSON)
- **🔄 Reset All Data** - Complete database reset option
- **📱 Device-Specific Storage** - Each device maintains its own local database
- **🧾 Thermal Printing** - Special format for 80mm receipt printers

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or newer
- pip (Python package manager)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/apkarthik1986/JewelCalc1.git
   cd JewelCalc1
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   streamlit run app.py
   ```
   
   Or use the convenience script:
   ```bash
   ./run.sh
   ```

4. **Access the app:**
   The application will automatically open at `http://localhost:8501`

---

## 📖 Usage Guide

### First Time Setup

**Step 1: Configure Settings**
1. Go to **⚙️ Settings** tab
2. Review and adjust metal rates (Gold 24K, 22K, 18K, Silver)
3. Set wastage % and making % for each metal
4. Configure CGST and SGST percentages
5. Click **💾 Save Settings**

**Step 2: Add Customers**
1. Go to **👥 Customers** tab
2. Click **Add Customer**
3. Fill in customer details (account number auto-generated)
4. Click **➕ Add Customer**

**Step 3: Create Invoices**
1. Go to **📝 Create Invoice** tab
2. Select customer from dropdown
3. Add items (metal, weight, rate, etc.)
4. Apply discount if needed
5. Click **💾 Save Invoice**

**Step 4: View/Download Invoices**
1. Go to **📋 View Invoices** tab
2. Browse or search for invoices
3. Click on an invoice to expand details
4. Use **📄 Download PDF** or **🖨️ Print PDF**

### Daily Workflow

**Creating Invoices**
- Select customer → Add items → Review calculations → Save

**Managing Customers**
- **Search:** Use search box to find by name or phone
- **Edit:** Select "Edit Customer" option
- **Delete:** Use with caution (deletes all customer invoices)

**Database Management (Sidebar)**
- View current device ID and database
- Switch between different databases
- Backup/restore database files

---

## 🗄️ Local Storage & Device-Specific Data

### How It Works
- Each device gets a **unique device ID** based on system information
- Database files are named: `jewelcalc_[device_id].db`
- Data on PC stays on PC, data on mobile stays on mobile
- No cloud synchronization - complete local storage

### Managing Multiple Devices
If you want to share data between devices:
1. Use **💾 Backup DB** on one device
2. Transfer the backup file
3. Use **📂 Restore DB** on the other device

### Multiple Databases
You can maintain separate databases:
- `jewelcalc_abc12345.db` - Your PC
- `jewelcalc_def67890.db` - Your mobile
- `store1.db` - Branch 1
- `test.db` - Testing

Use the sidebar to switch between databases.

---

## 📊 Calculations

### Item Level Calculations
```
item_value = weight × rate
wastage_amount = item_value × (wastage% / 100)
making_amount = item_value × (making% / 100)
line_total = item_value + wastage_amount + making_amount
```

### Invoice Level Calculations
```
subtotal = sum of all line_totals
discount_amount = subtotal × (discount% / 100)
taxable_amount = subtotal - discount_amount
cgst_amount = taxable_amount × (cgst% / 100)
sgst_amount = taxable_amount × (sgst% / 100)
total = taxable_amount + cgst_amount + sgst_amount
```

---

## 🔧 Advanced Features

### Invoice Editing
1. Find the invoice in **View Invoices** tab
2. Click **✏️ Edit Invoice**
3. Add or remove items
4. Modify discount
5. Click **💾 Save Changes**

### Import/Export Data

**Export Customers (CSV):**
- Customers tab → **📥 Export Customers**
- Download CSV file for backup

**Import Customers (CSV):**
- Prepare CSV with headers: `account_no, name, phone, address`
- Customers tab → Upload CSV → **Confirm Import**

**Export Invoices (JSON):**
- View Invoices tab → **📥 Export All Invoices**
- Complete backup of all invoice data

**Import Invoices (JSON):**
- View Invoices tab → Upload JSON → **Confirm Import**
- Note: Customers must exist before importing invoices

### Reset All Data
1. Go to **⚙️ Settings** tab
2. Scroll to **🔄 Reset Database** section
3. Click **🗑️ Reset All Data**
4. Confirm by clicking **✅ YES, DELETE EVERYTHING**
5. All customers, invoices, and data will be deleted

⚠️ **Warning:** This action cannot be undone! Create a backup first.

---

## 🏗️ Project Structure

```
JewelCalc1/
├── app.py              # Main Streamlit application (UI)
├── database.py         # Database operations (SQLite)
├── utils.py            # Utility functions
├── pdf_generator.py    # PDF generation (ReportLab)
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

### Technology Stack
- **Frontend:** Streamlit
- **Database:** SQLite3
- **PDF Generation:** ReportLab
- **Data Processing:** Pandas

---

## 🛠️ Troubleshooting

### App Won't Start
```bash
# Check Python version (must be 3.8+)
python --version

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Database Errors
If database is corrupted:
```bash
# Backup current database
mv jewelcalc_*.db jewelcalc_backup.db

# Restart app (new database will be created)
streamlit run app.py
```

### Module Not Found
```bash
pip install streamlit pandas reportlab
```

### PDF Not Downloading
- Check browser download settings
- Disable pop-up blockers for print PDF
- Ensure sufficient disk space

### Import Errors
- Check CSV/JSON format matches requirements
- Ensure all required fields are present
- Verify customer IDs exist before importing invoices

---

## 🔒 Security & Privacy

- **Local Storage:** All data stays on your device
- **No Cloud:** No internet connection required
- **File Security:** Keep database files secure
- **Backups:** Store backup files safely
- **Exports:** CSV/JSON files contain sensitive data - handle with care

---

## 💡 Tips & Best Practices

1. **Regular Backups** - Create backups before major changes
2. **Export Data** - Periodically export for redundancy
3. **Test First** - Use a test database for training
4. **Update Rates** - Keep metal rates current
5. **Phone Validation** - System enforces 10-digit phone numbers
6. **Unique Phones** - Each customer must have unique phone

---

## 📋 Requirements

- Python 3.8 or newer
- streamlit >= 1.25.0
- pandas
- numpy
- reportlab
- python-dotenv

Install all requirements:
```bash
pip install -r requirements.txt
```

---

## 🤝 Support

For issues or questions:
1. Check this documentation
2. Review error messages carefully
3. Test with a backup database
4. Open an issue on GitHub

---

## 📜 License

MIT License

---

## 📞 Contact

**Developer:** apkarthik1986  
**Repository:** https://github.com/apkarthik1986/JewelCalc1

---

**JewelCalc** - Clean, reliable billing for jewelry shops. 💎
