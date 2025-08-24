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
        
        # Create tasks table (legacy)
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
        
        # Create postings table (new job posting pipeline)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS postings (
                id TEXT PRIMARY KEY,
                job_title TEXT NOT NULL,
                job_description TEXT NOT NULL,
                example_task TEXT,
                processed_criteria TEXT,
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
                status TEXT DEFAULT 'pending',
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
        
        # Run migrations for existing databases
        self.migrate_database()
        
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

    def migrate_database(self):
        """Add any missing columns to existing database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if status column exists in submissions table
            cursor.execute("PRAGMA table_info(submissions)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'status' not in columns:
                print("Adding status column to submissions table...")
                cursor.execute("ALTER TABLE submissions ADD COLUMN status TEXT DEFAULT 'pending'")
                conn.commit()
                print("Status column added successfully")
                
        except Exception as e:
            print(f"Migration error: {e}")
        finally:
            conn.close()
    
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
    
    # Posting operations (new job posting pipeline)
    def create_posting(self, posting_data):
        """Create a new job posting"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO postings (id, job_title, job_description, example_task, processed_criteria, 
                                created_at, deadline, status, company)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            posting_data['id'],
            posting_data['job_title'],
            posting_data['job_description'],
            posting_data.get('example_task'),
            json.dumps(posting_data['processed_criteria']) if posting_data.get('processed_criteria') else None,
            posting_data['created_at'],
            posting_data.get('deadline'),
            posting_data.get('status', 'active'),
            posting_data['company']
        ))
        
        conn.commit()
        conn.close()
        return posting_data
    
    def get_postings(self, status='active'):
        """Get all postings with given status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM postings WHERE status = ?', (status,))
        rows = cursor.fetchall()
        
        postings = []
        for row in rows:
            posting = dict(row)
            posting['processed_criteria'] = json.loads(posting['processed_criteria']) if posting['processed_criteria'] else []
            # Get submission count for this posting (using posting_id as task_id for compatibility)
            cursor.execute('SELECT COUNT(*) FROM submissions WHERE task_id = ?', (posting['id'],))
            submission_count = cursor.fetchone()[0]
            posting['submissions'] = [f"submission_{i}" for i in range(submission_count)]
            postings.append(posting)
        
        conn.close()
        return postings
    
    def get_posting(self, posting_id):
        """Get a specific posting by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM postings WHERE id = ?', (posting_id,))
        row = cursor.fetchone()
        
        if row:
            posting = dict(row)
            posting['processed_criteria'] = json.loads(posting['processed_criteria']) if posting['processed_criteria'] else []
            # Get submission IDs for this posting
            cursor.execute('SELECT id FROM submissions WHERE task_id = ?', (posting_id,))
            submission_ids = [r[0] for r in cursor.fetchall()]
            posting['submissions'] = submission_ids
            conn.close()
            return posting
        
        conn.close()
        return None
    
    def delete_posting(self, posting_id):
        """Delete a posting and all related submissions"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get all submissions for this posting first (for file cleanup)
        cursor.execute('SELECT * FROM submissions WHERE task_id = ?', (posting_id,))
        submissions = [dict(row) for row in cursor.fetchall()]
        
        # Delete submissions
        cursor.execute('DELETE FROM submissions WHERE task_id = ?', (posting_id,))
        
        # Delete posting
        cursor.execute('DELETE FROM postings WHERE id = ?', (posting_id,))
        
        # Update user portfolios to remove entries for this posting
        cursor.execute('SELECT email, portfolio FROM users WHERE type = "applicant"')
        users = cursor.fetchall()
        
        for user in users:
            portfolio = json.loads(user['portfolio']) if user['portfolio'] else []
            updated_portfolio = [entry for entry in portfolio if entry.get('task_id') != posting_id]
            cursor.execute('UPDATE users SET portfolio = ? WHERE email = ?', 
                         (json.dumps(updated_portfolio), user['email']))
        
        conn.commit()
        conn.close()
        
        return submissions  # Return submissions for file cleanup
    
    def get_company_postings(self, company_email):
        """Get all postings by a specific company"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM postings WHERE company = ? AND status = ?', (company_email, 'active'))
        rows = cursor.fetchall()
        
        postings = []
        for row in rows:
            posting = dict(row)
            posting['processed_criteria'] = json.loads(posting['processed_criteria']) if posting['processed_criteria'] else []
            # Get submission count for this posting (using posting_id as task_id for compatibility)
            cursor.execute('SELECT COUNT(*) FROM submissions WHERE task_id = ?', (posting['id'],))
            submission_count = cursor.fetchone()[0]
            posting['submissions'] = [f"submission_{i}" for i in range(submission_count)]
            postings.append(posting)
        
        conn.close()
        return postings
    
    # Submission operations
    def create_submission(self, submission_data):
        """Create a new submission"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO submissions (id, task_id, applicant_email, applicant_name, video_path, 
                                   code_path, key_frames, submitted_at, rank, percentile, feedback, pros_cons, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            submission_data.get('pros_cons'),
            submission_data.get('status', 'pending')
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
            
            # Handle key_frames JSON parsing
            try:
                submission['key_frames'] = json.loads(submission['key_frames']) if submission['key_frames'] else []
            except (json.JSONDecodeError, TypeError) as e:
                print(f"Error parsing key_frames for submission {submission['id']}: {e}")
                submission['key_frames'] = []
            
            # Handle pros_cons JSON parsing with better error handling
            try:
                if submission['pros_cons']:
                    if isinstance(submission['pros_cons'], str):
                        submission['pros_cons'] = json.loads(submission['pros_cons'])
                    # If it's already a dict/object, keep it as is
                else:
                    submission['pros_cons'] = None
            except (json.JSONDecodeError, TypeError) as e:
                print(f"Error parsing pros_cons for submission {submission['id']}: {e}")
                submission['pros_cons'] = None
            
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
    
    def get_user_submission_status(self, email):
        """Get submission status for all tasks/postings by a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Try the new query with status column
            cursor.execute('''
                SELECT task_id, status, submitted_at, rank, percentile 
                FROM submissions 
                WHERE applicant_email = ?
                ORDER BY submitted_at DESC
            ''', (email,))
            rows = cursor.fetchall()
            
            submission_status = {}
            for row in rows:
                submission_status[row['task_id']] = {
                    'status': row.get('status', 'completed'),  # Default to completed for old submissions
                    'submitted_at': row['submitted_at'],
                    'rank': row['rank'],
                    'percentile': row['percentile']
                }
                
        except Exception as e:
            print(f"Status column not found, using fallback query: {e}")
            # Fallback for databases without status column
            cursor.execute('''
                SELECT task_id, submitted_at, rank, percentile 
                FROM submissions 
                WHERE applicant_email = ?
                ORDER BY submitted_at DESC
            ''', (email,))
            rows = cursor.fetchall()
            
            submission_status = {}
            for row in rows:
                # Determine status based on existing data
                status = 'completed' if row['rank'] is not None else 'pending'
                submission_status[row['task_id']] = {
                    'status': status,
                    'submitted_at': row['submitted_at'],
                    'rank': row['rank'],
                    'percentile': row['percentile']
                }
        
        conn.close()
        return submission_status
    
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
