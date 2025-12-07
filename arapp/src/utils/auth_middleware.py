"""
Authentication Middleware for Role-Based Access Control
Provides decorators and functions to restrict route access based on user roles
"""
import flet as ft
from functools import wraps

def get_user_role(page: ft.Page):
    """
    Get the role of the currently logged-in user
    
    Args:
        page: Flet Page object
        
    Returns:
        str: User role (Admin, CSPCean, Visitor) or None if not logged in
    """
    user_email = page.client_storage.get("logged_in_user")
    
    if not user_email:
        return None
    
    try:
        from database.db import supabase
        response = supabase.table("users").select("role").eq("email", user_email).execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]["role"]
    except Exception as e:
        print(f"Error getting user role: {e}")
    
    return None

def require_login(view_func):
    """
    Decorator to require user to be logged in
    Redirects to login page if not authenticated
    
    Usage:
        @require_login
        def MyView(page: ft.Page):
            return ft.View(...)
    """
    @wraps(view_func)
    def wrapper(page: ft.Page):
        user_email = page.client_storage.get("logged_in_user")
        
        if not user_email:
            # Not logged in - redirect to login
            page.go("/login_signup")
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Please login to access this page"),
                bgcolor="red"
            )
            page.snack_bar.open = True
            page.update()
            return ft.View("/login_signup", controls=[])
        
        # User is logged in - proceed to view
        return view_func(page)
    
    return wrapper

def require_role(allowed_roles):
    """
    Decorator to restrict route access based on user role
    Redirects unauthorized users to appropriate page
    
    Args:
        allowed_roles: List of roles that can access this route (e.g., ["Admin"])
        
    Usage:
        @require_role(["Admin"])
        def DashboardView(page: ft.Page):
            return ft.View(...)
            
        @require_role(["CSPCean", "Visitor"])
        def HomeView(page: ft.Page):
            return ft.View(...)
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(page: ft.Page):
            user_email = page.client_storage.get("logged_in_user")
            
            # Check if user is logged in
            if not user_email:
                page.go("/login_signup")
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Please login to access this page"),
                    bgcolor="red"
                )
                page.snack_bar.open = True
                page.update()
                return ft.View("/login_signup", controls=[])
            
            # Get user role
            user_role = get_user_role(page)
            
            if not user_role:
                # Error getting role - redirect to login
                page.go("/login_signup")
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Session error. Please login again."),
                    bgcolor="red"
                )
                page.snack_bar.open = True
                page.update()
                return ft.View("/login_signup", controls=[])
            
            # Check if user role is allowed
            if user_role not in allowed_roles:
                # Unauthorized - redirect based on their actual role
                if user_role == "Admin":
                    page.go("/dashboard")
                else:
                    page.go("/home")
                
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("You don't have permission to access this page"),
                    bgcolor="red"
                )
                page.snack_bar.open = True
                page.update()
                return ft.View("/home" if user_role != "Admin" else "/dashboard", controls=[])
            
            # Role is authorized - proceed to view
            return view_func(page)
        
        return wrapper
    return decorator

def check_route_access(page: ft.Page, route: str) -> bool:
    """
    Check if current user has access to a specific route
    
    Args:
        page: Flet Page object
        route: Route path to check (e.g., "/dashboard")
        
    Returns:
        bool: True if user has access, False otherwise
    """
    user_email = page.client_storage.get("logged_in_user")
    
    if not user_email:
        return False
    
    user_role = get_user_role(page)
    
    if not user_role:
        return False
    
    # Define route permissions
    route_permissions = {
        "/dashboard": ["Admin"],
        "/home": ["Admin", "CSPCean", "Visitor"],
        "/settings": ["Admin", "CSPCean", "Visitor"],
        "/ar": ["Admin", "CSPCean", "Visitor"],
    }
    
    allowed_roles = route_permissions.get(route, [])
    
    return user_role in allowed_roles
