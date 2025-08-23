import sqlite3
import json
import os
from datetime import datetime

class Database:
    def __init__(self, db_path='tasks.db'):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # This allows dict-like access to rows
        return conn
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create tasks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                criteria TEXT,
                created_at TEXT,
                deadline TEXT,
                status TEXT DEFAULT 'active',
                company TEXT
            )
        ''')
        
        # Create submissions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS submissions (
                id TEXT PRIMARY KEY,
                task_id TEXT,
                applicant_email TEXT,
                applicant_name TEXT,
                video_path TEXT,
                code_path TEXT,
                key_frames TEXT,
                submitted_at TEXT,
                rank INTEGER,
                percentile REAL,
                feedback TEXT,
                pros_cons TEXT,
                FOREIGN KEY (task_id) REFERENCES tasks (id)
            )
        ''')
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                email TEXT PRIMARY KEY,
                password TEXT,
                type TEXT,
                name TEXT,
                portfolio TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Initialize default users if they don't exist
        self.init_default_users()
    
    def init_default_users(self):
        """Initialize default users if the users table is empty"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM users')
        count = cursor.fetchone()[0]
        
        if count == 0:
            default_users = [
                ('gemini@test.com', '123', 'applicant', 'Gemini AI', '[]'),
                ('gpt@test.com', '123', 'applicant', 'GPT Assistant', '[]'),
                ('custom@test.com', '123', 'applicant', 'Custom AI', '[]'),
                ('deepseek@test.com', '123', 'applicant', 'DeepSeek AI', '[]'),
                ('demo@test.com', '123', 'company', 'Demo Company', '[]')
            ]
            
            cursor.executemany(
                'INSERT INTO users (email, password, type, name, portfolio) VALUES (?, ?, ?, ?, ?)',
                default_users
            )
            conn.commit()
        
        conn.close()
    
    # Task operations
    def create_task(self, task_data):
        """Create a new task"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO tasks (id, title, description, criteria, created_at, deadline, status, company)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            task_data['id'],
            task_data['title'],
            task_data['description'],
            json.dumps(task_data['criteria']),
            task_data['created_at'],
            task_data.get('deadline'),
            task_data['status'],
            task_data['company']
        ))
        
        conn.commit()
        conn.close()
        return task_data
    
    def get_tasks(self, status='active'):
        """Get all tasks with given status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM tasks WHERE status = ?', (status,))
        rows = cursor.fetchall()
        
        tasks = []
        for row in rows:
            task = dict(row)
            task['criteria'] = json.loads(task['criteria']) if task['criteria'] else []
            # Get submission count for this task
            cursor.execute('SELECT COUNT(*) FROM submissions WHERE task_id = ?', (task['id'],))
            submission_count = cursor.fetchone()[0]
            task['submissions'] = [f"submission_{i}" for i in range(submission_count)]  # Placeholder for compatibility
            tasks.append(task)
        
        conn.close()
        return tasks
    
    def get_task(self, task_id):
        """Get a specific task by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
        row = cursor.fetchone()
        
        if row:
            task = dict(row)
            task['criteria'] = json.loads(task['criteria']) if task['criteria'] else []
            # Get submission IDs for this task
            cursor.execute('SELECT id FROM submissions WHERE task_id = ?', (task_id,))
            submission_ids = [r[0] for r in cursor.fetchall()]
            task['submissions'] = submission_ids
            conn.close()
            return task
        
        conn.close()
        return None
    
    def delete_task(self, task_id):
        """Delete a task and all related submissions"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get all submissions for this task first (for file cleanup)
        cursor.execute('SELECT * FROM submissions WHERE task_id = ?', (task_id,))
        submissions = [dict(row) for row in cursor.fetchall()]
        
        # Delete submissions
        cursor.execute('DELETE FROM submissions WHERE task_id = ?', (task_id,))
        
        # Delete task
        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        
        # Update user portfolios to remove entries for this task
        cursor.execute('SELECT email, portfolio FROM users WHERE type = "applicant"')
        users = cursor.fetchall()
        
        for user in users:
            portfolio = json.loads(user['portfolio']) if user['portfolio'] else []
            updated_portfolio = [entry for entry in portfolio if entry.get('task_id') != task_id]
            cursor.execute('UPDATE users SET portfolio = ? WHERE email = ?', 
                         (json.dumps(updated_portfolio), user['email']))
        
        conn.commit()
        conn.close()
        
        return submissions  # Return submissions for file cleanup
    
    # Submission operations
    def create_submission(self, submission_data):
        """Create a new submission"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO submissions (id, task_id, applicant_email, applicant_name, video_path, 
                                   code_path, key_frames, submitted_at, rank, percentile, feedback, pros_cons)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            submission_data['id'],
            submission_data['task_id'],
            submission_data['applicant_email'],
            submission_data['applicant_name'],
            submission_data['video_path'],
            submission_data['code_path'],
            json.dumps(submission_data['key_frames']),
            submission_data['submitted_at'],
            submission_data.get('rank'),
            submission_data.get('percentile'),
            submission_data.get('feedback'),
            submission_data.get('pros_cons')
        ))
        
        conn.commit()
        conn.close()
        return submission_data
    
    def get_submissions(self, task_id):
        """Get all submissions for a task"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM submissions WHERE task_id = ?', (task_id,))
        rows = cursor.fetchall()
        
        submissions = []
        for row in rows:
            submission = dict(row)
            submission['key_frames'] = json.loads(submission['key_frames']) if submission['key_frames'] else []
            submission['pros_cons'] = json.loads(submission['pros_cons']) if submission['pros_cons'] else None
            submissions.append(submission)
        
        conn.close()
        return submissions
    
    def get_user_submissions(self, email):
        """Get all submissions by a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM submissions WHERE applicant_email = ?', (email,))
        rows = cursor.fetchall()
        
        submissions = []
        for row in rows:
            submission = dict(row)
            submission['key_frames'] = json.loads(submission['key_frames']) if submission['key_frames'] else []
            submission['pros_cons'] = json.loads(submission['pros_cons']) if submission['pros_cons'] else None
            submissions.append(submission)
        
        conn.close()
        return submissions
    
    def update_submission(self, submission_id, updates):
        """Update a submission with new data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Build dynamic update query
        set_clauses = []
        values = []
        
        for key, value in updates.items():
            if key == 'key_frames' or key == 'pros_cons':
                value = json.dumps(value)
            set_clauses.append(f"{key} = ?")
            values.append(value)
        
        values.append(submission_id)
        
        query = f"UPDATE submissions SET {', '.join(set_clauses)} WHERE id = ?"
        cursor.execute(query, values)
        
        conn.commit()
        conn.close()
    
    # User operations
    def get_user(self, email):
        """Get user by email"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        row = cursor.fetchone()
        
        if row:
            user = dict(row)
            user['portfolio'] = json.loads(user['portfolio']) if user['portfolio'] else []
            conn.close()
            return user
        
        conn.close()
        return None
    
    def update_user_portfolio(self, email, portfolio_entry):
        """Add an entry to user's portfolio"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT portfolio FROM users WHERE email = ?', (email,))
        row = cursor.fetchone()
        
        if row:
            portfolio = json.loads(row['portfolio']) if row['portfolio'] else []
            portfolio.append(portfolio_entry)
            
            cursor.execute('UPDATE users SET portfolio = ? WHERE email = ?', 
                         (json.dumps(portfolio), email))
            conn.commit()
        
        conn.close()

# Global database instance
db = Database()
