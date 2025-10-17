"""Database operations for JewelCalc"""
import sqlite3
import pandas as pd
from datetime import datetime
import json
import csv
from io import StringIO


class Database:
    """Handle all database operations"""
    
    def __init__(self, db_path="jewelcalc.db"):
        self.db_path = db_path
        self._init_database()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path, check_same_thread=False)
    
    def _init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Customers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_no TEXT UNIQUE,
                name TEXT NOT NULL,
                phone TEXT UNIQUE NOT NULL,
                address TEXT
            )
        ''')
        
        # Invoices table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_no TEXT UNIQUE NOT NULL,
                customer_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                subtotal REAL NOT NULL,
                cgst_percent REAL NOT NULL,
                sgst_percent REAL NOT NULL,
                cgst_amount REAL NOT NULL,
                sgst_amount REAL NOT NULL,
                discount_percent REAL DEFAULT 0,
                discount_amount REAL DEFAULT 0,
                total REAL NOT NULL,
                FOREIGN KEY(customer_id) REFERENCES customers(id)
            )
        ''')
        
        # Invoice items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoice_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id INTEGER NOT NULL,
                item_no INTEGER NOT NULL,
                metal TEXT NOT NULL,
                weight REAL NOT NULL,
                rate REAL NOT NULL,
                wastage_percent REAL NOT NULL,
                making_percent REAL NOT NULL,
                item_value REAL NOT NULL,
                wastage_amount REAL NOT NULL,
                making_amount REAL NOT NULL,
                line_total REAL NOT NULL,
                FOREIGN KEY(invoice_id) REFERENCES invoices(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # Customer operations
    def add_customer(self, account_no, name, phone, address=""):
        """Add a new customer"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO customers (account_no, name, phone, address) VALUES (?, ?, ?, ?)',
            (account_no, name, phone, address)
        )
        conn.commit()
        customer_id = cursor.lastrowid
        conn.close()
        return customer_id
    
    def get_customers(self):
        """Get all customers as DataFrame"""
        conn = self.get_connection()
        df = pd.read_sql_query(
            'SELECT id, account_no, name, phone, address FROM customers ORDER BY id DESC',
            conn
        )
        conn.close()
        return df
    
    def get_customer_by_id(self, customer_id):
        """Get customer by ID"""
        conn = self.get_connection()
        df = pd.read_sql_query(
            'SELECT * FROM customers WHERE id = ?',
            conn,
            params=(customer_id,)
        )
        conn.close()
        return df.iloc[0].to_dict() if not df.empty else None
    
    def update_customer(self, customer_id, account_no, name, phone, address=""):
        """Update customer details"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE customers SET account_no=?, name=?, phone=?, address=? WHERE id=?',
            (account_no, name, phone, address, customer_id)
        )
        conn.commit()
        conn.close()
    
    def delete_customer(self, customer_id):
        """Delete customer and related invoices"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get invoice IDs
        cursor.execute('SELECT id FROM invoices WHERE customer_id=?', (customer_id,))
        invoice_ids = [row[0] for row in cursor.fetchall()]
        
        # Delete invoice items
        for invoice_id in invoice_ids:
            cursor.execute('DELETE FROM invoice_items WHERE invoice_id=?', (invoice_id,))
        
        # Delete invoices
        cursor.execute('DELETE FROM invoices WHERE customer_id=?', (customer_id,))
        
        # Delete customer
        cursor.execute('DELETE FROM customers WHERE id=?', (customer_id,))
        
        conn.commit()
        conn.close()
    
    # Invoice operations
    def save_invoice(self, customer_id, invoice_no, items, cgst_percent, sgst_percent, discount_percent=0):
        """Save invoice with items"""
        if not items:
            raise ValueError("Invoice must have at least one item")
        
        # Calculate totals
        subtotal = sum(item['line_total'] for item in items)
        discount_amount = subtotal * (discount_percent / 100)
        taxable_amount = subtotal - discount_amount
        cgst_amount = taxable_amount * (cgst_percent / 100)
        sgst_amount = taxable_amount * (sgst_percent / 100)
        total = taxable_amount + cgst_amount + sgst_amount
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Insert invoice
        cursor.execute('''
            INSERT INTO invoices (
                invoice_no, customer_id, date, subtotal, cgst_percent, sgst_percent,
                cgst_amount, sgst_amount, discount_percent, discount_amount, total
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            invoice_no, customer_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            subtotal, cgst_percent, sgst_percent, cgst_amount, sgst_amount,
            discount_percent, discount_amount, total
        ))
        
        invoice_id = cursor.lastrowid
        
        # Insert invoice items
        for idx, item in enumerate(items, start=1):
            cursor.execute('''
                INSERT INTO invoice_items (
                    invoice_id, item_no, metal, weight, rate, wastage_percent,
                    making_percent, item_value, wastage_amount, making_amount, line_total
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                invoice_id, idx, item['metal'], item['weight'], item['rate'],
                item['wastage_percent'], item['making_percent'], item['item_value'],
                item['wastage_amount'], item['making_amount'], item['line_total']
            ))
        
        conn.commit()
        conn.close()
        return invoice_no
    
    def get_invoices(self):
        """Get all invoices as DataFrame"""
        conn = self.get_connection()
        df = pd.read_sql_query('''
            SELECT 
                i.id, i.invoice_no, i.date, i.total,
                c.name as customer_name, c.phone as customer_phone, c.account_no
            FROM invoices i
            LEFT JOIN customers c ON i.customer_id = c.id
            ORDER BY i.date DESC
        ''', conn)
        conn.close()
        return df
    
    def get_invoice_by_number(self, invoice_no):
        """Get invoice details by invoice number"""
        conn = self.get_connection()
        
        # Get invoice
        invoice_df = pd.read_sql_query(
            'SELECT * FROM invoices WHERE invoice_no = ?',
            conn,
            params=(invoice_no,)
        )
        
        if invoice_df.empty:
            conn.close()
            return None, None, None
        
        invoice = invoice_df.iloc[0].to_dict()
        
        # Get invoice items
        items_df = pd.read_sql_query(
            'SELECT * FROM invoice_items WHERE invoice_id = ? ORDER BY item_no',
            conn,
            params=(invoice['id'],)
        )
        
        # Get customer
        customer_df = pd.read_sql_query(
            'SELECT * FROM customers WHERE id = ?',
            conn,
            params=(invoice['customer_id'],)
        )
        
        customer = customer_df.iloc[0].to_dict() if not customer_df.empty else None
        
        conn.close()
        return invoice, items_df, customer
    
    def update_invoice(self, invoice_id, items, cgst_percent, sgst_percent, discount_percent=0):
        """Update an existing invoice"""
        if not items:
            raise ValueError("Invoice must have at least one item")
        
        # Calculate totals
        subtotal = sum(item['line_total'] for item in items)
        discount_amount = subtotal * (discount_percent / 100)
        taxable_amount = subtotal - discount_amount
        cgst_amount = taxable_amount * (cgst_percent / 100)
        sgst_amount = taxable_amount * (sgst_percent / 100)
        total = taxable_amount + cgst_amount + sgst_amount
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Update invoice
        cursor.execute('''
            UPDATE invoices SET
                subtotal=?, cgst_percent=?, sgst_percent=?,
                cgst_amount=?, sgst_amount=?, discount_percent=?, discount_amount=?, total=?
            WHERE id=?
        ''', (
            subtotal, cgst_percent, sgst_percent, cgst_amount, sgst_amount,
            discount_percent, discount_amount, total, invoice_id
        ))
        
        # Delete existing items
        cursor.execute('DELETE FROM invoice_items WHERE invoice_id=?', (invoice_id,))
        
        # Insert new items
        for idx, item in enumerate(items, start=1):
            cursor.execute('''
                INSERT INTO invoice_items (
                    invoice_id, item_no, metal, weight, rate, wastage_percent,
                    making_percent, item_value, wastage_amount, making_amount, line_total
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                invoice_id, idx, item['metal'], item['weight'], item['rate'],
                item['wastage_percent'], item['making_percent'], item['item_value'],
                item['wastage_amount'], item['making_amount'], item['line_total']
            ))
        
        conn.commit()
        conn.close()
    
    # Import/Export operations
    def export_customers_csv(self):
        """Export customers to CSV format"""
        conn = self.get_connection()
        df = pd.read_sql_query('SELECT * FROM customers', conn)
        conn.close()
        return df.to_csv(index=False)
    
    def import_customers_csv(self, csv_content):
        """Import customers from CSV content"""
        df = pd.read_csv(StringIO(csv_content))
        conn = self.get_connection()
        cursor = conn.cursor()
        
        imported = 0
        errors = []
        
        for _, row in df.iterrows():
            try:
                cursor.execute(
                    'INSERT INTO customers (account_no, name, phone, address) VALUES (?, ?, ?, ?)',
                    (row.get('account_no', ''), row.get('name', ''), 
                     row.get('phone', ''), row.get('address', ''))
                )
                imported += 1
            except sqlite3.IntegrityError as e:
                errors.append(f"Row {_ + 1}: {str(e)}")
        
        conn.commit()
        conn.close()
        return imported, errors
    
    def export_invoices_json(self):
        """Export all invoices with items to JSON format"""
        conn = self.get_connection()
        
        # Get all invoices
        invoices_df = pd.read_sql_query('SELECT * FROM invoices', conn)
        
        export_data = []
        for _, invoice_row in invoices_df.iterrows():
            invoice_dict = invoice_row.to_dict()
            
            # Get items for this invoice
            items_df = pd.read_sql_query(
                'SELECT * FROM invoice_items WHERE invoice_id = ?',
                conn,
                params=(invoice_dict['id'],)
            )
            invoice_dict['items'] = items_df.to_dict('records')
            
            # Get customer info
            customer_df = pd.read_sql_query(
                'SELECT * FROM customers WHERE id = ?',
                conn,
                params=(invoice_dict['customer_id'],)
            )
            if not customer_df.empty:
                invoice_dict['customer'] = customer_df.iloc[0].to_dict()
            
            export_data.append(invoice_dict)
        
        conn.close()
        return json.dumps(export_data, indent=2, default=str)
    
    def import_invoices_json(self, json_content):
        """Import invoices from JSON content"""
        data = json.loads(json_content)
        conn = self.get_connection()
        cursor = conn.cursor()
        
        imported = 0
        errors = []
        
        for idx, invoice_data in enumerate(data):
            try:
                # Check if customer exists
                customer_id = invoice_data.get('customer_id')
                cursor.execute('SELECT id FROM customers WHERE id = ?', (customer_id,))
                if not cursor.fetchone():
                    errors.append(f"Invoice {idx + 1}: Customer ID {customer_id} not found")
                    continue
                
                # Insert invoice
                cursor.execute('''
                    INSERT INTO invoices (
                        invoice_no, customer_id, date, subtotal, cgst_percent, sgst_percent,
                        cgst_amount, sgst_amount, discount_percent, discount_amount, total
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    invoice_data['invoice_no'], customer_id, invoice_data['date'],
                    invoice_data['subtotal'], invoice_data['cgst_percent'], 
                    invoice_data['sgst_percent'], invoice_data['cgst_amount'], 
                    invoice_data['sgst_amount'], invoice_data.get('discount_percent', 0),
                    invoice_data.get('discount_amount', 0), invoice_data['total']
                ))
                
                invoice_id = cursor.lastrowid
                
                # Insert items
                for item in invoice_data.get('items', []):
                    cursor.execute('''
                        INSERT INTO invoice_items (
                            invoice_id, item_no, metal, weight, rate, wastage_percent,
                            making_percent, item_value, wastage_amount, making_amount, line_total
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        invoice_id, item['item_no'], item['metal'], item['weight'],
                        item['rate'], item['wastage_percent'], item['making_percent'],
                        item['item_value'], item['wastage_amount'], item['making_amount'],
                        item['line_total']
                    ))
                
                imported += 1
            except Exception as e:
                errors.append(f"Invoice {idx + 1}: {str(e)}")
        
        conn.commit()
        conn.close()
        return imported, errors
    
    def export_database(self, target_path):
        """Export entire database to another file"""
        import shutil
        shutil.copy2(self.db_path, target_path)
        return True
    
    def import_database(self, source_path):
        """Import database from another file"""
        import shutil
        shutil.copy2(source_path, self.db_path)
        self._init_database()  # Ensure tables exist
        return True
