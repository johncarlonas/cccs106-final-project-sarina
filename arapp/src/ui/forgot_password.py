import flet as ft
import sys
import os
import re

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from database.db import check_user_exists, update_user_password
from utils.email_service import EmailService

def ForgotPasswordView(page: ft.Page):
    # Error message refs
    email_error = ft.Ref[ft.Text]()
    otp_error = ft.Ref[ft.Text]()
    
    # Input refs
    email_input = ft.Ref[ft.TextField]()
    otp_input = ft.Ref[ft.TextField]()
    
    # Container refs for showing/hiding
    otp_section = ft.Ref[ft.Container]()
    email_sent_message = ft.Ref[ft.Container]()
    
    # Password rules refs for modal
    rule_length = ft.Ref[ft.Text]()
    rule_uppercase = ft.Ref[ft.Text]()
    rule_special = ft.Ref[ft.Text]()
    
    def check_password_rules(password):
        """Check password against all rules and return status"""
        has_length = len(password) >= 8
        has_uppercase = bool(re.search(r'[A-Z]', password))
        has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
        
        return {
            'length': has_length,
            'uppercase': has_uppercase,
            'special': has_special,
            'all_valid': has_length and has_uppercase and has_special
        }
    
    def on_back_to_login(e):
        page.go("/login_signup")
    
    def on_receive_otp(e):
        """Handle Receive OTP button click"""
        # Clear previous errors
        email_error.current.value = ""
        email_error.current.visible = False
        
        email = email_input.current.value.strip().lower()
        
        if not email:
            page.snack_bar = ft.SnackBar(ft.Text("Please enter your email address"))
            page.snack_bar.open = True
            page.update()
            return
        
        # Check if email exists in database
        if not check_user_exists(email):
            email_error.current.value = "This email doesn't exist"
            email_error.current.visible = True
            otp_section.current.visible = False
            email_sent_message.current.visible = False
            page.update()
            return
        
        # Email exists - generate and send OTP
        otp_code = EmailService.generate_otp()
        page.session.set("reset_otp", otp_code)
        page.session.set("reset_email", email)
        
        # Send OTP email
        EmailService.send_otp_email(email, otp_code, purpose="password_reset")
        
        # Show OTP section and message
        otp_section.current.visible = True
        email_sent_message.current.visible = True
        page.update()
    
    def show_new_password_modal():
        """Show modal for entering new password"""
        password_match_error = ft.Text(
            value="",
            color="red",
            size=12,
            visible=False
        )
        
        new_password_input = ft.TextField(
            hint_text="Enter new password",
            hint_style=ft.TextStyle(color="black30", size=14),
            color="black",
            border_color="#002A7A",
            border_radius=10,
            password=True,
            can_reveal_password=True,
            content_padding=ft.padding.symmetric(horizontal=15, vertical=12),
            text_size=14,
            on_change=lambda e: update_password_rules(e.control.value)
        )
        
        def on_confirm_password_input_change(e):
            """Check if passwords match while typing"""
            new_password = new_password_input.value
            confirm_password = e.control.value
            
            if confirm_password and new_password != confirm_password:
                password_match_error.value = "Passwords do not match"
                password_match_error.visible = True
            else:
                password_match_error.value = ""
                password_match_error.visible = False
            page.update()
        
        confirm_password_input = ft.TextField(
            hint_text="Confirm new password",
            hint_style=ft.TextStyle(color="black30", size=14),
            color="black",
            border_color="#002A7A",
            border_radius=10,
            password=True,
            can_reveal_password=True,
            content_padding=ft.padding.symmetric(horizontal=15, vertical=12),
            text_size=14,
            on_change=on_confirm_password_input_change
        )
        
        password_rules_display = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        ref=rule_length,
                        value="• At least 8 characters",
                        color="red",
                        size=12
                    ),
                    ft.Text(
                        ref=rule_uppercase,
                        value="• At least 1 uppercase letter",
                        color="red",
                        size=12
                    ),
                    ft.Text(
                        ref=rule_special,
                        value="• At least 1 special character",
                        color="red",
                        size=12
                    )
                ],
                spacing=5
            ),
            padding=ft.padding.only(top=10, bottom=10)
        )
        
        def update_password_rules(password):
            """Update password rules display"""
            rules = check_password_rules(password)
            rule_length.current.color = "#00AA00" if rules['length'] else "red"
            rule_uppercase.current.color = "#00AA00" if rules['uppercase'] else "red"
            rule_special.current.color = "#00AA00" if rules['special'] else "red"
            page.update()
        
        def on_confirm_password_change(e):
            """Handle password change confirmation"""
            new_password = new_password_input.value
            confirm_password = confirm_password_input.value
            
            if not new_password or not confirm_password:
                page.snack_bar = ft.SnackBar(ft.Text("Please fill in both password fields"))
                page.snack_bar.open = True
                page.update()
                return
            
            # Check password rules
            rules = check_password_rules(new_password)
            if not rules['all_valid']:
                page.snack_bar = ft.SnackBar(ft.Text("Password must meet all requirements"))
                page.snack_bar.open = True
                page.update()
                return
            
            # Check if passwords match
            if new_password != confirm_password:
                page.snack_bar = ft.SnackBar(ft.Text("Passwords do not match"))
                page.snack_bar.open = True
                page.update()
                return
            
            # Update password in database
            reset_email = page.session.get("reset_email")
            if update_user_password(reset_email, new_password):
                page.close(password_modal)
                show_success_modal()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Failed to update password. Please try again."))
                page.snack_bar.open = True
                page.update()
        
        password_modal = ft.AlertDialog(
            title=ft.Text(
                "Create New Password",
                color="#002A7A",
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER
            ),
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(
                            "New Password",
                            color="black",
                            size=14,
                            weight=ft.FontWeight.W_500
                        ),
                        new_password_input,
                        password_rules_display,
                        ft.Container(height=10),
                        ft.Text(
                            "Confirm Password",
                            color="black",
                            size=14,
                            weight=ft.FontWeight.W_500
                        ),
                        confirm_password_input,
                        password_match_error,
                    ],
                    spacing=5,
                    tight=True
                ),
                width=350
            ),
            actions=[
                ft.Container(
                    content=ft.ElevatedButton(
                        content=ft.Text(
                            "Change Password",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color="white"
                        ),
                        bgcolor="#002A7A",
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=25)
                        ),
                        on_click=on_confirm_password_change
                    ),
                    alignment=ft.alignment.center,
                    width=300
                )
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
            bgcolor="white",
            shape=ft.RoundedRectangleBorder(radius=15)
        )
        
        page.open(password_modal)
    
    def show_success_modal():
        """Show success modal after password change"""
        def close_and_navigate(e):
            page.close(success_modal)
            page.go("/login_signup")
        
        success_modal = ft.AlertDialog(
            title=ft.Text(
                "Password Changed!",
                color="#002A7A",
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER
            ),
            content=ft.Text(
                "Your password has been successfully changed. You can now log in with your new password.",
                color="black",
                text_align=ft.TextAlign.CENTER
            ),
            actions=[
                ft.Container(
                    content=ft.ElevatedButton(
                        content=ft.Text(
                            "Back to Login",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color="white"
                        ),
                        bgcolor="#002A7A",
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=25)
                        ),
                        on_click=close_and_navigate
                    ),
                    alignment=ft.alignment.center,
                    width=300
                )
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
            bgcolor="white",
            shape=ft.RoundedRectangleBorder(radius=15)
        )
        
        page.open(success_modal)
    
    def on_submit_otp(e):
        """Handle OTP submission"""
        # Clear previous errors
        otp_error.current.value = ""
        otp_error.current.visible = False
        
        entered_otp = otp_input.current.value.strip()
        
        if not entered_otp:
            page.snack_bar = ft.SnackBar(ft.Text("Please enter the OTP"))
            page.snack_bar.open = True
            page.update()
            return
        
        # Verify OTP
        stored_otp = page.session.get("reset_otp")
        
        if entered_otp == stored_otp:
            # OTP is correct - show new password modal
            show_new_password_modal()
        else:
            # OTP is invalid
            otp_error.current.value = "Invalid OTP. Please try again."
            otp_error.current.visible = True
            page.update()
    
    return ft.View(
        "/forgot_password",
        controls=[
            ft.Container(
                content=ft.Column(
                    controls=[
                        # Logo
                        ft.Container(
                            content=ft.Image(
                                src="sarina_logo.png",
                                width=180,
                                height=80,
                                fit=ft.ImageFit.CONTAIN
                            ),
                            padding=ft.padding.only(top=40, bottom=20),
                            alignment=ft.alignment.center
                        ),
                        
                        # Back to Login Button
                        ft.Container(
                            content=ft.ElevatedButton(
                                content=ft.Text(
                                    "Back to Login",
                                    size=14,
                                    weight=ft.FontWeight.BOLD,
                                    color="#002A7A"
                                ),
                                bgcolor="white",
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=20)
                                ),
                                on_click=on_back_to_login
                            ),
                            alignment=ft.alignment.center,
                            padding=ft.padding.only(bottom=30)
                        ),
                        
                        # Title
                        ft.Container(
                            content=ft.Text(
                                "Forgot Password",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color="white",
                                text_align=ft.TextAlign.CENTER
                            ),
                            padding=ft.padding.symmetric(horizontal=30, vertical=20)
                        ),
                        
                        # Email Input
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text(
                                        "Enter your email address",
                                        color="white",
                                        size=14,
                                        weight=ft.FontWeight.W_500
                                    ),
                                    ft.TextField(
                                        ref=email_input,
                                        hint_text="Enter your email address",
                                        hint_style=ft.TextStyle(color="white30", size=14),
                                        color="white",
                                        border_color="transparent",
                                        bgcolor="#80000000",
                                        border_radius=25,
                                        content_padding=ft.padding.symmetric(horizontal=20, vertical=15),
                                        text_size=14
                                    ),
                                    ft.Text(
                                        ref=email_error,
                                        value="",
                                        color="red",
                                        size=12,
                                        visible=False
                                    )
                                ],
                                spacing=5
                            ),
                            padding=ft.padding.symmetric(horizontal=30, vertical=10)
                        ),
                        
                        # Receive OTP Button
                        ft.Container(
                            content=ft.ElevatedButton(
                                content=ft.Text(
                                    "Receive OTP",
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                    color="#002A7A"
                                ),
                                bgcolor="white",
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=25),
                                    padding=ft.padding.symmetric(horizontal=0, vertical=15)
                                ),
                                width=300,
                                on_click=on_receive_otp
                            ),
                            padding=ft.padding.only(top=10),
                            alignment=ft.alignment.center
                        ),
                        
                        # Email Sent Message (Hidden by default)
                        ft.Container(
                            ref=email_sent_message,
                            content=ft.Text(
                                "An email has been sent to your email address for OTP.",
                                size=14,
                                color="white70",
                                text_align=ft.TextAlign.CENTER
                            ),
                            padding=ft.padding.symmetric(horizontal=30, vertical=15),
                            visible=False
                        ),
                        
                        # OTP Section (Hidden by default)
                        ft.Container(
                            ref=otp_section,
                            content=ft.Column(
                                controls=[
                                    ft.Container(
                                        content=ft.Column(
                                            controls=[
                                                ft.Text(
                                                    "One-Time Pin",
                                                    color="white",
                                                    size=14,
                                                    weight=ft.FontWeight.W_500
                                                ),
                                                ft.TextField(
                                                    ref=otp_input,
                                                    hint_text="Enter OTP",
                                                    hint_style=ft.TextStyle(color="white30", size=14),
                                                    color="white",
                                                    border_color="transparent",
                                                    bgcolor="#80000000",
                                                    border_radius=25,
                                                    content_padding=ft.padding.symmetric(horizontal=20, vertical=15),
                                                    text_size=16,
                                                    text_align=ft.TextAlign.CENTER,
                                                    keyboard_type=ft.KeyboardType.NUMBER,
                                                    max_length=6
                                                ),
                                                ft.Text(
                                                    ref=otp_error,
                                                    value="",
                                                    color="red",
                                                    size=12,
                                                    visible=False
                                                )
                                            ],
                                            spacing=5
                                        ),
                                        padding=ft.padding.symmetric(horizontal=30, vertical=10)
                                    ),
                                    
                                    # Submit Button
                                    ft.Container(
                                        content=ft.ElevatedButton(
                                            content=ft.Text(
                                                "Submit",
                                                size=16,
                                                weight=ft.FontWeight.BOLD,
                                                color="#002A7A"
                                            ),
                                            bgcolor="white",
                                            style=ft.ButtonStyle(
                                                shape=ft.RoundedRectangleBorder(radius=25),
                                                padding=ft.padding.symmetric(horizontal=0, vertical=15)
                                            ),
                                            width=300,
                                            on_click=on_submit_otp
                                        ),
                                        padding=ft.padding.only(top=10),
                                        alignment=ft.alignment.center
                                    ),
                                ],
                                spacing=0
                            ),
                            visible=False
                        ),
                        
                        # Bottom spacer
                        ft.Container(expand=True)
                    ],
                    spacing=0,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                ),
                bgcolor="#002A7A",
                expand=True
            )
        ],
        padding=0,
        bgcolor="#002A7A"
    )
