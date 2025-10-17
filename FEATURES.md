# JewelCalc - New Features Guide

This document describes the new features added to JewelCalc.

## 1. Enhanced PDF Functionality

### Direct Download PDF
- **Location**: View Invoices tab → Each invoice expander
- **Button**: "📄 Download PDF"
- The PDF is now downloaded directly without creating intermediate links
- Uses Streamlit's native download button for better user experience

### Print PDF
- **Location**: View Invoices tab → Each invoice expander
- **Button**: "🖨️ Print PDF"
- Opens the PDF in a new browser tab for printing
- Allows users to use browser's print dialog with print settings

### Thermal Print
- **Location**: View Invoices tab → Each invoice expander
- **Button**: "🧾 Thermal Print"
- Generates a PDF optimized for thermal printers (80mm width)
- Compact layout suitable for receipt printers
- Includes all invoice details in a vertical format

## 2. Database Management

### Show/Hide Database Panel
- **Location**: Sidebar
- **Button**: "🔽 Toggle Database Panel" / "▶️ Toggle Database Panel"
- Allows users to hide/show the database management section
- Saves screen space when not needed
- State is preserved during the session

### Database Backup & Restore
- **Location**: Sidebar → Database Operations expander

#### Backup Database
- **Button**: "💾 Backup DB"
- Creates a timestamped backup of the current database
- Format: `backup_YYYYMMDD_HHMMSS.db`
- Saved in the application directory

#### Restore Database
- **File Upload**: "📂 Restore DB"
- Upload a `.db` file to restore
- Click "Confirm Restore" to apply the backup
- **Warning**: This will replace the current database

## 3. Edit Invoice

### Edit Existing Invoices
- **Location**: View Invoices tab → Each invoice expander
- **Button**: "✏️ Edit Invoice"

#### Features:
- View current invoice items
- Add new items to the invoice
- Remove last item from the invoice
- Modify discount percentage
- Recalculates all totals automatically

#### How to Use:
1. Click "✏️ Edit Invoice" on any invoice
2. Review current items
3. Add new items using the form:
   - Select metal type
   - Enter weight, rate, wastage, and making percentages
   - Click "➕ Add Item"
4. Remove unwanted items with "🗑️ Remove Last Item"
5. Adjust discount if needed
6. Click "💾 Save Changes" to update
7. Or click "❌ Cancel Edit" to discard changes

## 4. Customer Import/Export

### Export Customers
- **Location**: Customers tab → Import/Export section
- **Button**: "📥 Export Customers (CSV)"
- Downloads all customers as a CSV file
- File name: `customers_export.csv`

#### CSV Format:
```csv
id,account_no,name,phone,address
1,CUS-00001,John Doe,1234567890,123 Main St
```

### Import Customers
- **Location**: Customers tab → Import/Export section
- **File Upload**: "📤 Import Customers (CSV)"
- Upload a CSV file with customer data
- Click "Confirm Import Customers" to process
- Shows number of imported customers and any errors

#### CSV Requirements:
- Must include headers: `account_no,name,phone,address`
- Phone numbers must be unique
- Account numbers must be unique
- Duplicate entries will be skipped with error messages

## 5. Invoice Import/Export

### Export Invoices
- **Location**: View Invoices tab → Import/Export section
- **Button**: "📥 Export All Invoices (JSON)"
- Downloads all invoices with items and customer data
- File name: `invoices_export.json`
- Format: JSON with complete invoice details

#### JSON Structure:
```json
[
  {
    "id": 1,
    "invoice_no": "ABCD-123456",
    "customer_id": 1,
    "date": "2024-01-01 10:00:00",
    "subtotal": 74750.0,
    "total": 77750.0,
    "items": [...],
    "customer": {...}
  }
]
```

### Import Invoices
- **Location**: View Invoices tab → Import/Export section
- **File Upload**: "📤 Import Invoices (JSON)"
- Upload a JSON file with invoice data
- Click "Confirm Import Invoices" to process
- Shows number of imported invoices and any errors

#### Import Notes:
- Customer IDs in the JSON must exist in the database
- Import customers first if needed
- Duplicate invoice numbers will cause errors
- Only valid invoices will be imported

## Local Storage

### Database Storage
- All data is stored in local SQLite database files
- Default database: `jewelcalc.db`
- No cloud storage - completely offline operation
- Data stays on your PC or mobile device

### Database Files
- Files end with `.db` extension
- Can have multiple databases for different purposes
- Switch between databases using the sidebar
- Example uses:
  - `jewelcalc.db` - Main database
  - `store1.db` - Branch 1
  - `store2.db` - Branch 2
  - `test.db` - Testing/training

### Creating New Database
- Simply enter a new filename ending with `.db` in the sidebar
- If the file doesn't exist, it will be created automatically
- All necessary tables are created on first use

## Tips and Best Practices

1. **Regular Backups**: Create backups before making major changes
2. **Export Data**: Periodically export customers and invoices for redundancy
3. **Test First**: Use a test database to familiarize yourself with features
4. **Thermal Printing**: Test thermal print format with your printer before production use
5. **Edit Carefully**: Always review invoice changes before saving
6. **Import Validation**: Check error messages when importing data

## Security Notes

- Keep database files secure - they contain sensitive customer data
- Backup files contain complete data - store them safely
- CSV/JSON exports contain customer information - handle with care
- Use file encryption for additional security if needed

## Troubleshooting

### PDF Issues
- If PDF doesn't download, check browser download settings
- For thermal print, ensure printer supports 80mm width
- Print PDF may be blocked by pop-up blockers

### Import Errors
- Check CSV/JSON format matches requirements
- Ensure all required fields are present
- Verify customer IDs exist before importing invoices
- Check for duplicate phone numbers or account numbers

### Database Issues
- If database is corrupted, restore from backup
- Ensure `.db` files are not opened by other programs
- Check file permissions if database won't open

## Support

For issues or questions:
1. Check this documentation first
2. Review error messages carefully
3. Test with a backup database
4. Contact support with specific error details
