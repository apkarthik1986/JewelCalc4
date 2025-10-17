# JewelCalc - Developer Documentation

## Overview

JewelCalc is a clean, modular jewelry billing and customer management system built with Streamlit. The application has been completely rewritten from scratch with a focus on:

- **Clean Code:** Modular design with separated concerns
- **Maintainability:** Easy to understand and modify
- **Extensibility:** Simple to add new features
- **Performance:** Efficient database operations

## Architecture

### Module Structure

```
JewelCalc1/
├── app.py              # Main Streamlit application (UI layer)
├── database.py         # Database operations (Data layer)
├── utils.py            # Utility functions (Helper layer)
├── pdf_generator.py    # PDF generation (Output layer)
└── requirements.txt    # Python dependencies
```

### Module Details

#### 1. `database.py`
Handles all database operations using SQLite.

**Key Classes:**
- `Database`: Main database handler

**Key Methods:**
- `add_customer()`: Add new customer
- `get_customers()`: Retrieve all customers
- `update_customer()`: Update customer details
- `delete_customer()`: Delete customer and related invoices
- `save_invoice()`: Save invoice with items
- `get_invoices()`: Get all invoices
- `get_invoice_by_number()`: Get specific invoice with items

**Database Schema:**
```sql
customers:
  - id (PRIMARY KEY)
  - account_no (UNIQUE)
  - name
  - phone (UNIQUE)
  - address

invoices:
  - id (PRIMARY KEY)
  - invoice_no (UNIQUE)
  - customer_id (FOREIGN KEY)
  - date
  - subtotal
  - cgst_percent, cgst_amount
  - sgst_percent, sgst_amount
  - discount_percent, discount_amount
  - total

invoice_items:
  - id (PRIMARY KEY)
  - invoice_id (FOREIGN KEY)
  - item_no
  - metal
  - weight
  - rate
  - wastage_percent, wastage_amount
  - making_percent, making_amount
  - item_value
  - line_total
```

#### 2. `utils.py`
Utility functions for common operations.

**Key Functions:**
- `format_currency(amount)`: Format numbers as currency (₹)
- `generate_invoice_number()`: Generate unique invoice numbers
- `generate_account_number(existing)`: Generate sequential account numbers
- `validate_phone(phone)`: Validate 10-digit phone numbers
- `calculate_item_totals()`: Calculate item values, wastage, making charges

#### 3. `pdf_generator.py`
PDF generation using ReportLab.

**Key Functions:**
- `create_invoice_pdf(invoice, items, customer)`: Generate PDF from invoice data
- `get_pdf_download_link(pdf_buffer)`: Create HTML download link

**PDF Contents:**
- Header with invoice number and date
- Customer information
- Itemized list with calculations
- Tax and discount breakdown
- Total amount

#### 4. `app.py`
Main Streamlit application with UI.

**Structure:**
- Session state initialization
- Four main tabs:
  1. Settings: Configure metals and tax rates
  2. Customers: Add, edit, delete, search customers
  3. Create Invoice: Build and save new invoices
  4. View Invoices: Browse, search, and download PDFs

## Key Features

### 1. Metal Settings
- Configurable metal types (Gold 24K, 22K, 18K, Silver)
- Customizable rates per gram
- Adjustable wastage and making percentages
- Easy to add new metal types via data editor

### 2. Customer Management
- Automatic account number generation (CUS-00001, CUS-00002, etc.)
- Phone number validation (10 digits required)
- Unique phone constraint
- Full CRUD operations
- Search functionality

### 3. Invoice Creation
- Multi-item invoices
- Real-time calculation of:
  - Item value (weight × rate)
  - Wastage amount (item_value × wastage%)
  - Making charges (item_value × making%)
  - Line total (item_value + wastage + making)
- Discount support (percentage-based)
- Tax calculation (CGST + SGST on taxable amount)
- Invoice preview before saving

### 4. Invoice Management
- List all invoices with search
- Expandable detail view
- PDF generation and download
- Customer information display
- Full calculation breakdown

## Calculations

### Item Level:
```
item_value = weight × rate
wastage_amount = item_value × (wastage% / 100)
making_amount = item_value × (making% / 100)
line_total = item_value + wastage_amount + making_amount
```

### Invoice Level:
```
subtotal = sum(all line_totals)
discount_amount = subtotal × (discount% / 100)
taxable_amount = subtotal - discount_amount
cgst_amount = taxable_amount × (cgst% / 100)
sgst_amount = taxable_amount × (sgst% / 100)
total = taxable_amount + cgst_amount + sgst_amount
```

## Extension Points

### Adding New Metal Types
1. Go to Settings tab
2. Use data editor to add new row
3. Save settings
4. New metal appears in invoice creation

### Modifying Calculations
Edit `calculate_item_totals()` in `utils.py`

### Customizing PDF Layout
Modify `create_invoice_pdf()` in `pdf_generator.py`

### Adding Database Fields
1. Update table creation in `database.py` `_init_database()`
2. Update relevant CRUD methods
3. Update UI in `app.py`

## Testing

### Manual Testing Steps:
1. **Settings**
   - Modify metal rates
   - Change tax percentages
   - Add/remove metals
   - Save and verify persistence

2. **Customers**
   - Add customer (validate phone format)
   - Search customers
   - Edit customer details
   - Delete customer (verify cascade delete of invoices)

3. **Invoices**
   - Create invoice with multiple items
   - Apply discount
   - Verify calculations
   - Save and check invoice list
   - Download PDF and verify content

### Unit Tests:
See the test commands in git history for examples of testing individual modules.

## Performance Considerations

- **Database Indexing:** Primary keys and unique constraints on frequently queried fields
- **Lazy Loading:** Invoices loaded on demand with expandable UI
- **Caching:** PDF generation cached by Streamlit
- **Connection Management:** Database connections properly opened and closed

## Security Notes

- **Database Files:** Stored locally, excluded from git via `.gitignore`
- **No Authentication:** This is a local application
- **Input Validation:** Phone numbers, required fields validated
- **SQL Injection:** Protected via parameterized queries

## Future Enhancement Ideas

1. **Multi-user Support:** Add login/authentication
2. **Backup/Restore:** Database backup functionality
3. **Reports:** Sales reports, customer history
4. **Search Enhancement:** Advanced filtering options
5. **Batch Operations:** Bulk customer import/export
6. **Payment Tracking:** Track payments against invoices
7. **GST Compliance:** Additional GST reporting features
8. **Email Integration:** Email invoices directly to customers
9. **Mobile Responsiveness:** Optimize for mobile devices
10. **Barcode/QR Codes:** Generate codes for invoices

## Troubleshooting

### Database Issues
- If database is corrupted, delete the `.db` file and restart
- Application will create fresh database with tables

### Module Import Errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version (3.8+ required)

### PDF Generation Issues
- Verify ReportLab is installed
- Check write permissions in directory
- Ensure sufficient disk space

## Maintenance

### Regular Tasks:
1. Backup database files regularly
2. Review and update metal rates
3. Monitor application logs for errors
4. Keep dependencies updated

### Version Updates:
```bash
pip install --upgrade -r requirements.txt
```

## License

MIT License - See LICENSE file for details

---

**Developer Contact:** apkarthik1986  
**Repository:** https://github.com/apkarthik1986/JewelCalc1
