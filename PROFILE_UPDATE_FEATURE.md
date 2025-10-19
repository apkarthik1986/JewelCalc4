# User Profile Update Feature

## Overview
This feature allows users and admins to update their profile information (email and phone number) after logging in.

## How to Use

### Accessing Profile Settings
1. Log in to your account
2. Look for the sidebar menu on the left
3. Click on the **"⚙️ Profile Settings"** expander

### Updating Your Profile
1. In the Profile Settings expander, you'll see the **"Update Profile"** section
2. The form will show your current email and phone number
3. Update either or both fields:
   - **Email**: Enter your new email address (can be left empty)
   - **Phone Number**: Must be exactly 10 digits (e.g., 9876543210)
4. Click the **"Update Profile"** button
5. You'll see a success message: "✅ Profile updated successfully!"
6. The page will refresh automatically to show your updated information

### Phone Number Validation
- Phone numbers must be exactly **10 digits**
- Only numeric characters are allowed
- Invalid phone numbers will show an error: "Phone must be exactly 10 digits"

### Changing Your Password
The password change functionality remains in the same Profile Settings section:
1. Enter your current password
2. Enter your new password
3. Confirm your new password
4. Click "Update Password"

## Technical Details

### Database Changes
- Added `update_user_profile()` method in `database.py`
- Supports updating email and phone fields individually or together
- Uses parameterized queries to prevent SQL injection

### UI Implementation
- Profile update form added to the sidebar in `auth.py`
- Form pre-populates with current user information
- Validates phone number format before submission
- Provides clear error messages for invalid input

### Security
- No security vulnerabilities detected
- Input validation ensures data integrity
- Uses existing authentication checks

## Permissions
- **All Users**: Can update their own profile (email and phone)
- **Admins**: Can update their own profile (email and phone)
- **Note**: Users cannot update other users' profiles; only admins can do this through the Admin Panel

## Testing
The feature has been thoroughly tested:
- Profile update with both fields
- Profile update with only email
- Profile update with only phone
- Phone number validation
- Empty field handling
- All existing tests continue to pass

## Examples

### Valid Phone Numbers
- `9876543210` ✅
- `1234567890` ✅
- `5555555555` ✅

### Invalid Phone Numbers
- `123` ❌ (too short)
- `12345678901` ❌ (too long)
- `abcdefghij` ❌ (not numeric)
- `123-456-7890` ❌ (contains special characters)

## Support
If you encounter any issues with the profile update feature, please contact your system administrator.
