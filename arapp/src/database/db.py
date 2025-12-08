import os
import sys
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.password_hashing import PasswordHasher

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_all_users():
    """Get all users except admin"""
    try:
        response = supabase.table("users").select("*").neq("role", "Admin").order("last_login", desc=True).execute()
        return response.data
    except Exception as e:
        print(f"Error fetching users: {e}")
        return []

def get_analytics():
    """Get analytics summary"""
    try:
        # Total users (excluding admin)
        total_users_response = supabase.table("users").select("id", count="exact").neq("role", "Admin").execute()
        total_users = total_users_response.count
        
        # New users this month (December 2025)
        new_users_response = supabase.table("users").select("id", count="exact").neq("role", "Admin").gte("created_at", "2025-12-01").execute()
        new_users_this_month = new_users_response.count
        
        # Visitor percentage
        visitor_response = supabase.table("users").select("id", count="exact").eq("role", "Visitor").execute()
        visitor_count = visitor_response.count
        visitor_percentage = round((visitor_count / total_users) * 100) if total_users > 0 else 0
        
        # Daily usage (today)
        today = datetime.now().strftime('%Y-%m-%d')
        daily_usage_response = supabase.table("app_usage").select("id", count="exact").gte("timestamp", today).lt("timestamp", f"{today}T23:59:59").execute()
        daily_usage = daily_usage_response.count
        
        # Most visited place (from app_usage destination)
        app_usage_data = supabase.table("app_usage").select("destination").not_.is_("destination", "null").execute()
        destination_counts = {}
        for record in app_usage_data.data:
            dest = record.get("destination")
            if dest:
                destination_counts[dest] = destination_counts.get(dest, 0) + 1
        
        most_visited_place = "N/A"
        most_visited_count = 0
        if destination_counts:
            most_visited_place = max(destination_counts, key=destination_counts.get)
            most_visited_count = destination_counts[most_visited_place]
        
        # Peak usage hours
        usage_data = supabase.table("app_usage").select("timestamp").execute()
        hour_counts = {}
        for record in usage_data.data:
            timestamp = record.get("timestamp")
            if timestamp:
                hour = datetime.fromisoformat(timestamp.replace('Z', '+00:00')).hour
                hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        peak_usage_hours = "N/A"
        if hour_counts:
            peak_hour = max(hour_counts, key=hour_counts.get)
            end_hour = (peak_hour + 2) % 24
            peak_usage_hours = f"{peak_hour}:00 {'PM' if peak_hour >= 12 else 'AM'} - {end_hour}:00 {'PM' if end_hour >= 12 else 'AM'}"
        
        return {
            "total_users": total_users,
            "new_users_this_month": new_users_this_month,
            "visitor_percentage": visitor_percentage,
            "daily_usage": daily_usage,
            "most_visited_place": most_visited_place,
            "most_visited_count": most_visited_count,
            "peak_usage_hours": peak_usage_hours
        }
    except Exception as e:
        print(f"Error fetching analytics: {e}")
        return {
            "total_users": 0,
            "new_users_this_month": 0,
            "visitor_percentage": 0,
            "daily_usage": 0,
            "most_visited_place": "N/A",
            "most_visited_count": 0,
            "peak_usage_hours": "N/A"
        }

def get_weekly_search_trend():
    """Get search trend for the past 7 days"""
    try:
        # Get app usage data for last 7 days
        from datetime import timedelta
        today = datetime.now()
        week_ago = (today - timedelta(days=6)).strftime('%Y-%m-%d')
        
        usage_data = supabase.table("app_usage").select("timestamp").gte("timestamp", week_ago).execute()
        
        # Group by day
        day_counts = {}
        for record in usage_data.data:
            timestamp = record.get("timestamp")
            if timestamp:
                date_obj = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                day_name = date_obj.strftime('%a')  # Mon, Tue, Wed...
                day_counts[day_name] = day_counts.get(day_name, 0) + 1
        
        # Create trend with all 7 days
        days_order = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        trend = []
        for day in days_order:
            trend.append({"day": day, "searches": day_counts.get(day, 0)})
        
        return trend
    except Exception as e:
        print(f"Error fetching weekly trend: {e}")
        return [{"day": day, "searches": 0} for day in ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]]

def add_user(name, email, password, role):
    """Add a new user"""
    try:
        # Hash password before storing
        hashed_password = PasswordHasher.hash_password(password)
        
        created_at = datetime.now().isoformat()
        data = {
            "name": name,
            "email": email,
            "password": hashed_password,
            "role": role,
            "created_at": created_at,
            "last_login": created_at
        }
        response = supabase.table("users").insert(data).execute()
        return response.data[0]["id"] if response.data else None
    except Exception as e:
        print(f"Error adding user: {e}")
        return None

def delete_user(user_id):
    """Delete a user"""
    try:
        supabase.table("users").delete().eq("id", user_id).execute()
    except Exception as e:
        print(f"Error deleting user: {e}")

def update_user(user_id, name, email, role):
    """Update user information"""
    try:
        data = {
            "name": name,
            "email": email,
            "role": role
        }
        supabase.table("users").update(data).eq("id", user_id).execute()
    except Exception as e:
        print(f"Error updating user: {e}")

def check_user_exists(email):
    """Check if a user with the given email exists"""
    try:
        response = supabase.table("users").select("id").eq("email", email).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"Error checking user exists: {e}")
        return False

def verify_user_login(email, password):
    """Verify user login credentials using password hash"""
    try:
        # Get user by email
        response = supabase.table("users").select("*").eq("email", email).execute()
        
        if response.data and len(response.data) > 0:
            user = response.data[0]
            hashed_password = user["password"]
            
            # Verify password using bcrypt
            if PasswordHasher.verify_password(password, hashed_password):
                # Update last login
                user_id = user["id"]
                supabase.table("users").update({"last_login": datetime.now().isoformat()}).eq("id", user_id).execute()
                return True
        
        return False
    except Exception as e:
        print(f"Error verifying login: {e}")
        return False

def update_user_password(email, new_password):
    """Update user password with hashing"""
    try:
        # Hash new password before storing
        hashed_password = PasswordHasher.hash_password(new_password)
        
        response = supabase.table("users").update({"password": hashed_password}).eq("email", email).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"Error updating password: {e}")
        return False
