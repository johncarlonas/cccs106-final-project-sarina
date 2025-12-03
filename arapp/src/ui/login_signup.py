import flet as ft

def LoginSignupView(page: ft.Page):
    return ft.View(
        "/login_signup",
        controls=[
            ft.Container(
                content=ft.Text("Login/Signup Screen", color="white", size=24),
                alignment=ft.alignment.center,
                expand=True,
                bgcolor="#041E42",
            )
        ],
        padding=0,
        bgcolor="#041E42"
    )
