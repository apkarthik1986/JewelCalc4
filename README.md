# JewelCalc

**JewelCalc** is a Streamlit-based web application designed for jewelry shops to easily manage customer details, create and edit invoices with multiple metal items, apply taxes and discounts, and generate printable PDF bills—all in an intuitive, tabbed interface.

## Features

- **Tabbed Navigation:** Easy access to Base Settings, Customers, Invoice Entry, and Invoices.
- **Customer Management:** Add, edit, search, and delete customer records with account numbers and contact info.
- **Invoice Management:** Create new invoices, add multiple items per invoice (with metal type, weight, rate, wastage, making charges), apply discounts, and preview totals.
- **Tax Calculation:** Built-in CGST and SGST support, customizable rates.
- **PDF Export:** Generate and download professional PDF invoices for printing or emailing.
- **Database Management:** Switch between multiple SQLite database files for different shops or branches.
- **Sticky UI:** Fixed title and tab bar stay visible during scrolling for a smooth UX.

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/jewelcalc.git
   cd jewelcalc
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the app:**
   ```bash
   streamlit run jewelcalc.py
   ```

## Requirements

- Python 3.8 or newer
- See `requirements.txt` for Python package dependencies

## Usage

- Open the app in your browser at `http://localhost:8501/`
- Use the tabs at the top to set base values, manage customers, enter invoices, and view/export invoices.
- The sidebar helps with database management and navigation.

## Screenshots

*(Add your screenshots here!)*

## License

MIT License

---

**JewelCalc**  
Simple, reliable billing for jewellers.
