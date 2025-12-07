import flet as ft
from src.database.db import get_all_users, get_analytics, get_weekly_search_trend, delete_user, update_user

def DashboardView(page: ft.Page):
    # Get real data from database
    def refresh_data():
        try:
            users = get_all_users()
            analytics = get_analytics()
            weekly_trend = get_weekly_search_trend()
            return users, analytics, weekly_trend
        except Exception as e:
            print(f"Database error: {e}")
            # Fallback to dummy data if database fails
            # users = [
            #     {"name": "Juan Dela Cruz", "email": "juan@example.com", "role": "Student"},
            #     {"name": "Maria Santos", "email": "maria@example.com", "role": "Student"},
            # ]
            # analytics = {
            #     "total_users": 12,
            #     "new_users_this_month": 2,
            #     "visitor_percentage": 25,
            #     "most_visited_place": "CSPC Library",
            #     "most_visited_count": 456
            # }
            # weekly_trend = [
            #     {"day": "Mon", "searches": 10},
            #     {"day": "Tue", "searches": 12},
            #     {"day": "Wed", "searches": 8},
            #     {"day": "Thu", "searches": 15},
            #     {"day": "Fri", "searches": 11},
            #     {"day": "Sat", "searches": 9},
            #     {"day": "Sun", "searches": 7},
            # ]
            # return users, analytics, weekly_trend
    
    users, analytics, weekly_trend = refresh_data()
    
    # Graph navigation state
    current_week_offset = 0  # 0 = current week, -1 = last week, etc.
    graph_container = ft.Container()
    date_text = ft.Text("", size=14, weight=ft.FontWeight.BOLD, color="#002A7A", text_align=ft.TextAlign.CENTER)
    
    def update_graph(offset=0):
        """Update bar graph with data for the selected week"""
        nonlocal current_week_offset
        current_week_offset = offset
        
        # Get data from database
        from datetime import datetime, timedelta
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday()) + timedelta(weeks=offset)
        
        # Use actual database data
        _, _, weekly_data = refresh_data()
        
        # Create 7 days of data (Sun to Sat)
        days_order = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        data = []
        for i, day_name in enumerate(days_order):
            # Find matching data from database
            day_record = next((d for d in weekly_data if d["day"] == day_name), None)
            searches = day_record["searches"] if day_record else 0
            data.append({"day": day_name, "searches": searches})
        
        week_end = week_start + timedelta(days=6)
        date_text.value = f"{week_start.strftime('%b %d')} - {week_end.strftime('%b %d')}"
        
        # Create bar chart
        max_value = max([d["searches"] for d in data]) if data and max([d["searches"] for d in data]) > 0 else 1
        bars = []
        
        for day_data in data:
            bar_height = (day_data["searches"] / max_value) * 80 if max_value > 0 else 0
            bars.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                str(day_data["searches"]),
                                size=10,
                                color="#002A7A",
                                weight=ft.FontWeight.BOLD
                            ),
                            ft.Container(
                                bgcolor="#002A7A",
                                width=35,
                                height=bar_height,
                                border_radius=ft.border_radius.only(top_left=5, top_right=5)
                            ),
                            ft.Text(
                                day_data["day"],
                                size=11,
                                color="#002A7A",
                                weight=ft.FontWeight.BOLD
                            )
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=2,
                        alignment=ft.MainAxisAlignment.END
                    ),
                    width=40,
                    height=120
                )
            )
        
        graph_container.content = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK_IOS,
                            icon_color="#002A7A",
                            icon_size=20,
                            on_click=lambda e: [update_graph(current_week_offset - 1), page.update()]
                        ),
                        ft.Container(
                            content=date_text,
                            expand=True
                        ),
                        ft.IconButton(
                            icon=ft.Icons.ARROW_FORWARD_IOS,
                            icon_color="#002A7A" if current_week_offset < 0 else "#CCCCCC",
                            icon_size=20,
                            on_click=lambda e: [update_graph(current_week_offset + 1), page.update()] if current_week_offset < 0 else None,
                            disabled=current_week_offset >= 0
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                ft.Container(height=5),
                ft.Row(
                    controls=bars,
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                    spacing=2
                )
            ],
            spacing=0
        )
    
    # Initialize graph
    update_graph(0)
    
    def show_success_modal(message):
        success_modal = ft.AlertDialog(
            title=ft.Text("Success", color="black", weight=ft.FontWeight.BOLD),
            content=ft.Text(message, color="black"),
            actions=[
                ft.TextButton(
                    "OK",
                    on_click=lambda e: page.close(success_modal),
                    style=ft.ButtonStyle(color="#002A7A")
                )
            ],
            bgcolor="white"
        )
        page.open(success_modal)
        page.update()
    
    def delete_user_action(user):
        def confirm_delete(e):
            page.close(confirm_modal)
            
            try:
                delete_user(user["id"])
                page.go("/dashboard")
                
                # Then show success modal
                show_success_modal(f"{user['name']} has been successfully removed from the system.")
            except Exception as ex:
                show_success_modal(f"Error: Unable to delete user. {str(ex)}")
        
        def cancel_delete(e):
            page.close(confirm_modal)
        
        confirm_modal = ft.AlertDialog(
            title=ft.Text("Confirm Deletion", color="black", weight=ft.FontWeight.BOLD),
            content=ft.Text(
                f"Are you sure you want to remove {user['name']} from the system?",
                color="black"
            ),
            actions=[
                ft.TextButton(
                    "Cancel",
                    on_click=cancel_delete,
                    style=ft.ButtonStyle(color="#002A7A")
                ),
                ft.TextButton(
                    "Confirm",
                    on_click=confirm_delete,
                    style=ft.ButtonStyle(color="#002A7A")
                )
            ],
            bgcolor="white"
        )
        page.open(confirm_modal)
    
    def set_as_admin_action(user):
        def confirm_admin(e):
            page.close(confirm_modal)
            
            try:
                update_user(user["id"], user["name"], user["email"], "Admin")
                # Refresh the list - like display_contacts() in contact book
                display_users()
                
                # Then show success modal
                show_success_modal(f"{user['name']} has been granted administrator privileges.")
            except Exception as ex:
                show_success_modal(f"Error: Unable to update user role. {str(ex)}")
        
        def cancel_admin(e):
            page.close(confirm_modal)
        
        confirm_modal = ft.AlertDialog(
            title=ft.Text("Confirm Admin Assignment", color="black", weight=ft.FontWeight.BOLD),
            content=ft.Text(
                f"Are you sure you want to grant administrator privileges to {user['name']}?",
                color="black"
            ),
            actions=[
                ft.TextButton(
                    "Cancel",
                    on_click=cancel_admin,
                    style=ft.ButtonStyle(color="#002A7A")
                ),
                ft.TextButton(
                    "Confirm",
                    on_click=confirm_admin,
                    style=ft.ButtonStyle(color="#002A7A")
                )
            ],
            bgcolor="white"
        )
        page.open(confirm_modal)
    
    def on_logout(e):
        page.go("/login")
    
    # Create user list container that will be updated
    user_list_column = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=8)
    
    # Filter state for users
    current_filter = "All"
    
    # Create analytics containers that will be updated
    total_users_text = ft.Text(str(analytics["total_users"]), size=25, weight=ft.FontWeight.BOLD, color="#002A7A")
    new_users_text = ft.Text(str(analytics["new_users_this_month"]), size=25, weight=ft.FontWeight.BOLD, color="#002A7A")
    visitor_percentage_text = ft.Text(f"{analytics['visitor_percentage']}%", size=25, weight=ft.FontWeight.BOLD, color="#002A7A")
    most_visited_place_text = ft.Text(analytics["most_visited_place"], size=16, weight=ft.FontWeight.BOLD, color="#002A7A", text_align=ft.TextAlign.CENTER)
    
    def display_users(filter_role=None):
        """Refresh user list from database - like display_contacts() in contact book"""
        user_list_column.controls.clear()
        fresh_users, fresh_analytics, _ = refresh_data()
        
        # Update analytics
        total_users_text.value = str(fresh_analytics["total_users"])
        new_users_text.value = str(fresh_analytics["new_users_this_month"])
        visitor_percentage_text.value = f"{fresh_analytics['visitor_percentage']}%"
        most_visited_place_text.value = fresh_analytics["most_visited_place"]
        
        # Apply filter
        if filter_role == "CSPCean":
            fresh_users = [u for u in fresh_users if u["role"] == "CSPCean"]
        elif filter_role == "Visitor":
            fresh_users = [u for u in fresh_users if u["role"] == "Visitor"]
        
        # Rebuild user list
        for user in fresh_users:
            popup_menu = ft.PopupMenuButton(
                icon=ft.Icons.MORE_VERT,
                icon_color="#002A7A",
                items=[
                    ft.PopupMenuItem(
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.DELETE_OUTLINE, size=18),
                                ft.Container(width=8),
                                ft.Text("Delete", size=14),
                            ],
                            spacing=0
                        ),
                        on_click=lambda e, u=user: delete_user_action(u)
                    ),
                    ft.PopupMenuItem(
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.ADMIN_PANEL_SETTINGS_OUTLINED, size=18),
                                ft.Container(width=8),
                                ft.Text("Set as Admin", size=14),
                            ],
                            spacing=0
                        ),
                        on_click=lambda e, u=user: set_as_admin_action(u)
                    ),
                ],
            )
            
            user_list_column.controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.ACCOUNT_CIRCLE, color="#002A7A", size=35),
                            ft.Container(width=10),
                            ft.Column(
                                controls=[
                                    ft.Text(user["name"], size=15, weight=ft.FontWeight.BOLD, color="#002A7A"),
                                    ft.Text(user["role"], size=12, color="#002A7A"),
                                ],
                                spacing=2,
                                expand=True
                            ),
                            popup_menu
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    bgcolor="white",
                    border_radius=15,
                    padding=ft.padding.symmetric(horizontal=20, vertical=12)
                )
            )
        page.update()
    
    def on_filter_change(e):
        """Handle radio button filter change"""
        nonlocal current_filter
        current_filter = e.control.value
        if current_filter == "All":
            display_users()
        elif current_filter == "CSPCeans":
            display_users("CSPCean")
        elif current_filter == "Visitors":
            display_users("Visitor")
    
    # Initial display of users
    display_users()
    
    def delete_user_action(user):
        def confirm_delete(e):
            page.close(confirm_modal)
            
            try:
                delete_user(user["id"])
                # Refresh the list - like display_contacts() in contact book
                display_users()
                
                # Then show success modal
                show_success_modal(f"{user['name']} has been successfully removed from the system.")
            except Exception as ex:
                show_success_modal(f"Error: Unable to delete user. {str(ex)}")
        
        def cancel_delete(e):
            page.close(confirm_modal)
        
        confirm_modal = ft.AlertDialog(
            title=ft.Text("Confirm Deletion", color="black", weight=ft.FontWeight.BOLD),
            content=ft.Text(
                f"Are you sure you want to remove {user['name']} from the system?",
                color="black"
            ),
            actions=[
                ft.TextButton(
                    "Cancel",
                    on_click=cancel_delete,
                    style=ft.ButtonStyle(color="#002A7A")
                ),
                ft.TextButton(
                    "Confirm",
                    on_click=confirm_delete,
                    style=ft.ButtonStyle(color="#002A7A")
                )
            ],
            bgcolor="white"
        )
        page.open(confirm_modal)
    
    def set_as_admin_action(user):
        def confirm_admin(e):
            page.close(confirm_modal)
            
            try:
                update_user(user["id"], user["name"], user["email"], "Admin")
                # Refresh the list - like display_contacts() in contact book
                display_users()
                
                # Then show success modal
                show_success_modal(f"{user['name']} has been granted administrator privileges.")
            except Exception as ex:
                show_success_modal(f"Error: Unable to update user role. {str(ex)}")
        
        def cancel_admin(e):
            page.close(confirm_modal)
        
        confirm_modal = ft.AlertDialog(
            title=ft.Text("Confirm Admin Assignment", color="black", weight=ft.FontWeight.BOLD),
            content=ft.Text(
                f"Are you sure you want to grant administrator privileges to {user['name']}?",
                color="black"
            ),
            actions=[
                ft.TextButton(
                    "Cancel",
                    on_click=cancel_admin,
                    style=ft.ButtonStyle(color="#002A7A")
                ),
                ft.TextButton(
                    "Confirm",
                    on_click=confirm_admin,
                    style=ft.ButtonStyle(color="#002A7A")
                )
            ],
            bgcolor="white"
        )
        page.open(confirm_modal)
    
    # Tab switching state
    users_container = ft.Container()
    analytics_container = ft.Container()
    users_button = ft.Container()
    analytics_button = ft.Container()
    
    def switch_to_users(e):
        users_button.bgcolor = "white"
        users_button.content.color = "#002A7A"
        analytics_button.bgcolor = "transparent"
        analytics_button.content.color = "white"
        users_container.visible = True
        analytics_container.visible = False
        page.update()
    
    def switch_to_analytics(e):
        analytics_button.bgcolor = "white"
        analytics_button.content.color = "#002A7A"
        users_button.bgcolor = "transparent"
        users_button.content.color = "white"
        analytics_container.visible = True
        users_container.visible = False
        page.update()
    
    # Configure tab buttons
    users_button = ft.Container(
        content=ft.Text("Users", size=16, weight=ft.FontWeight.BOLD, color="#002A7A"),
        bgcolor="white",
        border_radius=20,
        padding=ft.padding.symmetric(horizontal=40, vertical=10),
        on_click=switch_to_users
    )
    
    analytics_button = ft.Container(
        content=ft.Text("Analytics", size=16, weight=ft.FontWeight.BOLD, color="white"),
        bgcolor="transparent",
        border_radius=20,
        padding=ft.padding.symmetric(horizontal=23, vertical=10),
        on_click=switch_to_analytics
    )
    
    # Users content
    users_container = ft.Container(
        content=ft.Column(
            controls=[
                # Radio button filters
                ft.Container(
                    content=ft.RadioGroup(
                        content=ft.Row(
                            controls=[
                                ft.Radio(
                                    value="All",
                                    label="All",
                                    fill_color="white",
                                    label_style=ft.TextStyle(color="white", size=14)
                                ),
                                ft.Radio(
                                    value="CSPCeans",
                                    label="CSPCeans",
                                    fill_color="white",
                                    label_style=ft.TextStyle(color="white", size=14)
                                ),
                                ft.Radio(
                                    value="Visitors",
                                    label="Visitors",
                                    fill_color="white",
                                    label_style=ft.TextStyle(color="white", size=14)
                                )
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=5
                        ),
                        value="All",
                        on_change=on_filter_change
                    ),
                    padding=ft.padding.only(bottom=15)
                ),
                # User list
                ft.Container(
                    content=user_list_column,
                    expand=True
                )
            ],
            expand=True
        ),
        padding=ft.padding.symmetric(horizontal=20, vertical=15),
        visible=True,
        expand=True
    )
    
    # Analytics content
    analytics_container = ft.Container(
        content=ft.Column(
            controls=[
                # Top row - Total users and New users
                ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text("Total number of\nusers", size=13, color="#002A7A", weight=ft.FontWeight.W_500, text_align=ft.TextAlign.CENTER),
                                    ft.Container(height=5),
                                    total_users_text,
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=0,
                                alignment=ft.MainAxisAlignment.CENTER
                            ),
                            bgcolor="white",
                            border_radius=15,
                            padding=15,
                            height=100,
                            expand=1
                        ),
                        ft.Container(width=10),
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text("New users this\nmonth", size=13, color="#002A7A", weight=ft.FontWeight.W_500, text_align=ft.TextAlign.CENTER),
                                    ft.Container(height=5),
                                    new_users_text,
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=0,
                                alignment=ft.MainAxisAlignment.CENTER
                            ),
                            bgcolor="white",
                            border_radius=15,
                            padding=15,
                            height=100,
                            expand=1
                        ),
                    ],
                    spacing=0
                ),
                
                ft.Container(height=10),
                
                # Second row - Visitor percentage and Most visited
                ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text("No. of Visitor\nPercentage", size=13, color="#002A7A", weight=ft.FontWeight.W_500, text_align=ft.TextAlign.CENTER),
                                    ft.Container(height=5),
                                    visitor_percentage_text,
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=0,
                                alignment=ft.MainAxisAlignment.CENTER
                            ),
                            bgcolor="white",
                            border_radius=15,
                            padding=15,
                            height=100,
                            expand=1
                        ),
                        ft.Container(width=10),
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text("Most visited\nplace", size=13, color="#002A7A", weight=ft.FontWeight.W_500, text_align=ft.TextAlign.CENTER),
                                    ft.Container(height=5),
                                    most_visited_place_text,
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=0,
                                alignment=ft.MainAxisAlignment.CENTER
                            ),
                            bgcolor="white",
                            border_radius=15,
                            padding=15,
                            height=100,
                            expand=1
                        ),
                    ],
                    spacing=0
                ),
                
                ft.Container(height=15),
                
                # Bar graph with navigation
                ft.Container(
                    content=graph_container,
                    bgcolor="white",
                    border_radius=15,
                    padding=20,
                    height=200
                )
            ],
            spacing=0,
            expand=True,
            scroll=ft.ScrollMode.AUTO
        ),
        padding=ft.padding.symmetric(horizontal=20, vertical=15),
        visible=False,
        expand=True
    )
    
    view = ft.View(
        "/dashboard",
        controls=[
            ft.Container(
                content=ft.Column(
                    controls=[
                        # Header with Logo and Logout
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Container(height=10),
                                    # Logo and Logout row
                                    ft.Row(
                                        controls=[
                                            ft.Container(expand=True),
                                            ft.Container(
                                                content=ft.Image(
                                                    src="sarina_logo.png",
                                                    width=120,
                                                    fit=ft.ImageFit.CONTAIN
                                                ),
                                                margin=ft.margin.only(left=44)
                                            ),
                                            ft.Container(expand=True),
                                            ft.Container(
                                                content=ft.IconButton(
                                                    icon=ft.Icons.LOGOUT,
                                                    icon_color="white",
                                                    icon_size=30,
                                                    on_click=on_logout
                                                ),
                                                margin=ft.margin.only(right=10)
                                            )
                                        ],
                                        vertical_alignment=ft.CrossAxisAlignment.CENTER
                                    ),
                                    ft.Container(height=15),
                                    # Greeting text (left-aligned)
                                    ft.Text(
                                        "Hello, Carlo (Admin)!",
                                        size=20,
                                        weight=ft.FontWeight.BOLD,
                                        color="white"
                                    )
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.START,
                                spacing=0
                            ),
                            padding=ft.padding.only(top=40, left=20, right=10, bottom=15),
                            bgcolor="#002A7A"
                        ),
                        
                        # Tab Navigation
                        ft.Container(
                            content=ft.Container(
                                content=ft.Row(
                                    controls=[
                                        users_button,
                                        ft.Container(width=15),
                                        analytics_button
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER
                                ),
                                bgcolor="#80000000",  # Black with 50% opacity
                                border_radius=25,
                                padding=ft.padding.symmetric(horizontal=8, vertical=8)
                            ),
                            padding=ft.padding.only(left=40, right=40, top=5, bottom=10),
                            bgcolor="#002A7A"
                        ),
                        
                        # Content Area (Users or Analytics)
                        ft.Container(
                            content=ft.Stack(
                                controls=[
                                    users_container,
                                    analytics_container
                                ]
                            ),
                            bgcolor="#002A7A",
                            expand=True
                        )
                    ],
                    spacing=0,
                    expand=True
                ),
                expand=True
            )
        ],
        padding=0,
        bgcolor="#002A7A"
    )
    
    return view

