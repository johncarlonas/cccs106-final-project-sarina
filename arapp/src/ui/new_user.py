import flet as ft

def NewUserView(page: ft.Page):
    return ft.View(
        "/new_user",
        controls=[
            ft.Container(
                content=ft.Column(
                    controls=[
                        # Content Section (Logo, Image, Text)
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Image(
                                        src="sarina_logo.png",
                                        width=250,
                                        fit=ft.ImageFit.CONTAIN
                                    ),
                                    ft.Image(
                                        src="sarina_3d.png",
                                        width=300,
                                        fit=ft.ImageFit.CONTAIN
                                    ),
                                    ft.Text(
                                        "Your first step to knowing every\ncorner of campus.",
                                        color="white",
                                        size=18,
                                        text_align=ft.TextAlign.CENTER,
                                        weight=ft.FontWeight.BOLD
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=20
                            ),
                            expand=True,
                            alignment=ft.alignment.center
                        ),
                        # Button Section
                        ft.Container(
                            content=ft.ElevatedButton(
                                content=ft.Container(
                                    content=ft.Text("Next", size=18, weight=ft.FontWeight.BOLD, color="#041E42"),
                                    padding=ft.padding.symmetric(horizontal=120, vertical=15),
                                ),
                                style=ft.ButtonStyle(
                                    bgcolor="white",
                                    shape=ft.RoundedRectangleBorder(radius=30),
                                ),
                                on_click=lambda _: page.go("/user_selection")
                            ),
                            padding=ft.padding.only(bottom=80),
                            alignment=ft.alignment.center
                        )
                    ],
                ),
                expand=True,
                bgcolor="#002A7A",
                padding=20
            )
        ],
        padding=0,
        bgcolor="#002A7A"
    )
