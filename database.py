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
        
        # Users table for authentication
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                role TEXT DEFAULT 'user',
                status TEXT DEFAULT 'pending',
                created_at TEXT NOT NULL,
                approved_at TEXT,
                approved_by INTEGER,
                FOREIGN KEY(approved_by) REFERENCES users(id)
            )
        ''')
        
        # Password reset requests table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS password_reset_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                request_type TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                requested_at TEXT NOT NULL,
                resolved_at TEXT,
                resolved_by INTEGER,
                FOREIGN KEY(user_id) REFERENCES users(id),
                FOREIGN KEY(resolved_by) REFERENCES users(id)
            )
        ''')
        
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
        
        # Settings table for persistent user settings
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL,
                updated_at TEXT NOT NULL
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
    
    # User operations
    def add_user(self, username, password_hash, full_name, email="", phone="", role="user"):
        """Add a new user (signup)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO users (username, password_hash, full_name, email, phone, role, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (username, password_hash, full_name, email, phone, role, 'pending', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id
    
    def get_user_by_username(self, username):
        """Get user by username"""
        conn = self.get_connection()
        df = pd.read_sql_query(
            'SELECT * FROM users WHERE username = ?',
            conn,
            params=(username,)
        )
        conn.close()
        return df.iloc[0].to_dict() if not df.empty else None
    
    def get_all_users(self):
        """Get all users"""
        conn = self.get_connection()
        df = pd.read_sql_query(
            'SELECT id, username, full_name, email, phone, role, status, created_at, approved_at FROM users ORDER BY created_at DESC',
            conn
        )
        conn.close()
        return df
    
    def get_pending_users(self):
        """Get users with pending approval"""
        conn = self.get_connection()
        df = pd.read_sql_query(
            'SELECT id, username, full_name, email, phone, created_at FROM users WHERE status = ? ORDER BY created_at DESC',
            conn,
            params=('pending',)
        )
        conn.close()
        return df
    
    def approve_user(self, user_id, admin_id):
        """Approve a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE users SET status=?, approved_at=?, approved_by=? WHERE id=?',
            ('approved', datetime.now().strftime("%Y-%m-%d %H:%M:%S"), admin_id, user_id)
        )
        conn.commit()
        conn.close()
    
    def reject_user(self, user_id):
        """Reject/delete a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE id=?', (user_id,))
        conn.commit()
        conn.close()
    
    def update_user_role(self, user_id, role):
        """Update user role"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE users SET role=? WHERE id=?',
            (role, user_id)
        )
        conn.commit()
        conn.close()
    
    def update_user_password(self, user_id, new_password_hash):
        """Update user password"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE users SET password_hash=? WHERE id=?',
            (new_password_hash, user_id)
        )
        conn.commit()
        conn.close()
    
    def update_user_profile(self, user_id, email=None, phone=None):
        """Update user profile (email and phone)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Build dynamic update query based on provided fields
        updates = []
        params = []
        
        if email is not None:
            updates.append('email=?')
            params.append(email)
        
        if phone is not None:
            updates.append('phone=?')
            params.append(phone)
        
        if updates:
            params.append(user_id)
            query = f'UPDATE users SET {", ".join(updates)} WHERE id=?'
            cursor.execute(query, params)
            conn.commit()
        
        conn.close()
    
    def add_user_with_approval(self, username, password_hash, full_name, email="", phone="", role="user", admin_id=None):
        """Add a new user with immediate approval (for admin creation)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            'INSERT INTO users (username, password_hash, full_name, email, phone, role, status, created_at, approved_at, approved_by) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (username, password_hash, full_name, email, phone, role, 'approved', now, now, admin_id)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id
    
    def create_password_reset_request(self, username="", email="", phone="", request_type="password"):
        """Create a password reset request - supports lookup by username, email, or phone"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Try to find user by username, email, or phone
        user = None
        if username:
            cursor.execute('SELECT id, username, email, phone FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()
        
        if not user and email:
            cursor.execute('SELECT id, username, email, phone FROM users WHERE email = ?', (email,))
            user = cursor.fetchone()
        
        if not user and phone:
            cursor.execute('SELECT id, username, email, phone FROM users WHERE phone = ?', (phone,))
            user = cursor.fetchone()
        
        if user is None:
            conn.close()
            return None
        
        user_id = user[0]
        username_found = user[1]
        user_email = user[2] or ""
        user_phone = user[3] or ""
        
        cursor.execute(
            'INSERT INTO password_reset_requests (user_id, username, email, phone, request_type, status, requested_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (user_id, username_found, email or user_email, phone or user_phone, request_type, 'pending', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()
        request_id = cursor.lastrowid
        conn.close()
        return request_id
    
    def get_pending_password_reset_requests(self):
        """Get all pending password reset requests"""
        conn = self.get_connection()
        df = pd.read_sql_query(
            'SELECT id, user_id, username, email, phone, request_type, requested_at FROM password_reset_requests WHERE status = ? ORDER BY requested_at DESC',
            conn,
            params=('pending',)
        )
        conn.close()
        return df
    
    def resolve_password_reset_request(self, request_id, admin_id, new_password_hash=None):
        """Resolve a password reset request and optionally set new password"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get request details
        cursor.execute('SELECT user_id FROM password_reset_requests WHERE id = ?', (request_id,))
        result = cursor.fetchone()
        
        if result is None:
            conn.close()
            return False
        
        user_id = result[0]
        
        # Update password if provided
        if new_password_hash:
            cursor.execute('UPDATE users SET password_hash=? WHERE id=?', (new_password_hash, user_id))
        
        # Mark request as resolved
        cursor.execute(
            'UPDATE password_reset_requests SET status=?, resolved_at=?, resolved_by=? WHERE id=?',
            ('resolved', datetime.now().strftime("%Y-%m-%d %H:%M:%S"), admin_id, request_id)
        )
        
        conn.commit()
        conn.close()
        return True
    
    def reject_password_reset_request(self, request_id):
        """Reject a password reset request"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE password_reset_requests SET status=?, resolved_at=? WHERE id=?',
            ('rejected', datetime.now().strftime("%Y-%m-%d %H:%M:%S"), request_id)
        )
        conn.commit()
        conn.close()
        return True
    
    def create_admin_if_not_exists(self):
        """Create default admin user if no admin exists"""
        import hashlib
        import os
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users WHERE role = ?', ('admin',))
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Default admin: username=admin, password=admin123
            # Use PBKDF2 for secure password hashing
            salt = os.urandom(32)
            pwd_hash = hashlib.pbkdf2_hmac('sha256', "admin123".encode('utf-8'), salt, 100000)
            password_hash = salt.hex() + ':' + pwd_hash.hex()
            
            cursor.execute(
                'INSERT INTO users (username, password_hash, full_name, email, phone, role, status, created_at, approved_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                ('admin', password_hash, 'Administrator', '', '', 'admin', 'approved', 
                 datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                 datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )
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
    
    def delete_invoice(self, invoice_id):
        """Delete an invoice and its items"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Delete invoice items first (foreign key constraint)
        cursor.execute('DELETE FROM invoice_items WHERE invoice_id=?', (invoice_id,))
        
        # Delete invoice
        cursor.execute('DELETE FROM invoices WHERE id=?', (invoice_id,))
        
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
    
    # Settings operations for persistent storage
    def save_setting(self, key, value):
        """Save a setting to the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Convert value to JSON string for storage
        value_json = json.dumps(value)
        cursor.execute(
            'INSERT OR REPLACE INTO settings (key, value, updated_at) VALUES (?, ?, ?)',
            (key, value_json, now)
        )
        conn.commit()
        conn.close()
    
    def get_setting(self, key, default=None):
        """Get a setting from the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        result = cursor.fetchone()
        conn.close()
        if result:
            # Parse JSON string back to original type
            return json.loads(result[0])
        return default
    
    def delete_setting(self, key):
        """Delete a setting from the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM settings WHERE key = ?', (key,))
        conn.commit()
        conn.close()
    
    # Reporting functions
    def get_sales_report(self, start_date=None, end_date=None):
        """Get sales report for a date range"""
        conn = self.get_connection()
        query = '''
            SELECT 
                i.date,
                i.invoice_no,
                c.name as customer_name,
                c.account_no,
                i.subtotal,
                i.discount_amount,
                i.cgst_amount,
                i.sgst_amount,
                i.total
            FROM invoices i
            JOIN customers c ON i.customer_id = c.id
        '''
        params = []
        if start_date and end_date:
            query += ' WHERE i.date >= ? AND i.date < ?'
            params = [start_date, end_date]
        elif start_date:
            query += ' WHERE i.date >= ?'
            params = [start_date]
        elif end_date:
            query += ' WHERE i.date < ?'
            params = [end_date]
        
        query += ' ORDER BY i.date DESC'
        
        df = pd.read_sql_query(query, conn, params=params if params else None)
        conn.close()
        return df
    
    def get_customer_purchase_analysis(self, customer_id=None):
        """Get customer-wise purchase analysis"""
        conn = self.get_connection()
        
        if customer_id:
            query = '''
                SELECT 
                    c.account_no,
                    c.name,
                    c.phone,
                    COUNT(i.id) as invoice_count,
                    SUM(i.subtotal) as total_subtotal,
                    SUM(i.discount_amount) as total_discount,
                    SUM(i.total) as total_amount,
                    MIN(i.date) as first_purchase,
                    MAX(i.date) as last_purchase
                FROM customers c
                LEFT JOIN invoices i ON c.id = i.customer_id
                WHERE c.id = ?
                GROUP BY c.id, c.account_no, c.name, c.phone
            '''
            params = (customer_id,)
        else:
            query = '''
                SELECT 
                    c.account_no,
                    c.name,
                    c.phone,
                    COUNT(i.id) as invoice_count,
                    SUM(i.subtotal) as total_subtotal,
                    SUM(i.discount_amount) as total_discount,
                    SUM(i.total) as total_amount,
                    MIN(i.date) as first_purchase,
                    MAX(i.date) as last_purchase
                FROM customers c
                LEFT JOIN invoices i ON c.id = i.customer_id
                GROUP BY c.id, c.account_no, c.name, c.phone
                ORDER BY total_amount DESC
            '''
            params = None
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    
    def get_category_report(self):
        """Get category (metal type) wise report"""
        conn = self.get_connection()
        query = '''
            SELECT 
                ii.metal,
                COUNT(DISTINCT ii.invoice_id) as invoice_count,
                SUM(ii.weight) as total_weight,
                AVG(ii.rate) as avg_rate,
                SUM(ii.item_value) as total_item_value,
                SUM(ii.wastage_amount) as total_wastage,
                SUM(ii.making_amount) as total_making,
                SUM(ii.line_total) as total_amount
            FROM invoice_items ii
            GROUP BY ii.metal
            ORDER BY total_amount DESC
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def duplicate_invoice(self, invoice_id, new_invoice_no):
        """Duplicate an existing invoice with a new invoice number"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Get original invoice
            cursor.execute('SELECT * FROM invoices WHERE id = ?', (invoice_id,))
            invoice = cursor.fetchone()
            
            if not invoice:
                conn.close()
                return None
            
            # Get invoice items
            cursor.execute('SELECT * FROM invoice_items WHERE invoice_id = ?', (invoice_id,))
            items = cursor.fetchall()
            
            # Insert new invoice with today's date
            today = datetime.now().strftime("%Y-%m-%d")
            cursor.execute('''
                INSERT INTO invoices 
                (invoice_no, customer_id, date, subtotal, cgst_percent, sgst_percent, 
                 cgst_amount, sgst_amount, discount_percent, discount_amount, total)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                new_invoice_no,
                invoice[2],  # customer_id (index 2)
                today,       # new date
                invoice[4],  # subtotal (index 4)
                invoice[5],  # cgst_percent (index 5)
                invoice[6],  # sgst_percent (index 6)
                invoice[7],  # cgst_amount (index 7)
                invoice[8],  # sgst_amount (index 8)
                invoice[9],  # discount_percent (index 9)
                invoice[10], # discount_amount (index 10)
                invoice[11]  # total (index 11)
            ))
            
            new_invoice_id = cursor.lastrowid
            
            # Copy all items to new invoice
            # invoice_items schema: id, invoice_id, item_no, metal, weight, rate, 
            #                       wastage_percent, making_percent, item_value, 
            #                       wastage_amount, making_amount, line_total
            for item in items:
                cursor.execute('''
                    INSERT INTO invoice_items 
                    (invoice_id, item_no, metal, weight, rate, wastage_percent, 
                     making_percent, item_value, wastage_amount, making_amount, line_total)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    new_invoice_id,
                    item[2],   # item_no (index 2)
                    item[3],   # metal (index 3)
                    item[4],   # weight (index 4)
                    item[5],   # rate (index 5)
                    item[6],   # wastage_percent (index 6)
                    item[7],   # making_percent (index 7)
                    item[8],   # item_value (index 8)
                    item[9],   # wastage_amount (index 9)
                    item[10],  # making_amount (index 10)
                    item[11]   # line_total (index 11)
                ))
            
            conn.commit()
            conn.close()
            return new_invoice_id
            
        except Exception as e:
            conn.rollback()
            conn.close()
            raise e
