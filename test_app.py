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
    import glob
    # Find all test database files dynamically
    test_patterns = ['test_*.db', 'jewelcalc_test*.db']
    for pattern in test_patterns:
        for f in glob.glob(pattern):
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
    # PBKDF2 hash format: salt:hash (32 bytes each = 64 hex chars + colon + 64 hex chars = 129 chars)
    assert len(hashed) == 129, f"Hash should be 129 characters, got {len(hashed)}"
    assert ':' in hashed, "Hash should contain salt separator"
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
    
    # Test 7: Update user password
    new_hash = hash_password('newpass456')
    db.update_user_password(user_id, new_hash)
    user = db.get_user_by_username('testuser')
    assert verify_password('newpass456', user['password_hash']), "Password should be updated"
    print("✓ Update user password works correctly")
    
    # Test 7.5: Update user profile
    db.update_user_profile(user_id, email='updated@test.com', phone='5555555555')
    user = db.get_user_by_username('testuser')
    assert user['email'] == 'updated@test.com', "Email should be updated"
    assert user['phone'] == '5555555555', "Phone should be updated"
    print("✓ Update user profile works correctly")
    
    # Test 8: Add user with immediate approval (admin creation)
    admin_created_user_id = db.add_user_with_approval(
        'adminuser', 
        hash_password('admin123'), 
        'Admin Created User', 
        'admin@test.com', 
        '9876543210', 
        'user',
        admin['id']
    )
    assert admin_created_user_id > 0, "Admin-created user should be created"
    admin_user = db.get_user_by_username('adminuser')
    assert admin_user['status'] == 'approved', "Admin-created user should be approved"
    print(f"✓ Admin-created user with ID: {admin_created_user_id}")
    
    # Test 9: Password reset request
    reset_request_id = db.create_password_reset_request('testuser', 'test@test.com', '1234567890', 'password')
    assert reset_request_id is not None, "Password reset request should be created"
    print(f"✓ Password reset request created with ID: {reset_request_id}")
    
    # Test 10: Get pending password reset requests
    pending_resets = db.get_pending_password_reset_requests()
    assert len(pending_resets) == 1, "Should have 1 pending reset request"
    print("✓ Pending password reset requests retrieved correctly")
    
    # Test 11: Resolve password reset request
    new_pwd_hash = hash_password('resetpass789')
    result = db.resolve_password_reset_request(reset_request_id, admin['id'], new_pwd_hash)
    assert result, "Password reset should be resolved"
    user = db.get_user_by_username('testuser')
    assert verify_password('resetpass789', user['password_hash']), "Password should be reset"
    print("✓ Password reset resolution works correctly")
    
    # Test 12: Reject password reset request
    reset_request_id2 = db.create_password_reset_request('testuser', '', '', 'username')
    assert reset_request_id2 is not None, "Username request should be created"
    result = db.reject_password_reset_request(reset_request_id2)
    assert result, "Request rejection should work"
    print("✓ Password reset request rejection works correctly")
    
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
    # Test data for a typical gold invoice
    test_weight = 10.5  # grams
    test_rate = 6500.0  # per gram
    test_wastage_percent = 5.0
    test_making_percent = 10.0
    
    # Calculate expected values
    test_item_value = test_weight * test_rate  # 68250.0
    test_wastage_amount = test_item_value * (test_wastage_percent / 100)  # 3412.5
    test_making_amount = test_item_value * (test_making_percent / 100)  # 6825.0
    test_line_total = test_item_value + test_wastage_amount + test_making_amount  # 78487.5
    
    items = [
        {
            'metal': 'Gold 24K',
            'weight': test_weight,
            'rate': test_rate,
            'wastage_percent': test_wastage_percent,
            'making_percent': test_making_percent,
            'item_value': test_item_value,
            'wastage_amount': test_wastage_amount,
            'making_amount': test_making_amount,
            'line_total': test_line_total
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
    test_weight = 10.0  # grams
    test_rate = 6500.0  # per gram
    test_wastage_percent = 5.0
    test_making_percent = 10.0
    
    totals = calculate_item_totals(test_weight, test_rate, test_wastage_percent, test_making_percent)
    
    expected_item_value = 65000.0
    expected_wastage = 3250.0
    expected_making = 6500.0
    expected_total = 74750.0
    
    assert totals['item_value'] == expected_item_value, "Item value should be correct"
    assert totals['wastage_amount'] == expected_wastage, "Wastage should be correct"
    assert totals['making_amount'] == expected_making, "Making charge should be correct"
    assert totals['line_total'] == expected_total, "Line total should be correct"
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
