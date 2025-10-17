# Quick Start Guide - New Features

This guide helps you quickly get started with JewelCalc's new features.

## 🚀 Quick Actions

### Download & Print Invoices

1. Go to **View Invoices** tab
2. Click on any invoice to expand it
3. Choose your action:
   - **📄 Download PDF** - Saves invoice as PDF file
   - **🖨️ Print PDF** - Opens in browser for printing
   - **🧾 Thermal Print** - Downloads 80mm thermal printer format

### Edit an Invoice

1. Go to **View Invoices** tab
2. Expand the invoice you want to edit
3. Click **✏️ Edit Invoice**
4. Add or remove items as needed
5. Adjust discount if needed
6. Click **💾 Save Changes**

### Backup Your Database

1. Open the **sidebar**
2. Expand **Database Operations**
3. Click **💾 Backup DB**
4. Your backup is saved with timestamp (e.g., `backup_YYYYMMDD_HHMMSS.db`)

### Export Customers

1. Go to **Customers** tab
2. Scroll to **Import/Export Customers** section
3. Click **📥 Export Customers (CSV)**
4. Click **💾 Download CSV** button
5. Save the file

### Import Customers

1. Prepare a CSV file with these exact column headers (first row): `account_no,name,phone,address`
   Example format:
   ```
   account_no,name,phone,address
   CUS-00001,John Doe,1234567890,123 Main St
   ```
2. Go to **Customers** tab
3. Click **📤 Import Customers (CSV)**
4. Choose your CSV file
5. Click **Confirm Import Customers**

### Export Invoices

1. Go to **View Invoices** tab
2. Click **📥 Export All Invoices (JSON)**
3. Click **💾 Download JSON** button
4. Save the file

### Import Invoices

1. Ensure all customers exist first (import customers if needed)
2. Go to **View Invoices** tab
3. Click **📤 Import Invoices (JSON)**
4. Choose your JSON file
5. Click **Confirm Import Invoices**

## 💡 Pro Tips

### For Multiple Stores
1. Create separate databases for each store:
   - `store1.db`
   - `store2.db`
   - `store3.db`
2. Switch between them using the sidebar

### For Testing
1. Create a `test.db` database
2. Practice with sample data
3. Delete it when done

### For Backup Strategy
1. **Daily**: Export customers and invoices
2. **Weekly**: Create database backup
3. **Monthly**: Store backups in a safe location

### For Thermal Printing
1. Test the thermal print format first
2. Adjust printer settings if needed
3. Most thermal printers support 80mm width
4. Use good quality thermal paper

## 🔧 Common Tasks

### Moving Data to Another Computer

**Export Method:**
1. Export customers to CSV
2. Export invoices to JSON
3. Copy files to new computer
4. Import on new computer in order: customers first, then invoices

**Backup Method:**
1. Click **💾 Backup DB** in sidebar
2. Copy the backup file to new computer
3. On new computer, use **📂 Restore DB** to load it

### Recovering from Mistakes

If you made a mistake:
1. Use your latest backup
2. Click **📂 Restore DB** in sidebar
3. Select the backup file
4. Click **Confirm Restore**

### Starting Fresh

To start with a clean database:
1. In sidebar, enter a new database name (e.g., `new.db`)
2. Click **Switch Database**
3. New database is created automatically

## 📱 Mobile Usage

All features work on mobile devices:
- Touch-friendly interface
- Responsive design
- Local storage on your device
- No internet required after initial load

## 🔐 Security Tips

1. **Backup Regularly** - Data loss can happen
2. **Secure Your Device** - Database files contain customer data
3. **Export Before Updates** - Always backup before major changes
4. **Test Imports** - Use a test database first
5. **Keep Backups Safe** - Store in multiple locations

## ❓ Need Help?

1. Check [FEATURES.md](FEATURES.md) for detailed documentation
2. Review error messages carefully
3. Test with sample data first
4. Check the troubleshooting section in FEATURES.md

---

**Happy Billing!** 💎
