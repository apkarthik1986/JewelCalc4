#!/usr/bin/env python
"""
Test script for admin cross-database viewing functionality
"""

import os
import sys
from database import Database
from auth import hash_password

def cleanup_test_files():
    """Remove test database files"""
    import glob
    test_patterns = ['test_*.db', 'jewelcalc_test*.db', 'jewelcalc_user_*.db', 'jewelcalc_admin.db', 'jewelcalc_auth.db']
    for pattern in test_patterns:
        for f in glob.glob(pattern):
            if os.path.exists(f):
                os.remove(f)

def test_admin_cross_database_views():
    """Test that admin can view data from multiple user databases"""
    print("Testing Admin Cross-Database Views...")
    
    # Create auth database with admin and users
    auth_db = Database('jewelcalc_auth.db')
    auth_db.create_admin_if_not_exists()
    
    # Create test users
    user1_id = auth_db.add_user('user1', hash_password('pass1'), 'User One', 'user1@test.com', '1111111111')
    user2_id = auth_db.add_user('user2', hash_password('pass2'), 'User Two', 'user2@test.com', '2222222222')
    
    # Approve users
    admin = auth_db.get_user_by_username('admin')
    auth_db.approve_user(user1_id, admin['id'])
    auth_db.approve_user(user2_id, admin['id'])
    
    print(f"✓ Created users: user1 (ID: {user1_id}), user2 (ID: {user2_id})")
    
    # Create user1's database and add data
    user1_db = Database(f'jewelcalc_user_{user1_id}.db')
    user1_db.add_customer('CUS-001', 'Customer One', '9999999999', 'Address 1')
    user1_db.add_customer('CUS-002', 'Customer Two', '8888888888', 'Address 2')
    print(f"✓ Added 2 customers to user1's database")
    
    # Create user2's database and add data
    user2_db = Database(f'jewelcalc_user_{user2_id}.db')
    user2_db.add_customer('CUS-003', 'Customer Three', '7777777777', 'Address 3')
    print(f"✓ Added 1 customer to user2's database")
    
    # Create admin's database and add data (will be deprioritized for duplicate phone)
    admin_db = Database('jewelcalc_admin.db')
    admin_db.add_customer('CUS-ADM', 'Admin Customer', '6666666666', 'Admin Address')
    admin_db.add_customer('CUS-DUP', 'Duplicate User', '9999999999', 'Will be hidden')  # Duplicate phone
    print(f"✓ Added 2 customers to admin's database (one duplicate)")
    
    # Test admin view of all customers
    all_customers = admin_db.get_all_customers_admin()
    print(f"\n✓ Admin view retrieved {len(all_customers)} customers total")
    
    # Verify we have 4 unique customers (duplicate excluded)
    assert len(all_customers) == 4, f"Expected 4 customers, got {len(all_customers)}"
    print("✓ Correctly excluded duplicate customer (user data takes priority)")
    
    # Verify database column exists
    assert 'database' in all_customers.columns, "Missing 'database' column"
    print("✓ Database source column present")
    
    # Count by database
    db_counts = all_customers['database'].value_counts()
    print(f"\nCustomer distribution:")
    for db_name, count in db_counts.items():
        print(f"  - {db_name}: {count} customers")
    
    # Add invoices to test invoice viewing
    cust1_id = user1_db.get_customers().iloc[0]['id']
    items1 = [{
        'metal': 'Gold 24K',
        'weight': 10.0,
        'rate': 6500.0,
        'wastage_percent': 5.0,
        'making_percent': 10.0,
        'item_value': 65000.0,
        'wastage_amount': 3250.0,
        'making_amount': 6500.0,
        'line_total': 74750.0
    }]
    user1_db.save_invoice(cust1_id, 'INV-USER1-001', items1, 1.5, 1.5, 0)
    print(f"\n✓ Added invoice to user1's database")
    
    cust2_id = user2_db.get_customers().iloc[0]['id']
    items2 = [{
        'metal': 'Silver',
        'weight': 50.0,
        'rate': 75.0,
        'wastage_percent': 3.0,
        'making_percent': 8.0,
        'item_value': 3750.0,
        'wastage_amount': 112.5,
        'making_amount': 300.0,
        'line_total': 4162.5
    }]
    user2_db.save_invoice(cust2_id, 'INV-USER2-001', items2, 1.5, 1.5, 0)
    print(f"✓ Added invoice to user2's database")
    
    # Test admin view of all invoices
    all_invoices = admin_db.get_all_invoices_admin()
    print(f"\n✓ Admin view retrieved {len(all_invoices)} invoices total")
    
    assert len(all_invoices) == 2, f"Expected 2 invoices, got {len(all_invoices)}"
    print("✓ All invoices retrieved correctly")
    
    # Verify database column exists
    assert 'database' in all_invoices.columns, "Missing 'database' column in invoices"
    print("✓ Database source column present in invoices")
    
    # Count by database
    inv_counts = all_invoices['database'].value_counts()
    print(f"\nInvoice distribution:")
    for db_name, count in inv_counts.items():
        print(f"  - {db_name}: {count} invoices")
    
    print("\n✅ Admin cross-database views test passed!\n")

def main():
    """Run all tests"""
    print("=" * 60)
    print("Admin Cross-Database Views Test Suite")
    print("=" * 60)
    print()
    
    try:
        # Clean up any existing test files
        cleanup_test_files()
        
        # Run tests
        test_admin_cross_database_views()
        
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
