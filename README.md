# JewelCalc

**JewelCalc** is a clean, modular Streamlit-based web application designed for jewelry shops to manage customer details, create invoices with multiple metal items, apply taxes and discounts, and generate professional PDF bills.

## Features

- **🎨 Clean Modern UI:** Intuitive tabbed interface with beautiful styling
- **👥 Customer Management:** Add, edit, search, and delete customer records with automatic account numbering
- **📝 Invoice Creation:** Create invoices with multiple items (metal type, weight, rate, wastage, making charges)
- **✏️ Invoice Editing:** Edit existing invoices, add/remove items, modify discounts
- **💰 Tax & Discount Support:** Built-in CGST and SGST calculation with discount options
- **📄 PDF Export:** Generate and download professional PDF invoices with direct download
- **🖨️ Print Support:** Print PDFs directly from browser with optimized layouts
- **🧾 Thermal Printing:** Special thermal printer format (80mm width) for receipt printers
- **📥📤 Import/Export:** Export customers (CSV) and invoices (JSON) for backup and transfer
- **🗄️ Database Management:** SQLite backend with easy switching, backup, and restore
- **⚙️ Configurable Settings:** Customize metal rates, wastage, and making charges
- **🔐 Local Storage:** All data stored locally on your PC/mobile, not in the cloud

## Project Structure

```
JewelCalc1/
├── app.py              # Main Streamlit application
├── database.py         # Database operations
├── utils.py            # Utility functions
├── pdf_generator.py    # PDF generation
├── requirements.txt    # Python dependencies
└── README.md          # Documentation
```

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/apkarthik1986/JewelCalc1.git
   cd JewelCalc1
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the app:**
   ```bash
   streamlit run app.py
   ```

## Requirements

- Python 3.8 or newer
- streamlit >= 1.25.0
- pandas
- reportlab
- sqlite3 (included in Python)

## Usage

1. **Settings Tab:** Configure metal rates, wastage percentages, making charges, and tax rates
2. **Customers Tab:** Add and manage customer information, import/export customer data
3. **Create Invoice Tab:** Select a customer, add items, and save invoices
4. **View Invoices Tab:** Browse, search, edit, and download invoice PDFs (regular/thermal print)

## New Features

See [FEATURES.md](FEATURES.md) for detailed documentation on:
- Direct PDF download and print functionality
- Thermal printer support
- Invoice editing
- Customer and invoice import/export
- Database backup and restore
- And more!

## Database

The application uses SQLite for data storage. Database files are stored in the project directory with a `.db` extension. You can switch between different databases using the sidebar.

## License

MIT License

---

**JewelCalc**  
Clean, reliable billing for jewelry shops.
