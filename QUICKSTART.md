# JewelCalc Quick Start Guide

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup Steps

1. **Clone the Repository**
```bash
git clone https://github.com/apkarthik1986/JewelCalc1.git
cd JewelCalc1
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the Application**
```bash
streamlit run app.py
```

Or use the convenience script:
```bash
./run.sh
```

4. **Open in Browser**
The application will automatically open at `http://localhost:8501`

## First Time Setup

### Step 1: Configure Settings
1. Click on the **⚙️ Settings** tab
2. Review the default metal rates (Gold 24K, 22K, 18K, Silver)
3. Adjust rates, wastage %, and making % as needed
4. Set your preferred CGST and SGST percentages
5. Click **💾 Save Settings**

### Step 2: Add Your First Customer
1. Go to **👥 Customers** tab
2. Select **Add Customer** option
3. Fill in:
   - Account Number (auto-generated as CUS-00001)
   - Customer Name
   - Phone Number (must be 10 digits)
   - Address (optional)
4. Click **➕ Add Customer**

### Step 3: Create Your First Invoice
1. Go to **📝 Create Invoice** tab
2. Select the customer from dropdown
3. Add items:
   - Select metal type
   - Enter weight in grams
   - Adjust rate/wastage/making if needed
   - Click **➕ Add Item to Invoice**
4. Add more items as needed
5. Apply discount if required
6. Review the invoice summary
7. Click **💾 Save Invoice**

### Step 4: View and Download Invoice
1. Go to **📋 View Invoices** tab
2. Find your invoice in the list
3. Click on the invoice to expand details
4. Click **📄 Download PDF** to get a printable copy

## Daily Workflow

### Creating Invoices
1. Go to Create Invoice tab
2. Select customer
3. Add all items
4. Apply discount (if any)
5. Review calculations
6. Save invoice

### Managing Customers
- **Search:** Use the search box to find customers by name or phone
- **Edit:** Select "Edit Customer" and choose the customer to modify
- **Delete:** Use with caution - this deletes all customer invoices too

### Viewing Past Invoices
- Use the search box to find specific invoices
- Click on invoice to see full details
- Download PDFs as needed for printing or emailing

## Tips and Tricks

### Metal Rates
- Update rates regularly to reflect market prices
- You can add new metal types in Settings
- Each metal can have different wastage and making percentages

### Account Numbers
- Auto-generated in sequence: CUS-00001, CUS-00002, etc.
- You can customize the number when adding customers

### Discounts
- Applied as percentage of subtotal
- Tax is calculated on amount after discount

### Database
- Default database is `jewelcalc.db`
- Create separate databases for different shops/branches
- Database files are automatically excluded from git

### PDF Invoices
- Professional format with all details
- Includes customer info, items, calculations
- Ready to print or email

## Troubleshooting

### App Won't Start
```bash
# Check Python version
python --version  # Should be 3.8+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Database Errors
If you encounter database errors, you can start fresh:
```bash
# Backup old database
mv jewelcalc.db jewelcalc.db.backup

# Restart app - new database will be created
streamlit run app.py
```

### Module Not Found
```bash
# Install specific module
pip install streamlit pandas reportlab
```

## Common Questions

**Q: Can I use this for multiple shops?**  
A: Yes! Create different database files for each shop using the sidebar.

**Q: How do I backup my data?**  
A: Simply copy the `.db` files to a safe location. All data is in these files.

**Q: Can I customize the PDF format?**  
A: Yes, edit `pdf_generator.py` to customize the PDF layout and styling.

**Q: What if I delete a customer by mistake?**  
A: Make regular backups of your database files. There's no undo feature.

**Q: Can multiple users access this at the same time?**  
A: This is designed as a single-user desktop application. For multi-user, deploy on a server.

## Getting Help

- Check `DEVELOPER.md` for technical details
- Review the code - it's well-commented and modular
- Open an issue on GitHub for bugs or feature requests

## Next Steps

- Customize metal types and rates for your business
- Add all your customers
- Start creating invoices
- Keep your database backed up regularly

---

Happy Billing! 💎
