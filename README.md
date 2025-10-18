# JewelCalc 💎

**A professional, multi-user jewellery billing and customer management system built with Streamlit.**

JewelCalc is designed for jewellery shops to manage customers, create invoices with multiple items, apply taxes and discounts, and generate professional PDF bills. Features a complete user authentication system with admin approval workflow and separate databases per user for enhanced security and privacy.

---

## ✨ Features

### Core Features
- **🔐 User Authentication** - Secure signup/login system with admin approval
- **👥 Multi-User Support** - Separate databases for each user with admin oversight
- **👨‍💼 Admin Panel** - Approve users, manage roles, monitor all databases
- **📊 Customer Management** - Add, edit, search, and delete customer records
- **📝 Invoice Creation** - Create multi-item invoices with automatic calculations
- **💰 Tax & Discount** - Built-in CGST/SGST calculation with discount support
- **📄 PDF Export** - Generate professional PDF invoices
- **🖨️ Smart Printing** - Printer selection dialog for any connected printer
- **⚙️ Configurable Settings** - Customize metal rates, wastage, and making charges
- **🗄️ Database Management** - Dedicated tab for backup/restore and import/export
- **📱 Mobile Responsive** - Optimized UI for mobile devices
- **🔐 Secure Storage** - User-specific local databases

### Advanced Features
- **✏️ Invoice Editing** - Edit existing invoices, add/remove items
- **📥📤 Import/Export** - Export/import customers (CSV) and invoices (JSON)
- **🔄 User Approval Workflow** - Admin reviews and approves new user registrations
- **👑 Role-Based Access** - Admin and regular user roles with different permissions
- **📊 Admin Dashboard** - View statistics across all user databases
- **🧾 Thermal Printing** - Special format for 80mm receipt printers
- **🔒 Data Isolation** - Each user's data stored separately and securely

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or newer
- pip (Python package manager)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/apkarthik1986/JewelCalc2.git
   cd JewelCalc2
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

5. **First time setup:**
   - Default admin credentials:
     - Username: `admin`
     - Password: `admin123`
   - **⚠️ Change the admin password after first login!**

---

## 📖 Usage Guide

### User Registration & Login

**For New Users:**
1. Click on **📝 Sign Up** tab
2. Fill in your details (username, full name, password)
3. Submit the registration form
4. Wait for admin approval

**For Existing Users:**
1. Click on **🔐 Login** tab
2. Enter your username and password
3. Click Login

**For Administrators:**
1. Login with admin credentials
2. Access the **🔐 Admin** tab
3. Review and approve pending user requests
4. Manage user roles and permissions

### First Time Setup (After Login)

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
4. Use **📄 Download PDF** or **🖨️ Print**

### Database Management

Navigate to **🗄️ Database** tab for:

**Backup & Restore:**
- Create backups of your database
- Download backups to your device
- Restore from previous backups

**Import/Export Data:**
- Export customers to CSV format
- Import customers from CSV
- Export invoices to JSON format
- Import invoices from JSON

### Admin Functions

Access **🔐 Admin** tab (admins only) for:

**User Management:**
- Approve or reject pending user registrations
- View all users in the system
- Change user roles (user ↔ admin)
- Delete user accounts
- Monitor user database status

**Database Overview:**
- View all user databases
- See statistics (customers, invoices, revenue)
- Monitor system-wide usage

---

## 🗄️ Multi-User Architecture

### How It Works
- **Central Authentication DB**: Stores all user credentials and roles
- **User-Specific DBs**: Each user gets their own database (`jewelcalc_user_[ID].db`)
- **Admin DB**: Admins have a separate database (`jewelcalc_admin.db`)
- **Data Isolation**: Users can only access their own data
- **Admin Oversight**: Admins can view statistics across all databases

### Security Features
- Password hashing (SHA-256)
- Session-based authentication
- Role-based access control
- Admin approval workflow
- Separate database per user

---

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

### Printer Selection
When printing invoices:
1. Click **🖨️ Print** button
2. Browser will open the print dialog
3. Select your preferred printer from the dropdown
4. Configure print settings as needed
5. Click Print to send to the selected printer

### User Management (Admin Only)
1. Go to **🔐 Admin** tab
2. Review pending user approvals
3. Approve or reject new users
4. Manage user roles and permissions
5. Monitor database usage across all users

---

## 🏗️ Project Structure

```
JewelCalc2/
├── app.py              # Main Streamlit application
├── auth.py             # Authentication and user management
├── database.py         # Database operations (SQLite)
├── utils.py            # Utility functions
├── pdf_generator.py    # PDF generation (ReportLab)
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

### Technology Stack
- **Frontend:** Streamlit (Mobile-Responsive)
- **Authentication:** Session-based with SHA-256 hashing
- **Database:** SQLite3 (Multi-database architecture)
- **PDF Generation:** ReportLab
- **Data Processing:** Pandas

---

## 🛠️ Troubleshooting

### Cannot Login
```
Issue: "Your account is pending approval"
Solution: Wait for an administrator to approve your account
```

### Forgot Admin Password
```bash
# Reset admin password by accessing the database directly
# Or contact the system administrator
```

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
- Disable pop-up blockers
- Ensure sufficient disk space

### Print Dialog Not Appearing
- Check browser pop-up settings
- Allow pop-ups for the application
- Try a different browser if issues persist

---

## 🔒 Security & Privacy

- **Password Hashing:** All passwords stored as SHA-256 hashes
- **Session Management:** Secure session-based authentication
- **Data Isolation:** Each user has separate database
- **Admin Approval:** New users require admin approval
- **Role-Based Access:** Different permissions for admin and users
- **Local Storage:** All data stays on your server
- **No Cloud:** No internet connection required
- **Backups:** Store backup files securely

---

## 💡 Tips & Best Practices

1. **Change Default Admin Password** - First priority after installation
2. **Regular Backups** - Create backups before major changes
3. **User Approvals** - Review user requests carefully
4. **Export Data** - Periodically export for redundancy
5. **Monitor Usage** - Use admin panel to monitor system usage
6. **Update Rates** - Keep metal rates current
7. **Phone Validation** - System enforces 10-digit phone numbers
8. **Mobile Access** - App is optimized for mobile devices

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
3. Check the admin panel for system status
4. Test with a backup database
5. Open an issue on GitHub

---

## 📜 License

MIT License

---

## 📞 Contact

**Developer:** apkarthik1986  
**Repository:** https://github.com/apkarthik1986/JewelCalc2

---

**JewelCalc** - Professional, secure billing for jewellery shops. 💎
