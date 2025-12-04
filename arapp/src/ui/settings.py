import flet as ft

def SettingsView(page: ft.Page):
    # References for change password fields
    current_password = ft.Ref[ft.TextField]()
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
            page.go("/login_signup")
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirm Logout"),
            content=ft.Text("Are you sure you want to log out?"),
            actions=[
                ft.TextButton("Cancel", on_click=close_dlg),
                ft.TextButton("Yes", on_click=confirm_logout),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
    
    def show_change_password_dialog(e):
        """Show change password dialog"""
        current_password_field = ft.TextField(
            ref=current_password,
            label="Current Password",
            password=True,
            can_reveal_password=True,
            border_color="white",
            label_style=ft.TextStyle(color="white"),
            text_style=ft.TextStyle(color="white"),
        )
        
        new_password_field = ft.TextField(
            ref=new_password,
            label="New Password",
            password=True,
            can_reveal_password=True,
            border_color="white",
            label_style=ft.TextStyle(color="white"),
            text_style=ft.TextStyle(color="white"),
        )
        
        retype_password_field = ft.TextField(
            ref=retype_password,
            label="Re-type New Password",
            password=True,
            can_reveal_password=True,
            border_color="white",
            label_style=ft.TextStyle(color="white"),
            text_style=ft.TextStyle(color="white"),
        )
        
        def validate_and_change_password(e):
            # Clear previous errors
            current_password_field.error_text = None
            new_password_field.error_text = None
            retype_password_field.error_text = None
            
            is_valid = True
            
            # Validate current password
            if not current_password_field.value:
                current_password_field.error_text = "This field is required to verify your identity"
                is_valid = False
            
            # Validate new password
            if not new_password_field.value:
                new_password_field.error_text = "This field is required to set a new password"
                is_valid = False
            
            # Validate retype password
            if not retype_password_field.value:
                retype_password_field.error_text = "This field is required to confirm your new password"
                is_valid = False
            elif new_password_field.value and retype_password_field.value != new_password_field.value:
                retype_password_field.error_text = "Passwords do not match"
                is_valid = False
            
            page.update()
            
            if is_valid:
                password_dialog.open = False
                page.update()
                
                # Show success message
                success_dialog = ft.AlertDialog(
                    modal=True,
                    title=ft.Text("Success"),
                    content=ft.Text("Password has been updated successfully!"),
                    actions=[
                        ft.TextButton("OK", on_click=lambda e: close_success_dialog(success_dialog))
                    ],
                )
                page.overlay.append(success_dialog)
                success_dialog.open = True
                page.update()
        
        def close_success_dialog(dialog):
            dialog.open = False
            page.update()
        
        def close_password_dialog(e):
            password_dialog.open = False
            page.update()
        
        password_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Change Password"),
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        current_password_field,
                        new_password_field,
                        retype_password_field,
                    ],
                    tight=True,
                    spacing=15
                ),
                width=400,
                padding=20
            ),
            actions=[
                ft.TextButton("Cancel", on_click=close_password_dialog),
                ft.TextButton("Confirm", on_click=validate_and_change_password),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.overlay.append(password_dialog)
        password_dialog.open = True
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
                ft.TextButton("Close", on_click=lambda e: close_about_dialog(about_dialog))
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
                                    ft.Container(expand=True),
                                    ft.Image(
                                        src="sarina_logo.png",
                                        width=120,
                                        fit=ft.ImageFit.CONTAIN
                                    ),
                                    ft.Container(expand=True),
                                ],
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            padding=ft.padding.only(top=20, left=10, right=20, bottom=10)
                        ),
                        
                        # Profile Section
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Icon(
                                        ft.Icons.ACCOUNT_CIRCLE,
                                        size=80,
                                        color="white"
                                    ),
                                    ft.Text(
                                        "JUAN DELA CRUZ",
                                        size=22,
                                        weight=ft.FontWeight.BOLD,
                                        color="white"
                                    ),
                                    ft.Text(
                                        "Student",
                                        size=16,
                                        color="white70"
                                    ),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=5
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
                            padding=ft.padding.only(bottom=40)
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
