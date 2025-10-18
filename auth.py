"""Authentication module for JewelCalc"""
import hashlib
import os
import streamlit as st


def hash_password(password):
    """Hash password using PBKDF2-SHA256 (secure for passwords)"""
    # Generate a random salt
    salt = os.urandom(32)
    # Use PBKDF2 with 100,000 iterations for strong password hashing
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    # Store salt and hash together
    return salt.hex() + ':' + pwd_hash.hex()


def verify_password(password, password_hash):
    """Verify password against hash"""
    try:
        # Split salt and hash
        salt_hex, hash_hex = password_hash.split(':')
        salt = bytes.fromhex(salt_hex)
        stored_hash = bytes.fromhex(hash_hex)
        # Hash the provided password with the stored salt
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        # Compare hashes
        return pwd_hash == stored_hash
    except (ValueError, AttributeError):
        # Backward compatibility for legacy SHA256 hashes (insecure, deprecated)
        # This is only for supporting old password hashes during migration
        # TODO: Remove this after all users have migrated to PBKDF2
        if len(password_hash) == 64:
            # Legacy SHA256 verification (not recommended for new passwords)
            return hashlib.sha256(password.encode()).hexdigest() == password_hash
        return False


def show_login_page(db):
    """Display login page"""
    st.markdown('<div class="main-header"><h1>💎 JewelCalc - Login</h1></div>', unsafe_allow_html=True)
    
    # Create tabs for login and signup
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
    
    with tab1:
        st.markdown("### Login to Your Account")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                if not username or not password:
                    st.error("Please enter both username and password")
                else:
                    user = db.get_user_by_username(username)
                    
                    if user is None:
                        st.error("❌ Invalid username or password")
                    elif user['status'] == 'pending':
                        st.warning("⏳ Your account is pending approval by an administrator")
                    elif user['status'] != 'approved':
                        st.error("❌ Your account has been deactivated")
                    elif not verify_password(password, user['password_hash']):
                        st.error("❌ Invalid username or password")
                    else:
                        # Login successful
                        st.session_state.logged_in = True
                        st.session_state.user_id = user['id']
                        st.session_state.username = user['username']
                        st.session_state.user_role = user['role']
                        st.session_state.user_full_name = user['full_name']
                        
                        # Set user-specific database path
                        if user['role'] == 'admin':
                            st.session_state.db_path = 'jewelcalc_admin.db'
                        else:
                            st.session_state.db_path = f'jewelcalc_user_{user["id"]}.db'
                        
                        st.success(f"✅ Welcome back, {user['full_name']}!")
                        st.rerun()
    
    with tab2:
        st.markdown("### Create New Account")
        st.info("📝 After signing up, an administrator will need to approve your account before you can login.")
        
        with st.form("signup_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_username = st.text_input("Username *", help="Choose a unique username")
                new_full_name = st.text_input("Full Name *")
            with col2:
                new_email = st.text_input("Email")
                new_phone = st.text_input("Phone Number")
            
            new_password = st.text_input("Password *", type="password", help="Choose a strong password")
            confirm_password = st.text_input("Confirm Password *", type="password")
            
            signup_submit = st.form_submit_button("Sign Up", use_container_width=True)
            
            if signup_submit:
                if not new_username or not new_full_name or not new_password:
                    st.error("Please fill in all required fields (*)")
                elif new_password != confirm_password:
                    st.error("Passwords do not match")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters long")
                else:
                    try:
                        # Check if username already exists
                        existing_user = db.get_user_by_username(new_username)
                        if existing_user:
                            st.error("❌ Username already exists. Please choose a different username.")
                        else:
                            # Create new user
                            password_hash = hash_password(new_password)
                            db.add_user(new_username, password_hash, new_full_name, new_email, new_phone)
                            st.success("✅ Account created successfully! Please wait for admin approval to login.")
                            st.info("💡 An administrator will review your request. You'll be notified once your account is approved.")
                    except Exception as e:
                        st.error(f"Error creating account: {str(e)}")


def show_user_menu():
    """Display user menu in sidebar"""
    with st.sidebar:
        st.markdown("---")
        st.markdown(f"### 👤 {st.session_state.user_full_name}")
        st.info(f"**Role:** {st.session_state.user_role.title()}")
        
        if st.button("🚪 Logout", use_container_width=True):
            # Clear session state
            for key in ['logged_in', 'user_id', 'username', 'user_role', 'user_full_name']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()


def require_auth(db):
    """Decorator to require authentication"""
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        show_login_page(db)
        return False
    return True


def require_admin():
    """Check if current user is admin"""
    return st.session_state.get('user_role') == 'admin'
