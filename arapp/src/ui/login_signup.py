import flet as ft
import os
import sys
import re

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import check_user_exists, verify_user_login, supabase

def LoginSignupView(page: ft.Page):
    # Set theme for password reveal icon color
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            on_surface_variant="#002A7A"
        )
    )
    
    # Load remembered email if exists
    remembered_email = page.client_storage.get("remembered_email")
    
    # Toggle state
    signup_container = ft.Container()
    login_container = ft.Container()
    signup_button = ft.Container()
    login_button = ft.Container()
    
    # Error message refs
    signup_email_error = ft.Ref[ft.Text]()
    login_email_error = ft.Ref[ft.Text]()
    login_password_error = ft.Ref[ft.Text]()
    
    # Password rules refs
    rule_length = ft.Ref[ft.Text]()
    rule_uppercase = ft.Ref[ft.Text]()
    rule_special = ft.Ref[ft.Text]()
    password_rules_container = ft.Ref[ft.Container]()
    
    def capitalize_name(name):
        """Capitalize each word in the name properly"""
        return ' '.join(word.capitalize() for word in name.split())
    
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
    
    def on_signup_password_change(e):
        """Update password rules display when user types"""
        password = signup_password.value
        rules = check_password_rules(password)
        
        # Show rules container
        password_rules_container.current.visible = True
        
        # Update rule colors
        rule_length.current.color = "white" if rules['length'] else "red"
        rule_uppercase.current.color = "white" if rules['uppercase'] else "red"
        rule_special.current.color = "white" if rules['special'] else "red"
        
        page.update()
    
    def on_signup_password_focus(e):
        """Show password rules when focused"""
        password_rules_container.current.visible = True
        page.update()
    
    def on_fullname_blur(e):
        """Capitalize name when user leaves the field"""
        if signup_fullname.value:
            signup_fullname.value = capitalize_name(signup_fullname.value)
            page.update()
    
    def on_signup_click(e):
        """Handle sign up button click"""
        # Clear previous errors
        signup_email_error.current.value = ""
        signup_email_error.current.visible = False
        
        fullname = signup_fullname.value.strip()
        email = signup_email.value.strip().lower()
        password = signup_password.value
        
        # Get selected role from session
        selected_role = page.session.get("selected_role")
        
        # Validate inputs
        has_error = False
        
        if not fullname or not email or not password:
            page.snack_bar = ft.SnackBar(ft.Text("Please fill in all fields"))
            page.snack_bar.open = True
            page.update()
            return
        
        # Validate email based on role
        is_cspc_email = email.endswith("@my.cspc.edu.ph") or email.endswith("@cspc.edu.ph")
        
        if selected_role == "CSPCean":
            if not is_cspc_email:
                signup_email_error.current.value = "Please use your CSPC email."
                signup_email_error.current.visible = True
                has_error = True
        elif selected_role == "Visitor":
            if is_cspc_email:
                signup_email_error.current.value = "Please use your personal email, not CSPC email"
                signup_email_error.current.visible = True
                has_error = True
        
        # Check if email already exists (only if no role-based error)
        if not has_error and check_user_exists(email):
            signup_email_error.current.value = "This email is already used"
            signup_email_error.current.visible = True
            has_error = True
        
        # Check password rules
        rules = check_password_rules(password)
        if not rules['all_valid']:
            has_error = True
        
        page.update()
        
        if has_error:
            return
        
        # Capitalize name
        fullname = capitalize_name(fullname)
        
        # All validations passed - navigate to email verification
        page.session.set("signup_data", {
            "name": fullname,
            "email": email,
            "password": password,
            "role": selected_role
        })
        page.go("/email_verification")
    
    def on_login_click(e):
        """Handle login button click"""
        # Clear previous errors
        login_email_error.current.value = ""
        login_email_error.current.visible = False
        login_password_error.current.value = ""
        login_password_error.current.visible = False
        
        email = login_email.value.strip()
        password = login_password.value
        
        # Validate inputs
        if not email or not password:
            page.snack_bar = ft.SnackBar(ft.Text("Please fill in all fields"))
            page.snack_bar.open = True
            page.update()
            return
        
        # Check if user exists
        if not check_user_exists(email):
            login_email_error.current.value = "This email doesn't exist"
            login_email_error.current.visible = True
            page.update()
            return
        
        # Verify password
        if not verify_user_login(email, password):
            login_password_error.current.value = "Incorrect password"
            login_password_error.current.visible = True
            page.update()
            return
        
        # Login successful - save to client storage
        page.client_storage.set("logged_in_user", email)
        page.client_storage.set("first_launch", False)
        page.session.set("user_email", email)
        
        # Handle Remember Me
        if login_remember.value:
            page.client_storage.set("remembered_email", email)
        else:
            page.client_storage.remove("remembered_email")
        
        # Check user role - if Admin, go to dashboard, else go to home
        try:
            response = supabase.table("users").select("role").eq("email", email).execute()
            if response.data and len(response.data) > 0:
                user_role = response.data[0]["role"]
                if user_role == "Admin":
                    page.go("/dashboard")
                else:
                    page.go("/home")
            else:
                page.go("/home")
        except Exception as e:
            print(f"Error checking user role: {e}")
            page.go("/home")
    
    def switch_to_signup(e):
        signup_button.bgcolor = "white"
        signup_button.content.color = "#002A7A"
        login_button.bgcolor = "transparent"
        login_button.content.color = "white"
        signup_container.visible = True
        login_container.visible = False
        # Clear errors
        signup_email_error.current.value = ""
        signup_email_error.current.visible = False
        password_rules_container.current.visible = False
        page.update()
    
    def switch_to_login(e):
        login_button.bgcolor = "white"
        login_button.content.color = "#002A7A"
        signup_button.bgcolor = "transparent"
        signup_button.content.color = "white"
        login_container.visible = True
        signup_container.visible = False
        # Clear errors
        login_email_error.current.value = ""
        login_email_error.current.visible = False
        login_password_error.current.value = ""
        login_password_error.current.visible = False
        page.update()
    
    # Configure toggle buttons
    signup_button = ft.Container(
        content=ft.Text("Sign Up", size=16, weight=ft.FontWeight.BOLD, color="#002A7A"),
        bgcolor="white",
        border_radius=20,
        padding=ft.padding.symmetric(horizontal=35, vertical=12),
        on_click=switch_to_signup
    )
    
    login_button = ft.Container(
        content=ft.Text("Login", size=16, weight=ft.FontWeight.BOLD, color="white"),
        bgcolor="transparent",
        border_radius=20,
        padding=ft.padding.symmetric(horizontal=35, vertical=12),
        on_click=switch_to_login
    )
    
    # Sign Up Form
    signup_fullname = ft.TextField(
        hint_text="Enter your full name",
        hint_style=ft.TextStyle(color="white30", size=14),
        color="white",
        border_color="transparent",
        bgcolor="#80000000",
        border_radius=25,
        content_padding=ft.padding.symmetric(horizontal=20, vertical=15),
        text_size=14,
        on_blur=on_fullname_blur
    )
    
    signup_email = ft.TextField(
        hint_text="Enter your email address",
        hint_style=ft.TextStyle(color="white30", size=14),
        color="white",
        border_color="transparent",
        bgcolor="#80000000",
        border_radius=25,
        content_padding=ft.padding.symmetric(horizontal=20, vertical=15),
        text_size=14
    )
    
    signup_password = ft.TextField(
        hint_text="Enter your password",
        hint_style=ft.TextStyle(color="white30", size=14),
        color="white",
        border_color="transparent",
        bgcolor="#80000000",
        border_radius=25,
        password=True,
        can_reveal_password=True,
        content_padding=ft.padding.only(left=20, right=55, top=15, bottom=15),
        text_size=14,
        on_change=on_signup_password_change,
        on_focus=on_signup_password_focus
    )
    
    signup_remember = ft.Checkbox(
        label="Remember Me",
        fill_color="white",
        check_color="#002A7A",
        label_style=ft.TextStyle(color="white", size=14),
        border_side=ft.BorderSide(2, "white")
    )
    
    # Login Form
    login_email = ft.TextField(
        hint_text="Enter your email address",
        hint_style=ft.TextStyle(color="white30", size=14),
        color="white",
        border_color="transparent",
        bgcolor="#80000000",
        border_radius=25,
        content_padding=ft.padding.symmetric(horizontal=20, vertical=15),
        text_size=14,
        value=remembered_email if remembered_email else ""
    )
    
    login_password = ft.TextField(
        hint_text="Enter your password",
        hint_style=ft.TextStyle(color="white30", size=14),
        color="white",
        border_color="transparent",
        bgcolor="#80000000",
        border_radius=25,
        password=True,
        can_reveal_password=True,
        content_padding=ft.padding.only(left=20, right=55, top=15, bottom=15),
        text_size=14
    )
    
    login_remember = ft.Checkbox(
        label="Remember Me",
        fill_color="white",
        check_color="#002A7A",
        label_style=ft.TextStyle(color="white", size=14),
        border_side=ft.BorderSide(2, "white"),
        value=True if remembered_email else False
    )
    
    # Sign Up Container
    signup_container = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    "Create an Account",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color="white",
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Container(height=20),
                ft.Container(
                    content=ft.Text("Full Name", color="white", size=14, weight=ft.FontWeight.W_500),
                    alignment=ft.alignment.center_left
                ),
                signup_fullname,
                ft.Container(height=10),
                ft.Container(
                    content=ft.Text("Email Address", color="white", size=14, weight=ft.FontWeight.W_500),
                    alignment=ft.alignment.center_left
                ),
                signup_email,
                ft.Text(
                    ref=signup_email_error,
                    value="",
                    color="red",
                    size=12,
                    visible=False
                ),
                ft.Container(height=10),
                ft.Container(
                    content=ft.Text("Password", color="white", size=14, weight=ft.FontWeight.W_500),
                    alignment=ft.alignment.center_left
                ),
                signup_password,
                ft.Container(
                    ref=password_rules_container,
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                ref=rule_length,
                                value="• Minimum 8 characters",
                                color="red",
                                size=11
                            ),
                            ft.Text(
                                ref=rule_uppercase,
                                value="• At least 1 uppercase letter",
                                color="red",
                                size=11
                            ),
                            ft.Text(
                                ref=rule_special,
                                value="• At least 1 special character (!@#$%^&*)",
                                color="red",
                                size=11
                            )
                        ],
                        spacing=2
                    ),
                    padding=ft.padding.only(left=5, top=5),
                    visible=False
                ),
                ft.Container(height=10),
                signup_remember,
                ft.Container(height=15),
                ft.ElevatedButton(
                    content=ft.Text(
                        "Sign Up",
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
                    on_click=on_signup_click
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0
        ),
        visible=True
    )
    
    # Login Container
    login_container = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    "Welcome Back!",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color="white",
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Container(height=20),
                ft.Container(
                    content=ft.Text("Email Address", color="white", size=14, weight=ft.FontWeight.W_500),
                    alignment=ft.alignment.center_left
                ),
                login_email,
                ft.Text(
                    ref=login_email_error,
                    value="",
                    color="red",
                    size=12,
                    visible=False
                ),
                ft.Container(height=10),
                ft.Container(
                    content=ft.Text("Password", color="white", size=14, weight=ft.FontWeight.W_500),
                    alignment=ft.alignment.center_left
                ),
                login_password,
                ft.Text(
                    ref=login_password_error,
                    value="",
                    color="red",
                    size=12,
                    visible=False
                ),
                ft.Container(height=10),
                ft.Row(
                    controls=[
                        login_remember,
                        ft.Container(expand=True),
                        ft.TextButton(
                            "Forgot Password?",
                            style=ft.ButtonStyle(color="white"),
                            on_click=lambda e: page.go("/forgot_password")
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Container(height=15),
                ft.ElevatedButton(
                    content=ft.Text(
                        "Login",
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
                    on_click=on_login_click
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0
        ),
        visible=False
    )
    
    return ft.View(
        "/login_signup",
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
                        
                        # Toggle Buttons with black background
                        ft.Container(
                            content=ft.Row(
                                controls=[
                                    signup_button,
                                    login_button
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=15
                            ),
                            bgcolor="#80000000",
                            border_radius=25,
                            padding=ft.padding.all(5),
                            width=280
                        ),
                        
                        # Forms Container
                        ft.Container(
                            content=ft.Stack(
                                controls=[
                                    signup_container,
                                    login_container
                                ]
                            ),
                            padding=ft.padding.symmetric(horizontal=30, vertical=20),
                            expand=True
                        )
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
