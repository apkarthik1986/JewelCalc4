# JewelCalc2 - Professional Multi-User Enhancement

## Summary of Changes

This update transforms JewelCalc from a simple single-user jewelry billing app into a professional, secure, multi-user system with comprehensive features suitable for jewelry shops of all sizes.

## Key Features Added

### 1. User Authentication System
- **Secure Signup/Login**: Users can register and login with username/password
- **Password Security**: PBKDF2-HMAC-SHA256 with 100,000 iterations and random salt
- **Admin Approval Workflow**: New users require admin approval before accessing the system
- **Role-Based Access**: Two roles - Admin and User with different permissions

### 2. Multi-User Architecture
- **Separate Databases**: Each user gets their own isolated database
- **Central Auth Database**: Single authentication database manages all users
- **Admin Database**: Admins have their own dedicated database
- **Data Isolation**: Users can only access their own data

### 3. Admin Panel (Admin Only)
- **User Management**: Approve/reject pending user registrations
- **Role Assignment**: Change user roles (promote to admin or demote to user)
- **System Overview**: View statistics across all user databases
- **Database Monitoring**: See customer count, invoice count, and revenue per user

### 4. Database Management Tab
- **Backup & Restore**: Create and restore database backups
- **Export/Import Customers**: CSV format for easy data migration
- **Export/Import Invoices**: JSON format with complete invoice data
- **Download Backups**: Download database files to local storage

### 5. Enhanced UI/UX
- **Professional Design**: Gradient headers, smooth animations, modern colors
- **Mobile Responsive**: Optimized for phones and tablets
- **Better Forms**: Improved input fields with focus effects
- **Enhanced Tabs**: Professional tab styling with gradient highlights
- **Loading States**: Better visual feedback for user actions

### 6. Print Improvements
- **Printer Selection**: JavaScript-based print dialog with printer selection
- **Thermal Print Support**: Optimized format for 80mm thermal printers
- **Standard PDF Print**: Professional A4 format invoices

## Security Improvements

### Password Security
- **Strong Hashing**: PBKDF2-HMAC-SHA256 with 100,000 iterations
- **Random Salts**: Each password gets unique salt
- **Secure Storage**: Only hashed passwords stored, never plain text
- **Backward Compatible**: Legacy SHA256 hashes supported during migration

### Data Security
- **Session-Based Auth**: Secure session management
- **Database Isolation**: User data completely separated
- **Input Validation**: All inputs validated before database operations
- **SQL Injection Protection**: Parameterized queries throughout

## Architecture

```
JewelCalc2/
├── jewelcalc_auth.db          # Central authentication database
├── jewelcalc_admin.db         # Admin user database
├── jewelcalc_user_2.db        # User ID 2 database
├── jewelcalc_user_3.db        # User ID 3 database
└── ...
```

## User Flows

### New User Registration
1. User visits the app
2. Clicks "Sign Up" tab
3. Fills in registration form
4. Submits registration
5. Waits for admin approval
6. Admin reviews in Admin Panel
7. Admin approves user
8. User can now login

### Admin Management
1. Admin logs in
2. Goes to Admin tab
3. Sees pending approvals
4. Reviews user details
5. Approves or rejects
6. Can change roles later
7. Monitors system usage

### Daily Operations
1. User logs in
2. Manages customers
3. Creates invoices
4. Views/prints invoices
5. Exports data in Database tab
6. Logs out when done

## Migration Guide

### For Existing Users
If you have an existing JewelCalc installation:

1. **Backup your data**: Export customers and invoices
2. **Update the code**: Pull latest changes
3. **Install dependencies**: Run `pip install -r requirements.txt`
4. **First run**: Default admin account created (admin/admin123)
5. **Change password**: Login as admin and change password immediately
6. **Create users**: Add user accounts or let users sign up
7. **Import data**: Import your backed-up data

### For New Installations
1. Clone repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run app: `streamlit run app.py`
4. Login as admin (admin/admin123)
5. **IMPORTANT**: Change admin password immediately
6. Create user accounts or enable signups

## Testing

A comprehensive test suite is included:
```bash
python test_app.py
```

Tests cover:
- Authentication system
- Database operations
- Utility functions
- Password hashing
- User management

## Best Practices

### For Administrators
1. **Change default password**: First action after installation
2. **Review signups carefully**: Verify user legitimacy before approval
3. **Regular backups**: Create database backups regularly
4. **Monitor usage**: Check admin panel for system statistics
5. **Secure the server**: Use HTTPS in production environments

### For Users
1. **Strong passwords**: Use complex passwords with mix of characters
2. **Regular exports**: Export your data periodically
3. **Backup before changes**: Create backup before major operations
4. **Keep data current**: Update metal rates regularly
5. **Secure your credentials**: Don't share passwords

## Configuration

### Default Settings
- Metal rates: Gold 24K, 22K, 18K, Silver
- Tax rates: CGST 1.5%, SGST 1.5%
- Admin credentials: admin/admin123 (change immediately)

### Customization
- Metal rates: Settings tab
- Tax rates: Settings tab
- User roles: Admin panel
- Database location: Automatic per user

## Troubleshooting

### Cannot Login
- Check username/password
- Verify account is approved (contact admin)
- Clear browser cache and retry

### No Admin Tab
- Admin tab only visible to admin role
- Login as admin or ask current admin to promote you

### Database Issues
- Use Database tab to backup/restore
- Check file permissions
- Verify disk space

### Print Issues
- Allow pop-ups in browser
- Check printer is connected
- Try different browser if issues persist

## Performance

### Scalability
- Supports multiple concurrent users
- Each user has isolated database
- Efficient SQLite operations
- Optimized queries with indexes

### Resource Usage
- Minimal memory footprint
- Fast database operations
- Responsive UI even on mobile
- Efficient PDF generation

## Future Enhancements

Potential areas for future development:
- Email notifications for approvals
- Password reset via email
- Two-factor authentication
- Cloud backup integration
- Multi-language support
- Advanced reporting
- Inventory management

## Support

For issues or questions:
1. Check the README.md
2. Review this document
3. Run test suite to verify installation
4. Check GitHub issues
5. Contact developer

## License

MIT License - See LICENSE file for details

---

**Version**: 2.0.0  
**Release Date**: 2025-10-18  
**Developer**: apkarthik1986  
**Repository**: https://github.com/apkarthik1986/JewelCalc2
