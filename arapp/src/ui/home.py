import flet as ft

def HomeView(page: ft.Page):
    # State for search text
    search_query = ft.Ref[ft.TextField]()
    
    def on_search_click(e):
        query = search_query.current.value
        if query:
            # Handle search logic here
            print(f"Searching for: {query}")
    
    def on_profile_click(e):
        # Navigate to profile/settings
        page.go("/settings")
    
    def on_location_toggle(e):
        # Switch between My Location and College of Computer Studies
        print("Location toggled")
    
    def on_ar_mode_click(e):
        # Open AR mode
        print("AR Mode activated")
    
    return ft.View(
        "/home",
        controls=[
            ft.Container(
                content=ft.Column(
                    controls=[
                        # Header with Logo and Profile Icon
                        ft.Container(
                            content=ft.Row(
                                controls=[
                                    ft.Container(expand=True),  # Left spacer
                                    ft.Image(
                                        src="sarina_logo.png",
                                        width=120,
                                        fit=ft.ImageFit.CONTAIN
                                    ),
                                    ft.Container(expand=True),  # Right spacer
                                    ft.IconButton(
                                        icon=ft.Icons.ACCOUNT_CIRCLE,
                                        icon_color="white",
                                        icon_size=35,
                                        on_click=on_profile_click
                                    )
                                ],
                                vertical_alignment=ft.CrossAxisAlignment.CENTER
                            ),
                            padding=ft.padding.only(top=20, left=80, right=20, bottom=10)
                        ),
                        
                        # Search Bar
                        ft.Container(
                            content=ft.TextField(
                                ref=search_query,
                                hint_text="Where are you going?",
                                hint_style=ft.TextStyle(color="white70"),
                                text_style=ft.TextStyle(color="white"),
                                border_radius=25,
                                filled=True,
                                bgcolor="#003580",
                                border_color="transparent",
                                focused_border_color="#0055D4",
                                content_padding=ft.padding.symmetric(horizontal=20, vertical=10),
                                suffix=ft.IconButton(
                                    icon=ft.Icons.SEARCH,
                                    icon_color="white",
                                    on_click=on_search_click
                                )
                            ),
                            padding=ft.padding.symmetric(horizontal=20, vertical=10)
                        ),
                        
                        # Recent Section
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Icon(
                                                ft.Icons.HISTORY,
                                                color="white",
                                                size=18
                                            ),
                                            ft.Text(
                                                "Recent",
                                                color="white",
                                                size=16,
                                                weight=ft.FontWeight.W_500
                                            )
                                        ],
                                        spacing=8,
                                        alignment=ft.MainAxisAlignment.CENTER
                                    ),
                                    ft.Divider(color="white30", height=20),
                                    ft.Text(
                                        "No recent visits",
                                        color="white70",
                                        size=14,
                                        italic=True,
                                        text_align=ft.TextAlign.CENTER
                                    )
                                ],
                                spacing=10,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER
                            ),
                            padding=ft.padding.symmetric(horizontal=30, vertical=20)
                        ),
                        
                        # Spacer
                        ft.Container(expand=True),
                        
                        # Location Toggle and AR Mode Section (Hidden by default)
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    # Location Toggle
                                    ft.Container(
                                        content=ft.Row(
                                            controls=[
                                                ft.Container(
                                                    content=ft.Text(
                                                        "My Location",
                                                        color="#041E42",
                                                        size=14,
                                                        weight=ft.FontWeight.BOLD
                                                    ),
                                                    bgcolor="white",
                                                    border_radius=20,
                                                    padding=ft.padding.symmetric(horizontal=20, vertical=10)
                                                ),
                                                ft.Icon(
                                                    ft.Icons.ARROW_FORWARD,
                                                    color="white",
                                                    size=20
                                                ),
                                                ft.Container(
                                                    content=ft.Text(
                                                        "College of\nComputer Studies",
                                                        color="white",
                                                        size=12,
                                                        weight=ft.FontWeight.BOLD,
                                                        text_align=ft.TextAlign.CENTER
                                                    ),
                                                    border=ft.border.all(2, "white"),
                                                    border_radius=20,
                                                    padding=ft.padding.symmetric(horizontal=15, vertical=8)
                                                )
                                            ],
                                            alignment=ft.MainAxisAlignment.CENTER,
                                            spacing=15
                                        ),
                                        padding=ft.padding.only(bottom=20)
                                    ),
                                    
                                    # AR Mode Button
                                    ft.ElevatedButton(
                                        content=ft.Container(
                                            content=ft.Text(
                                                "View AR Mode",
                                                size=16,
                                                weight=ft.FontWeight.BOLD,
                                                color="#041E42"
                                            ),
                                            padding=ft.padding.symmetric(horizontal=80, vertical=12)
                                        ),
                                        style=ft.ButtonStyle(
                                            bgcolor="white",
                                            shape=ft.RoundedRectangleBorder(radius=25)
                                        ),
                                        on_click=on_ar_mode_click
                                    )
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=0
                            ),
                            padding=ft.padding.only(bottom=40),
                            visible=False
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
