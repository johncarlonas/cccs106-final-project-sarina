import flet as ft
import json
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ar_navigation.routing import get_route

def HomeView(page: ft.Page):
    # Get current user from session/storage
    user_email = page.session.get("user_email") or page.client_storage.get("logged_in_user")
    
    # Get user data from database
    from database.db import supabase
    user_name = "User"
    
    if user_email:
        try:
            response = supabase.table("users").select("name").eq("email", user_email).execute()
            if response.data and len(response.data) > 0:
                user_name = response.data[0].get("name", "User")
        except Exception as e:
            print(f"Error fetching user data: {e}")
    
    # Load places from places_cache.json
    places_file = os.path.join(os.path.dirname(__file__), "..", "places_cache.json")
    with open(places_file, 'r') as f:
        PLACES = json.load(f)
    
    # Load search history
    history_file = os.path.join(os.path.dirname(__file__), "..", "search_history.json")
    try:
        with open(history_file, 'r') as f:
            content = f.read().strip()
            search_history = json.loads(content) if content else []
    except (FileNotFoundError, json.JSONDecodeError):
        search_history = []
        # Create empty history file if it doesn't exist
        try:
            with open(history_file, 'w') as f:
                json.dump([], f)
        except Exception:
            pass
    
    # State for search text and selected destination
    search_query = ft.Ref[ft.TextField]()
    suggestions_list = ft.Ref[ft.Column]()
    ar_section = ft.Ref[ft.Container]()
    searched_place_text = ft.Ref[ft.Text]()
    recent_section = ft.Ref[ft.Container]()
    recent_list = ft.Ref[ft.Column]()
    
    selected_destination = {"name": None, "coords": None}
    
    def on_search_change(e):
        query = e.control.value.strip().lower()
        
        # When search is cleared, hide AR section and show recent section
        if not query:
            recent_section.current.visible = True
            ar_section.current.visible = False
            suggestions_list.current.visible = False
            # Clear selected destination
            selected_destination["name"] = None
            selected_destination["coords"] = None
        else:
            # When typing, hide recent section
            recent_section.current.visible = False
        
        update_suggestions(query)
    
    def update_suggestions(query):
        suggestions_list.current.controls.clear()
        
        if not query:
            suggestions_list.current.visible = False
            page.update()
            return
        
        # Filter places that match the query
        matching_places = [name for name in PLACES.keys() if query in name.lower()]
        
        if matching_places:
            suggestions_list.current.visible = True
            # Hide AR section when showing suggestions
            ar_section.current.visible = False
            
            for place_name in matching_places[:10]:  # Show max 10 suggestions
                suggestions_list.current.controls.append(
                    ft.Container(
                        content=ft.Text(place_name, color="white", size=14),
                        bgcolor="#80000000",
                        padding=10,
                        border_radius=5,
                        on_click=lambda e, name=place_name: select_place(name)
                    )
                )
        else:
            suggestions_list.current.visible = False
        
        page.update()
    
    def save_to_history(place_name):
        """Save search to history (max 5 entries)"""
        from datetime import datetime
        
        # Remove if already exists
        search_history[:] = [item for item in search_history if item["name"] != place_name]
        
        # Add to beginning
        search_history.insert(0, {
            "name": place_name,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only last 5
        if len(search_history) > 5:
            search_history[:] = search_history[:5]
        
        # Save to file
        try:
            with open(history_file, 'w') as f:
                json.dump(search_history, f, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")
        
        # Update the recent list display
        populate_recent_searches()
    
    def select_place(place_name):
        # Set the selected destination
        selected_destination["name"] = place_name
        selected_destination["coords"] = PLACES[place_name]
        
        # Save to history
        save_to_history(place_name)
        
        # Update search field
        search_query.current.value = place_name
        
        # Hide suggestions and recent section
        suggestions_list.current.visible = False
        recent_section.current.visible = False
        
        # Update searched place text
        searched_place_text.current.value = place_name
        
        # Show AR section
        ar_section.current.visible = True
        
        page.update()
    
    def on_search_click(e):
        query = search_query.current.value.strip()
        if query and query in PLACES:
            select_place(query)
    
    def populate_recent_searches():
        """Populate the recent searches list"""
        recent_list.current.controls.clear()
        
        if not search_history:
            recent_list.current.controls.append(
                ft.Text(
                    "No recent visits",
                    color="white70",
                    size=14,
                    italic=True,
                    text_align=ft.TextAlign.CENTER
                )
            )
        else:
            for item in search_history:
                place_name = item["name"]
                recent_list.current.controls.append(
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Icon(
                                    ft.Icons.LOCATION_ON,
                                    color="white",
                                    size=16
                                ),
                                ft.Text(
                                    place_name,
                                    color="white",
                                    size=14
                                )
                            ],
                            spacing=8
                        ),
                        bgcolor="#80000000",
                        padding=10,
                        border_radius=5,
                        on_click=lambda e, name=place_name: select_place(name)
                    )
                )
        
        page.update()
    
    def on_profile_click(e):
        # Navigate to profile/settings
        page.go("/settings")
    
    def on_ar_mode_click(e):
        # Start AR navigation
        if not selected_destination["name"] or not selected_destination["coords"]:
            page.snack_bar = ft.SnackBar(ft.Text("Please select a destination first"))
            page.snack_bar.open = True
            page.update()
            return
        
        # Get user location
        try:
            loc = page.geolocator.get_geolocation()
            user_lat = loc.latitude
            user_lon = loc.longitude
        except Exception:
            # Fallback location (CSPC campus)
            user_lat, user_lon = 13.405569, 123.374683
        
        # Compute route
        dest_coords = selected_destination["coords"]
        route = get_route((user_lat, user_lon), dest_coords)
        
        # Save route to session and navigate to AR view
        page.session.set("current_route", route)
        page.go("/ar")
    
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
                            padding=ft.padding.only(top=50, left=80, right=20, bottom=5)
                        ),
                        
                        # Greeting Text
                        ft.Container(
                            content=ft.Text(
                                f"Hello, {user_name}!",
                                color="white",
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                text_align=ft.TextAlign.LEFT
                            ),
                            padding=ft.padding.only(left=25, right=20, top=10, bottom=20)
                        ),
                        
                        # Search Bar
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.TextField(
                                                ref=search_query,
                                                hint_text="Where are you going?",
                                                hint_style=ft.TextStyle(color="white70"),
                                                text_style=ft.TextStyle(color="white"),
                                                border_radius=25,
                                                filled=True,
                                                bgcolor="#80000000",
                                                border_color="transparent",
                                                focused_border_color="transparent",
                                                content_padding=ft.padding.symmetric(horizontal=20, vertical=15),
                                                text_vertical_align=ft.VerticalAlignment.CENTER,
                                                expand=True,
                                                on_change=on_search_change,
                                            ),
                                            ft.IconButton(
                                                icon=ft.Icons.SEARCH,
                                                icon_color="white",
                                                icon_size=28,
                                                on_click=on_search_click
                                            )
                                        ],
                                        spacing=10,
                                        vertical_alignment=ft.CrossAxisAlignment.CENTER
                                    ),
                                    # Suggestions list
                                    ft.Column(
                                        ref=suggestions_list,
                                        controls=[],
                                        spacing=5,
                                        visible=False
                                    )
                                ],
                                spacing=10
                            ),
                            padding=ft.padding.symmetric(horizontal=20, vertical=10)
                        ),
                        
                        # Recent Section (Hidden)
                        ft.Container(
                            ref=recent_section,
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
                                    ft.Column(
                                        ref=recent_list,
                                        controls=[],
                                        spacing=8
                                    )
                                ],
                                spacing=10,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER
                            ),
            padding=ft.padding.symmetric(horizontal=30, vertical=20),
                            visible=True
                        ),
                        
                        # Spacer
                        ft.Container(height=50),
                        
                        # Location Toggle and AR Mode Section (Centered)
                        ft.Container(
                            ref=ar_section,
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
                                                        ref=searched_place_text,
                                                        value="Searched Place",
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
                                                color="#002A7A"
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
                            visible=False
                        ),
                        
                        # Bottom spacer
                        ft.Container(expand=True)
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
    
    # Populate recent searches on load
    populate_recent_searches()
    
    return view
