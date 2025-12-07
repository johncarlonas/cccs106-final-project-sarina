"""
Database Migration: Add Login Protection Columns
Adds columns to users table for tracking failed login attempts and account lockout
"""
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from database.db import supabase

def migrate_add_login_protection_columns():
    """
    Add login protection columns to users table in Supabase
    
    NOTE: This script shows the SQL you need to run in Supabase SQL Editor
    Supabase doesn't allow ALTER TABLE through the Python client
    """
    
    sql_script = """
-- Migration: Add Login Protection Columns
-- Run this in Supabase SQL Editor: https://app.supabase.com

ALTER TABLE users 
ADD COLUMN IF NOT EXISTS failed_attempts INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS last_failed_attempt TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS locked_until TIMESTAMP WITH TIME ZONE;

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_email_locked ON users(email, locked_until);

-- Verify columns were added
SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_name = 'users'
AND column_name IN ('failed_attempts', 'last_failed_attempt', 'locked_until');
"""
    
    print("=" * 70)
    print("DATABASE MIGRATION: Add Login Protection Columns")
    print("=" * 70)
    print("\nRun the following SQL in your Supabase SQL Editor:")
    print("Go to: https://app.supabase.com → Your Project → SQL Editor\n")
    print("-" * 70)
    print(sql_script)
    print("-" * 70)
    print("\nAfter running the SQL, the following columns will be added:")
    print("  • failed_attempts (INTEGER) - Counter for failed login attempts")
    print("  • last_failed_attempt (TIMESTAMP) - Time of last failed attempt")
    print("  • locked_until (TIMESTAMP) - When account lock expires")
    print("\n" + "=" * 70)

if __name__ == "__main__":
    migrate_add_login_protection_columns()
