import flet as ft
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from database.db import add_user
from utils.email_service import EmailService

def EmailVerificationView(page: ft.Page):
    # Get signup data from session
    signup_data = page.session.get("signup_data")
    
    if not signup_data:
        page.go("/login_signup")
        return ft.View("/email_verification", controls=[])
    
    # Generate and send OTP
    otp_code = EmailService.generate_otp()
    page.session.set("otp_code", otp_code)
    
    # Send OTP email
    EmailService.send_otp_email(signup_data['email'], otp_code, purpose="verification")
    
    # Error message ref
    otp_error = ft.Ref[ft.Text]()
    otp_input = ft.Ref[ft.TextField]()
    
    def on_back_to_login(e):
        page.go("/login_signup")
    
    def show_success_modal():
        """Show success modal after email verification"""
        def close_and_navigate(e):
            page.close(success_modal)
            # Save user to database
            user_id = add_user(
                signup_data["name"],
                signup_data["email"],
                signup_data["password"],
                signup_data["role"]
            )
            
            if user_id:
                # Save logged in user
                page.client_storage.set("logged_in_user", signup_data["email"])
                page.client_storage.set("first_launch", False)
                page.session.set("user_email", signup_data["email"])
                page.go("/home")
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Error creating account. Please try again."))
                page.snack_bar.open = True
                page.update()
        
        success_modal = ft.AlertDialog(
            title=ft.Text(
                "Email Verified!",
                color="#002A7A",
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER
            ),
            content=ft.Text(
                "Your email has been successfully verified. Welcome to SARI NA!",
                color="black",
                text_align=ft.TextAlign.CENTER
            ),
            actions=[
                ft.Container(
                    content=ft.ElevatedButton(
                        content=ft.Text(
                            "Proceed to Home",
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
    
    def on_confirm_email(e):
        """Handle confirm email button click"""
        # Clear previous error
        otp_error.current.value = ""
        otp_error.current.visible = False
        
        entered_otp = otp_input.current.value.strip()
        
        if not entered_otp:
            page.snack_bar = ft.SnackBar(ft.Text("Please enter the OTP"))
            page.snack_bar.open = True
            page.update()
            return
        
        # Verify OTP
        stored_otp = page.session.get("otp_code")
        
        if entered_otp == stored_otp:
            # OTP is correct
            show_success_modal()
        else:
            # OTP is invalid
            otp_error.current.value = "Invalid OTP. Please try again."
            otp_error.current.visible = True
            page.update()
    
    return ft.View(
        "/email_verification",
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
                        
                        # Email Verification Title
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text(
                                        "Email Verification",
                                        size=24,
                                        weight=ft.FontWeight.BOLD,
                                        color="white",
                                        text_align=ft.TextAlign.CENTER
                                    ),
                                    ft.Container(height=10),
                                    ft.Text(
                                        "An email has sent to your email address for OTP.",
                                        size=14,
                                        color="white70",
                                        text_align=ft.TextAlign.CENTER
                                    )
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER
                            ),
                            padding=ft.padding.symmetric(horizontal=30, vertical=20)
                        ),
                        
                        # OTP Input
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
                                        hint_text="Enter One-Time PIN",
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
                        
                        # Confirm Button
                        ft.Container(
                            content=ft.ElevatedButton(
                                content=ft.Text(
                                    "Confirm Email",
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
                                on_click=on_confirm_email
                            ),
                            padding=ft.padding.only(top=20),
                            alignment=ft.alignment.center
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
