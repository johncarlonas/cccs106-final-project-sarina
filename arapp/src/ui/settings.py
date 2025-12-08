import flet as ft
import sys
import os
import re

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from database.db import update_user_password

def SettingsView(page: ft.Page):
    # Get current user email from session/storage
    user_email = page.session.get("user_email") or page.client_storage.get("logged_in_user")
    
    # Get user data from database
    from database.db import supabase
    user_data = {"name": "Guest", "role": "Unknown"}
    
    if user_email:
        try:
            response = supabase.table("users").select("*").eq("email", user_email).execute()
            if response.data and len(response.data) > 0:
                user_data = response.data[0]
        except Exception as e:
            print(f"Error fetching user data: {e}")
    
    # References for change password fields
    new_password = ft.Ref[ft.TextField]()
    retype_password = ft.Ref[ft.TextField]()
    
    def show_logout_confirmation(e):
        """Show confirmation dialog for logout"""
        def close_dlg(e):
            dialog.open = False
            page.update()
        
        def confirm_logout(e):
            dialog.open = False
            page.update()
            
            # Clear session and storage
            page.client_storage.remove("logged_in_user")
            page.session.clear()
            
            # Navigate to login/signup
            page.go("/login_signup")
        
        dialog = ft.AlertDialog(
            modal=True,
            bgcolor="white",
            title=ft.Text("Confirm Logout", color="black"),
            content=ft.Text("Are you sure you want to log out?", color="black"),
            actions=[
                ft.TextButton("Cancel", style=ft.ButtonStyle(color="#002A7A"), on_click=close_dlg),
                ft.TextButton("Yes", style=ft.ButtonStyle(color="#002A7A"), on_click=confirm_logout),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
    
    def show_change_password_dialog(e):
        """Show change password dialog with current password verification"""
        # Password rules refs
        rule_length = ft.Text(
            "• Minimum 8 characters",
            color="red",
            size=12
        )
        rule_uppercase = ft.Text(
            "• At least 1 uppercase letter",
            color="red",
            size=12
        )
        rule_special = ft.Text(
            "• At least 1 special character (!@#$%^&*)",
            color="red",
            size=12
        )
        
        def check_password_rules(password):
            """Check password against all rules"""
            has_length = len(password) >= 8
            has_uppercase = bool(re.search(r'[A-Z]', password))
            has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
            
            return {
                'length': has_length,
                'uppercase': has_uppercase,
                'special': has_special,
                'all_valid': has_length and has_uppercase and has_special
            }
        
        def on_password_change(e):
            """Update password rules display"""
            password = new_password_field.value
            rules = check_password_rules(password)
            
            rule_length.color = "#00AA00" if rules['length'] else "red"
            rule_uppercase.color = "#00AA00" if rules['uppercase'] else "red"
            rule_special.color = "#00AA00" if rules['special'] else "red"
            
            page.update()
        
        current_password_field = ft.TextField(
            label="Current Password",
            password=True,
            can_reveal_password=True,
            border_color="#002A7A",
            label_style=ft.TextStyle(color="black"),
            text_style=ft.TextStyle(color="black"),
        )
        
        new_password_field = ft.TextField(
            ref=new_password,
            label="New Password",
            password=True,
            can_reveal_password=True,
            border_color="#002A7A",
            label_style=ft.TextStyle(color="black"),
            text_style=ft.TextStyle(color="black"),
            on_change=on_password_change
        )
        
        confirm_password_field = ft.TextField(
            ref=retype_password,
            label="Confirm Password",
            password=True,
            can_reveal_password=True,
            border_color="#002A7A",
            label_style=ft.TextStyle(color="black"),
            text_style=ft.TextStyle(color="black"),
        )
        
        def validate_and_change_password(e):
            from utils.password_hashing import PasswordHasher
            
            # Clear previous errors
            current_password_field.error_text = None
            new_password_field.error_text = None
            confirm_password_field.error_text = None
            
            is_valid = True
            
            # Validate current password
            if not current_password_field.value:
                current_password_field.error_text = "This field is required"
                is_valid = False
            else:
                # Verify current password is correct
                try:
                    response = supabase.table("users").select("password").eq("email", user_email).execute()
                    if response.data and len(response.data) > 0:
                        stored_password = response.data[0]["password"]
                        if not PasswordHasher.verify_password(current_password_field.value, stored_password):
                            current_password_field.error_text = "Current password is incorrect"
                            is_valid = False
                    else:
                        current_password_field.error_text = "User not found"
                        is_valid = False
                except Exception as ex:
                    current_password_field.error_text = "Error verifying password"
                    is_valid = False
            
            # Validate new password
            if not new_password_field.value:
                new_password_field.error_text = "This field is required"
                is_valid = False
            else:
                # Check password rules
                rules = check_password_rules(new_password_field.value)
                if not rules['all_valid']:
                    new_password_field.error_text = "Password must meet all requirements"
                    is_valid = False
            
            # Validate confirm password
            if not confirm_password_field.value:
                confirm_password_field.error_text = "This field is required"
                is_valid = False
            elif new_password_field.value and confirm_password_field.value != new_password_field.value:
                confirm_password_field.error_text = "Passwords do not match"
                is_valid = False
            
            page.update()
            
            if is_valid:
                # Update password in database
                if update_user_password(user_email, new_password_field.value):
                    password_dialog.open = False
                    page.update()
                    
                    # Show success message
                    success_dialog = ft.AlertDialog(
                        modal=True,
                        bgcolor="white",
                        title=ft.Text("Success", color="black"),
                        content=ft.Text("Password has been updated successfully!", color="black"),
                        actions=[
                            ft.TextButton("OK", style=ft.ButtonStyle(color="#002A7A"), on_click=lambda e: close_success_dialog(success_dialog))
                        ],
                    )
                    page.overlay.append(success_dialog)
                    success_dialog.open = True
                    page.update()
                else:
                    new_password_field.error_text = "Failed to update password"
                    page.update()
        
        def close_success_dialog(dialog):
            dialog.open = False
            page.update()
        
        def close_password_dialog(e):
            password_dialog.open = False
            page.update()
        
        password_dialog = ft.AlertDialog(
            modal=True,
            bgcolor="white",
            title=ft.Text("Change Password", color="black"),
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        current_password_field,
                        new_password_field,
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    rule_length,
                                    rule_uppercase,
                                    rule_special,
                                ],
                                spacing=5
                            ),
                            padding=ft.padding.only(left=10, top=5, bottom=10)
                        ),
                        confirm_password_field,
                    ],
                    tight=True,
                    spacing=10
                ),
                width=400,
                padding=20
            ),
            actions=[
                ft.TextButton("Cancel", style=ft.ButtonStyle(color="#002A7A"), on_click=close_password_dialog),
                ft.TextButton("Confirm", style=ft.ButtonStyle(color="#002A7A"), on_click=validate_and_change_password),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.overlay.append(password_dialog)
        password_dialog.open = True
        page.update()
    
    def show_edit_profile_dialog(e):
        """Show edit profile dialog"""
        full_name_field = ft.TextField(
            label="Full Name",
            value=user_data.get("name", ""),
            border_color="#002A7A",
            label_style=ft.TextStyle(color="black"),
            text_style=ft.TextStyle(color="black"),
        )
        
        email_field = ft.TextField(
            label="Email",
            value=user_email,
            border_color="#002A7A",
            label_style=ft.TextStyle(color="black"),
            text_style=ft.TextStyle(color="black"),
            read_only=True,
            disabled=True,
        )
        
        def validate_and_update_profile(e):
            # Clear previous errors
            full_name_field.error_text = None
            
            is_valid = True
            
            # Validate full name
            if not full_name_field.value or not full_name_field.value.strip():
                full_name_field.error_text = "Full name cannot be blank"
                is_valid = False
            
            page.update()
            
            if is_valid:
                # Update profile in database
                try:
                    supabase.table("users").update({
                        "name": full_name_field.value.strip()
                    }).eq("email", user_email).execute()
                    
                    # Update local user_data
                    user_data["name"] = full_name_field.value.strip()
                    
                    profile_dialog.open = False
                    page.update()
                    
                    # Show success message
                    success_dialog = ft.AlertDialog(
                        modal=True,
                        bgcolor="white",
                        title=ft.Text("Success", color="black"),
                        content=ft.Text("Profile has been updated successfully!", color="black"),
                        actions=[
                            ft.TextButton("OK", style=ft.ButtonStyle(color="#002A7A"), on_click=lambda e: close_success_dialog(success_dialog))
                        ],
                    )
                    page.overlay.append(success_dialog)
                    success_dialog.open = True
                    page.update()
                except Exception as ex:
                    full_name_field.error_text = f"Failed to update profile: {str(ex)}"
                    page.update()
        
        def close_success_dialog(dialog):
            dialog.open = False
            page.update()
            # Refresh the page to show updated name
            page.go("/settings")
        
        def close_profile_dialog(e):
            profile_dialog.open = False
            page.update()
        
        profile_dialog = ft.AlertDialog(
            modal=True,
            bgcolor="white",
            title=ft.Text("Edit Profile", color="black"),
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        full_name_field,
                        email_field,
                    ],
                    tight=True,
                    spacing=15
                ),
                width=400,
                padding=20
            ),
            actions=[
                ft.TextButton("Cancel", style=ft.ButtonStyle(color="#002A7A"), on_click=close_profile_dialog),
                ft.TextButton("Save", style=ft.ButtonStyle(color="#002A7A"), on_click=validate_and_update_profile),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.overlay.append(profile_dialog)
        profile_dialog.open = True
        page.update()
    
    def show_about_dialog(e):
        """Show about dialog with app information"""
        about_dialog = ft.AlertDialog(
            modal=True,
            bgcolor="white",
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(
                            "Smart Augmented Reality Interactive Navigation App \n(SARI NA)",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color="black",
                            text_align=ft.TextAlign.CENTER
                        ),
                        ft.Divider(color="black"),
                        ft.Text(
                            "Version: 1.0.0\n\n"
                            "SARI NA is an innovative AR-powered campus navigation application "
                            "designed to help students, faculty, staff, alumni, and visitors "
                            "navigate the CSPC campus with ease.\n\n"
                            "Features:\n"
                            "• Real-time AR navigation\n"
                            "• Interactive campus map\n"
                            "• User-friendly interface\n\n"
                            "For support or feedback, please contact us at support@sarina.edu\n\n\n"
                            "© 2025 Werna. All rights reserved.",
                            size=14,
                            color="black"
                        )
                    ],
                    scroll=ft.ScrollMode.AUTO,
                    spacing=10,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                ),
                width=400,
                height=500
            ),
            actions=[
                ft.TextButton("Close", style=ft.ButtonStyle(color="#002A7A"), on_click=lambda e: close_about_dialog(about_dialog))
            ],
        )
        page.overlay.append(about_dialog)
        about_dialog.open = True
        page.update()
    
    def close_about_dialog(dialog):
        dialog.open = False
        page.update()
    
    def open_buy_coffee(e):
        """Open Buy Me a Coffee link"""
        page.launch_url("https://www.buymeacoffee.com")
    
    return ft.View(
        "/settings",
        controls=[
            ft.Container(
                content=ft.Column(
                    controls=[
                        # Header with back button and logo
                        ft.Container(
                            content=ft.Row(
                                controls=[
                                    ft.IconButton(
                                        icon=ft.Icons.ARROW_BACK,
                                        icon_color="white",
                                        icon_size=30,
                                        on_click=lambda _: page.go("/home")
                                    ),
                                    ft.Container(width=45),
                                    ft.Image(
                                        src="sarina_logo.png",
                                        width=120,
                                        fit=ft.ImageFit.CONTAIN
                                    ),
                                    ft.Container(expand=True),
                                ],
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            padding=ft.padding.only(top=50, left=10, right=20, bottom=10)
                        ),
                        
                        # Profile Section
                        ft.Container(
                            content=ft.Row(
                                controls=[
                                    ft.Container(width=20),
                                    ft.Icon(
                                        ft.Icons.ACCOUNT_CIRCLE,
                                        size=80,
                                        color="white"
                                    ),
                                    ft.Container(width=5),
                                    ft.Column(
                                        controls=[
                                            ft.Text(
                                                user_data.get("name", "Guest").upper(),
                                                size=22,
                                                weight=ft.FontWeight.BOLD,
                                                color="white"
                                            ),
                                            ft.Text(
                                                user_data.get("role", "Unknown"),
                                                size=16,
                                                color="white70"
                                            ),
                                        ],
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        spacing=0
                                    ),
                                    ft.Container(expand=True),
                                ],
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            padding=ft.padding.only(top=10, bottom=20)
                        ),
                        
                        ft.Divider(color="white", height=1),
                        
                        # Settings Options
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    # About
                                    ft.Container(
                                        content=ft.Row(
                                            controls=[
                                                ft.Icon(
                                                    ft.Icons.INFO_OUTLINE,
                                                    color="white",
                                                    size=24
                                                ),
                                                ft.Text(
                                                    "About",
                                                    color="white",
                                                    size=18
                                                )
                                            ],
                                            spacing=15
                                        ),
                                        on_click=show_about_dialog,
                                        padding=15,
                                        ink=True
                                    ),
                                    
                                    # Edit Profile
                                    ft.Container(
                                        content=ft.Row(
                                            controls=[
                                                ft.Icon(
                                                    ft.Icons.EDIT,
                                                    color="white",
                                                    size=24
                                                ),
                                                ft.Text(
                                                    "Edit Profile",
                                                    color="white",
                                                    size=18
                                                )
                                            ],
                                            spacing=15
                                        ),
                                        on_click=show_edit_profile_dialog,
                                        padding=15,
                                        ink=True
                                    ),
                                    
                                    # Change Password
                                    ft.Container(
                                        content=ft.Row(
                                            controls=[
                                                ft.Icon(
                                                    ft.Icons.KEY,
                                                    color="white",
                                                    size=24
                                                ),
                                                ft.Text(
                                                    "Change Password",
                                                    color="white",
                                                    size=18
                                                )
                                            ],
                                            spacing=15
                                        ),
                                        on_click=show_change_password_dialog,
                                        padding=15,
                                        ink=True
                                    ),
                                    
                                    # Buy Us Coffee
                                    ft.Container(
                                        content=ft.Row(
                                            controls=[
                                                ft.Icon(
                                                    ft.Icons.COFFEE,
                                                    color="white",
                                                    size=24
                                                ),
                                                ft.Text(
                                                    "Buy us Coffee",
                                                    color="white",
                                                    size=18
                                                )
                                            ],
                                            spacing=15
                                        ),
                                        on_click=open_buy_coffee,
                                        padding=15,
                                        ink=True
                                    ),
                                ],
                                spacing=10
                            ),
                            padding=ft.padding.symmetric(horizontal=20, vertical=10)
                        ),
                        
                        # Spacer
                        ft.Container(expand=True),
                        
                        # Logout Button
                        ft.Container(
                            content=ft.ElevatedButton(
                                content=ft.Container(
                                    content=ft.Text(
                                        "Logout",
                                        size=18,
                                        weight=ft.FontWeight.BOLD,
                                        color="#002A7A"
                                    ),
                                    padding=ft.padding.symmetric(horizontal=120, vertical=15)
                                ),
                                style=ft.ButtonStyle(
                                    bgcolor="white",
                                    shape=ft.RoundedRectangleBorder(radius=30)
                                ),
                                on_click=show_logout_confirmation
                            ),
                            alignment=ft.alignment.center,
                            padding=ft.padding.only(bottom=80)
                        )
                    ],
                    spacing=0
                ),
                bgcolor="#002A7A",
                expand=True
            )
        ],
        padding=0,
        bgcolor="#002A7A"
    )
