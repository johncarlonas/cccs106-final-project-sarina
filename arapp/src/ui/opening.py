import flet as ft

def OpeningView(page: ft.Page):
    return ft.View(
        "/",
        controls=[
            ft.Container(
                content=ft.Image(
                    src="sarina_logo.png", 
                    width=300, 
                    fit=ft.ImageFit.CONTAIN
                ),
                alignment=ft.alignment.center,
                expand=True,
                bgcolor="#002A7A",
            )
        ],
        padding=0,
        bgcolor="#002A7A"
    )
