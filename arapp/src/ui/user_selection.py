import flet as ft

def UserSelectionView(page: ft.Page):
    # State to track which option is selected
    selected_option = {"value": None}
    
    # References for the cards
    cspcean_card_ref = ft.Ref[ft.Container]()
    visitor_card_ref = ft.Ref[ft.Container]()
    continue_button_ref = ft.Ref[ft.Container]()
    
    def update_cards():
        """Update the appearance of both cards based on selection"""
        # Update CSPCean card
        is_cspcean_selected = selected_option["value"] == "cspcean"
        cspcean_card_ref.current.bgcolor = "white" if is_cspcean_selected else "transparent"
        cspcean_card_ref.current.content.controls[0].color = "#002A7A" if is_cspcean_selected else "white"  # Icon
        cspcean_card_ref.current.content.controls[1].color = "#002A7A" if is_cspcean_selected else "white"  # Title
        cspcean_card_ref.current.content.controls[2].color = "#002A7A" if is_cspcean_selected else "white"  # Subtitle
        
        # Update Visitor card
        is_visitor_selected = selected_option["value"] == "visitor"
        visitor_card_ref.current.bgcolor = "white" if is_visitor_selected else "transparent"
        visitor_card_ref.current.content.controls[0].color = "#002A7A" if is_visitor_selected else "white"  
        visitor_card_ref.current.content.controls[1].color = "#002A7A" if is_visitor_selected else "white"  
        visitor_card_ref.current.content.controls[2].color = "#002A7A" if is_visitor_selected else "white"  
        
        # Show/hide continue button
        continue_button_ref.current.visible = selected_option["value"] is not None
        
        page.update()
    
    def on_cspcean_click(e):
        selected_option["value"] = "cspcean"
        update_cards()
    
    def on_visitor_click(e):
        selected_option["value"] = "visitor"
        update_cards()
    
    def on_continue_click(e):
        if selected_option["value"]:
            page.go("/home")
    
    # CSPCean card
    cspcean_card = ft.Container(
        ref=cspcean_card_ref,
        content=ft.Column(
            controls=[
                ft.Icon(
                    ft.Icons.SCHOOL_ROUNDED,
                    size=70,
                    color="white"
                ),
                ft.Text(
                    "CSPCean",
                    size=22,
                    weight=ft.FontWeight.BOLD,
                    color="white"
                ),
                ft.Text(
                    "Student/Faculty/\nStaff/Alumni",
                    size=13,
                    color="white",
                    text_align=ft.TextAlign.CENTER
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8
        ),
        width=150,
        height=180,
        border=ft.border.all(3, "white"),
        border_radius=15,
        bgcolor="transparent",
        padding=15,
        on_click=on_cspcean_click,
    )
    
    # Visitor card
    visitor_card = ft.Container(
        ref=visitor_card_ref,
        content=ft.Column(
            controls=[
                ft.Icon(
                    ft.Icons.DIRECTIONS_WALK_ROUNDED,
                    size=70,
                    color="white"
                ),
                ft.Text(
                    "Visitor",
                    size=22,
                    weight=ft.FontWeight.BOLD,
                    color="white"
                ),
                ft.Text(
                    "Parent/Guardian/\nGuest/etc.",
                    size=13,
                    color="white",
                    text_align=ft.TextAlign.CENTER
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8
        ),
        width=150,
        height=180,
        border=ft.border.all(3, "white"),
        border_radius=15,
        bgcolor="transparent",
        padding=15,
        on_click=on_visitor_click,
    )
    
    return ft.View(
        "/user_selection",
        controls=[
            ft.Container(
                content=ft.Column(
                    controls=[
                        # Logo
                        ft.Container(
                            content=ft.Image(
                                src="sarina_logo.png",
                                width=200,
                                fit=ft.ImageFit.CONTAIN
                            ),
                            alignment=ft.alignment.center,
                            padding=ft.padding.only(top=40, bottom=80)
                        ),
                        # "I am a..." text
                        ft.Text(
                            "I am a...",
                            size=26,
                            color="white",
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Container(height=30),
                        # Selection cards
                        ft.Row(
                            controls=[cspcean_card, visitor_card],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=25
                        ),
                        # Spacer to push button to bottom
                        ft.Container(expand=True),
                        # Continue button (only visible when option selected)
                        ft.Container(
                            ref=continue_button_ref,
                            content=ft.ElevatedButton(
                                content=ft.Container(
                                    content=ft.Text(
                                        "Continue",
                                        size=18,
                                        weight=ft.FontWeight.BOLD,
                                        color="#002A7A"
                                    ),
                                    padding=ft.padding.symmetric(horizontal=120, vertical=15),
                                ),
                                style=ft.ButtonStyle(
                                    bgcolor="white",
                                    shape=ft.RoundedRectangleBorder(radius=30),
                                ),
                                on_click=on_continue_click,
                            ),
                            alignment=ft.alignment.center,
                            padding=ft.padding.only(bottom=30),
                            visible=False
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=0
                ),
                bgcolor="#002A7A",
                expand=True,
                padding=20
            )
        ],
        padding=0,
        bgcolor="#002A7A"
    )
