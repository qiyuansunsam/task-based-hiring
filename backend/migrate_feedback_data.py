#!/usr/bin/env python3
"""
Migration script to fix feedback data formatting issues
"""
import sqlite3
import json
import sys
import os

def migrate_feedback_data():
    """Fix any malformed feedback data in the database"""
    db_path = 'tasks.db'
    
    if not os.path.exists(db_path):
        print("No database found. Nothing to migrate.")
        return
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Get all submissions with feedback data
        cursor.execute('SELECT id, feedback, pros_cons FROM submissions WHERE feedback IS NOT NULL OR pros_cons IS NOT NULL')
        submissions = cursor.fetchall()
        
        print(f"Found {len(submissions)} submissions with feedback data")
        
        fixed_count = 0
        for submission in submissions:
            submission_id = submission['id']
            feedback = submission['feedback']
            pros_cons = submission['pros_cons']
            
            # Check and fix pros_cons data
            if pros_cons:
                try:
                    # Try to parse as JSON
                    if isinstance(pros_cons, str):
                        parsed_pros_cons = json.loads(pros_cons)
                        # Validate structure
                        if not isinstance(parsed_pros_cons, dict):
                            raise ValueError("pros_cons is not a dict")
                        if 'pros' not in parsed_pros_cons or 'cons' not in parsed_pros_cons:
                            raise ValueError("pros_cons missing required keys")
                    else:
                        # Already parsed, just validate
                        parsed_pros_cons = pros_cons
                        
                except (json.JSONDecodeError, ValueError, TypeError) as e:
                    print(f"Fixing malformed pros_cons for submission {submission_id}: {e}")
                    # Create default structure
                    parsed_pros_cons = {
                        'pros': ['Feedback data was corrupted and has been reset'],
                        'cons': ['Please re-evaluate to get proper feedback']
                    }
                    
                    # Update the database
                    cursor.execute(
                        'UPDATE submissions SET pros_cons = ? WHERE id = ?',
                        (json.dumps(parsed_pros_cons), submission_id)
                    )
                    fixed_count += 1
            
            # Ensure feedback is a string
            if feedback is not None and not isinstance(feedback, str):
                print(f"Fixing non-string feedback for submission {submission_id}")
                cursor.execute(
                    'UPDATE submissions SET feedback = ? WHERE id = ?',
                    (str(feedback), submission_id)
                )
                fixed_count += 1
        
        conn.commit()
        print(f"Migration completed. Fixed {fixed_count} submissions.")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
    
    return True

if __name__ == '__main__':
    print("Starting feedback data migration...")
    success = migrate_feedback_data()
    if success:
        print("Migration completed successfully!")
        sys.exit(0)
    else:
        print("Migration failed!")
        sys.exit(1)
