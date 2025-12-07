import sqlite3
from datetime import datetime, timedelta
import random
import os

# Get the database path
DB_PATH = os.path.join(os.path.dirname(__file__), '../../storage/data/sarina.db')

def init_database():
    """Initialize the database with tables and dummy data"""
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL,
            last_login TIMESTAMP
        )
    ''')
    
    # Create app_usage table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS app_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            search_query TEXT NOT NULL,
            destination TEXT NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            duration_seconds INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create location_visits table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS location_visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location_name TEXT UNIQUE NOT NULL,
            visit_count INTEGER DEFAULT 0,
            last_visited TIMESTAMP
        )
    ''')
    
    # Check if data already exists
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] > 0:
        print("Database already has data. Skipping initialization.")
        conn.close()
        return
    
    # Insert dummy users
    users = [
        ("Juan Dela Cruz", "juan@cspc.edu.ph", "hashed_password1", "Student", "2024-09-01", "2024-12-04"),
        ("Maria Santos", "maria@cspc.edu.ph", "hashed_password2", "Student", "2024-09-05", "2024-12-03"),
        ("Pedro Reyes", "pedro@gmail.com", "hashed_password3", "Visitor", "2024-10-12", "2024-12-02"),
        ("Ana Garcia", "ana@cspc.edu.ph", "hashed_password4", "Student", "2024-09-08", "2024-12-04"),
        ("Carlos Rivera", "carlos@yahoo.com", "hashed_password5", "Visitor", "2024-11-20", "2024-12-01"),
        ("Lisa Torres", "lisa@cspc.edu.ph", "hashed_password6", "Student", "2024-09-15", "2024-12-04"),
        ("Miguel Santos", "miguel@cspc.edu.ph", "hashed_password7", "Student", "2024-10-01", "2024-11-30"),
        ("Rosa Lim", "rosa@gmail.com", "hashed_password8", "Visitor", "2024-11-05", "2024-12-03"),
        ("Jose Gomez", "jose@cspc.edu.ph", "hashed_password9", "Student", "2024-09-20", "2024-12-04"),
        ("Elena Cruz", "elena@cspc.edu.ph", "hashed_password10", "Student", "2024-09-10", "2024-12-02"),
        ("David Tan", "david@cspc.edu.ph", "hashed_password11", "Student", "2024-11-15", "2024-12-03"),
        ("Sarah Lee", "sarah@gmail.com", "hashed_password12", "Visitor", "2024-11-25", "2024-12-04"),
        ("Admin Carlo", "admin@cspc.edu.ph", "admin_password", "Admin", "2024-08-01", "2024-12-05"),
    ]
    
    cursor.executemany('''
        INSERT INTO users (name, email, password, role, created_at, last_login)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', users)
    
    # Insert location visits
    locations = [
        ("CSPC Library", 456, "2024-12-04 15:30:00"),
        ("Canteen", 342, "2024-12-04 12:15:00"),
        ("College of Computer Studies", 289, "2024-12-04 14:20:00"),
        ("Gymnasium", 178, "2024-12-03 16:45:00"),
        ("Chapel", 145, "2024-12-04 08:30:00"),
        ("College of Engineering", 198, "2024-12-04 10:15:00"),
        ("Admin Building", 234, "2024-12-04 11:00:00"),
        ("Science Laboratory", 167, "2024-12-03 13:20:00"),
        ("Parking Lot", 123, "2024-12-04 07:45:00"),
    ]
    
    cursor.executemany('''
        INSERT INTO location_visits (location_name, visit_count, last_visited)
        VALUES (?, ?, ?)
    ''', locations)
    
    # Generate app usage for past 7 days
    location_names = [loc[0] for loc in locations]
    base_date = datetime(2024, 12, 5)
    
    app_usage_records = []
    for day_offset in range(7):
        date = base_date - timedelta(days=day_offset)
        daily_searches = random.randint(8, 15)
        
        for _ in range(daily_searches):
            user_id = random.randint(1, 12)  # Exclude admin
            search_query = random.choice(location_names)
            destination = random.choice(location_names)
            
            # Peak hours: 2PM-4PM
            if random.random() < 0.4:
                hour = random.randint(14, 15)
            else:
                hour = random.randint(7, 17)
            
            timestamp = date.replace(hour=hour, minute=random.randint(0, 59))
            duration = random.randint(60, 300)
            
            app_usage_records.append((
                user_id,
                search_query,
                destination,
                timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                duration
            ))
    
    cursor.executemany('''
        INSERT INTO app_usage (user_id, search_query, destination, timestamp, duration_seconds)
        VALUES (?, ?, ?, ?, ?)
    ''', app_usage_records)
    
    conn.commit()
    conn.close()
    print(f"Database initialized successfully at {DB_PATH}")

if __name__ == "__main__":
    init_database()
