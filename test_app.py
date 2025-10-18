#!/usr/bin/env python
"""
Test script for JewelCalc authentication and database operations
"""

import os
import sys
from database import Database
from auth import hash_password, verify_password
from utils import generate_invoice_number, generate_account_number, validate_phone, calculate_item_totals

def cleanup_test_files():
    """Remove test database files"""
    test_files = ['test_jewelcalc.db', 'test_auth.db', 'jewelcalc_test.db']
    for f in test_files:
        if os.path.exists(f):
            os.remove(f)

def test_authentication():
    """Test authentication system"""
    print("Testing Authentication System...")
    
    # Create test database
    db = Database('test_auth.db')
    db.create_admin_if_not_exists()
    
    # Test 1: Admin user exists
    admin = db.get_user_by_username('admin')
    assert admin is not None, "Admin user should exist"
    assert admin['role'] == 'admin', "Admin role should be 'admin'"
    assert admin['status'] == 'approved', "Admin should be approved"
    print("✓ Admin user created successfully")
    
    # Test 2: Password hashing
    password = 'testpass123'
    hashed = hash_password(password)
    assert len(hashed) == 64, "Hash should be 64 characters"
    assert verify_password(password, hashed), "Password should verify"
    assert not verify_password('wrong', hashed), "Wrong password should fail"
    print("✓ Password hashing works correctly")
    
    # Test 3: User creation
    user_id = db.add_user('testuser', hash_password('test123'), 'Test User', 'test@test.com', '1234567890')
    assert user_id > 0, "User should be created"
    print(f"✓ User created with ID: {user_id}")
    
    # Test 4: Pending users
    pending = db.get_pending_users()
    assert len(pending) == 1, "Should have 1 pending user"
    print("✓ Pending users retrieved correctly")
    
    # Test 5: User approval
    db.approve_user(user_id, admin['id'])
    user = db.get_user_by_username('testuser')
    assert user['status'] == 'approved', "User should be approved"
    print("✓ User approval works correctly")
    
    # Test 6: Get all users
    all_users = db.get_all_users()
    assert len(all_users) >= 2, "Should have at least 2 users"
    print("✓ Get all users works correctly")
    
    print("✅ Authentication tests passed!\n")

def test_database_operations():
    """Test database operations"""
    print("Testing Database Operations...")
    
    db = Database('test_jewelcalc.db')
    
    # Test 1: Add customer
    customer_id = db.add_customer('CUS-00001', 'John Doe', '9876543210', '123 Main St')
    assert customer_id > 0, "Customer should be created"
    print(f"✓ Customer created with ID: {customer_id}")
    
    # Test 2: Get customers
    customers = db.get_customers()
    assert len(customers) == 1, "Should have 1 customer"
    print("✓ Get customers works correctly")
    
    # Test 3: Update customer
    db.update_customer(customer_id, 'CUS-00001', 'John Smith', '9876543210', '456 Oak Ave')
    customer = db.get_customer_by_id(customer_id)
    assert customer['name'] == 'John Smith', "Customer name should be updated"
    print("✓ Update customer works correctly")
    
    # Test 4: Create invoice
    items = [
        {
            'metal': 'Gold 24K',
            'weight': 10.5,
            'rate': 6500.0,
            'wastage_percent': 5.0,
            'making_percent': 10.0,
            'item_value': 68250.0,
            'wastage_amount': 3412.5,
            'making_amount': 6825.0,
            'line_total': 78487.5
        }
    ]
    invoice_no = db.save_invoice(customer_id, 'INV-00001', items, 1.5, 1.5, 0)
    assert invoice_no == 'INV-00001', "Invoice should be created"
    print(f"✓ Invoice created: {invoice_no}")
    
    # Test 5: Get invoices
    invoices = db.get_invoices()
    assert len(invoices) == 1, "Should have 1 invoice"
    print("✓ Get invoices works correctly")
    
    # Test 6: Get invoice by number
    invoice, items_df, cust = db.get_invoice_by_number('INV-00001')
    assert invoice is not None, "Invoice should exist"
    assert len(items_df) == 1, "Should have 1 item"
    print("✓ Get invoice by number works correctly")
    
    # Test 7: Export/Import customers
    csv_data = db.export_customers_csv()
    assert len(csv_data) > 0, "CSV export should have data"
    print("✓ Export customers to CSV works")
    
    # Test 8: Export/Import invoices
    json_data = db.export_invoices_json()
    assert len(json_data) > 0, "JSON export should have data"
    print("✓ Export invoices to JSON works")
    
    print("✅ Database operations tests passed!\n")

def test_utility_functions():
    """Test utility functions"""
    print("Testing Utility Functions...")
    
    # Test 1: Generate invoice number
    inv_no = generate_invoice_number()
    assert len(inv_no) == 11, "Invoice number should be 11 characters"
    assert '-' in inv_no, "Invoice number should contain hyphen"
    print(f"✓ Invoice number generated: {inv_no}")
    
    # Test 2: Generate account number
    acc_no = generate_account_number([])
    assert acc_no == 'CUS-00001', "First account should be CUS-00001"
    acc_no2 = generate_account_number(['CUS-00001', 'CUS-00002'])
    assert acc_no2 == 'CUS-00003', "Next account should be CUS-00003"
    print("✓ Account number generation works correctly")
    
    # Test 3: Validate phone
    assert validate_phone('9876543210'), "Valid phone should pass"
    assert not validate_phone('123'), "Short phone should fail"
    assert not validate_phone('abcdefghij'), "Non-digit phone should fail"
    print("✓ Phone validation works correctly")
    
    # Test 4: Calculate item totals
    totals = calculate_item_totals(10.0, 6500.0, 5.0, 10.0)
    assert totals['item_value'] == 65000.0, "Item value should be correct"
    assert totals['wastage_amount'] == 3250.0, "Wastage should be correct"
    assert totals['making_amount'] == 6500.0, "Making charge should be correct"
    assert totals['line_total'] == 74750.0, "Line total should be correct"
    print("✓ Item calculation works correctly")
    
    print("✅ Utility functions tests passed!\n")

def main():
    """Run all tests"""
    print("=" * 60)
    print("JewelCalc Test Suite")
    print("=" * 60)
    print()
    
    try:
        # Clean up any existing test files
        cleanup_test_files()
        
        # Run tests
        test_authentication()
        test_database_operations()
        test_utility_functions()
        
        print("=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Clean up test files
        cleanup_test_files()
        print("\nTest files cleaned up.")

if __name__ == '__main__':
    main()
