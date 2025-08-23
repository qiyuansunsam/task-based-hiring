from flask import Flask, request, jsonify, send_file, Response
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import json
import zipfile
import shutil
from datetime import datetime
import uuid
from services.frame_extraction_service import extract_key_frames
from services.evaluation_service import EvaluationService
from services.llm_service import LLMService
from database import db

app = Flask(__name__)
CORS(app)

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['FRAMES_FOLDER'] = 'extracted_frames'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Services
evaluation_service = EvaluationService()
llm_service = LLMService()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    user = db.get_user(email)
    if user and user['password'] == password:
        user_response = user.copy()
        del user_response['password']
        return jsonify({'success': True, 'user': user_response})
    
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/api/tasks', methods=['GET', 'POST'])
def handle_tasks():
    if request.method == 'GET':
        # Get all tasks or filter by status
        status = request.args.get('status', 'active')
        tasks = db.get_tasks(status)
        return jsonify(tasks)
    
    elif request.method == 'POST':
        # Create new task (company only)
        data = request.json
        task = {
            'id': str(uuid.uuid4()),
            'title': data['title'],
            'description': data['description'],
            'criteria': data['criteria'],
            'created_at': datetime.now().isoformat(),
            'deadline': data.get('deadline'),
            'status': 'active',
            'company': data['company']
        }
        created_task = db.create_task(task)
        # Add submissions array for compatibility
        created_task['submissions'] = []
        return jsonify(created_task), 201

@app.route('/api/tasks/clear-all', methods=['DELETE'])
def clear_all_tasks():
    """Delete all tasks and their associated files"""
    try:
        # Get all tasks first
        all_tasks = db.get_tasks('active')
        
        # Delete each task and clean up files
        for task in all_tasks:
            # Delete task and get submissions for file cleanup
            task_submissions = db.delete_task(task['id'])
            
            # Clean up files for each submission
            for submission in task_submissions:
                # Delete video file
                if submission['video_path'] and os.path.exists(submission['video_path']):
                    try:
                        os.remove(submission['video_path'])
                    except OSError:
                        pass
                
                # Delete code file
                if submission['code_path'] and os.path.exists(submission['code_path']):
                    try:
                        os.remove(submission['code_path'])
                    except OSError:
                        pass
                
                # Delete extracted frames folder
                if submission.get('key_frames'):
                    import json
                    key_frames = json.loads(submission['key_frames']) if isinstance(submission['key_frames'], str) else submission['key_frames']
                    if key_frames:
                        # Get the frames directory from first frame path
                        frames_dir = os.path.dirname(key_frames[0])
                        if os.path.exists(frames_dir):
                            import shutil
                            try:
                                shutil.rmtree(frames_dir)
                            except OSError:
                                pass
        
        return jsonify({'message': f'Successfully cleared {len(all_tasks)} tasks'}), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to clear tasks: {str(e)}'}), 500

@app.route('/api/tasks/<task_id>', methods=['GET', 'DELETE'])
def handle_task(task_id):
    if request.method == 'GET':
        task = db.get_task(task_id)
        if task:
            return jsonify(task)
        return jsonify({'error': 'Task not found'}), 404
    
    elif request.method == 'DELETE':
        # Find the task to delete
        task = db.get_task(task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        # Delete task and get submissions for file cleanup
        task_submissions = db.delete_task(task_id)
        
        # Clean up files for each submission
        for submission in task_submissions:
            # Delete video file
            if submission['video_path'] and os.path.exists(submission['video_path']):
                try:
                    os.remove(submission['video_path'])
                except OSError:
                    pass
            
            # Delete code file
            if submission['code_path'] and os.path.exists(submission['code_path']):
                try:
                    os.remove(submission['code_path'])
                except OSError:
                    pass
            
            # Delete extracted frames folder
            frames_folder = os.path.join(app.config['FRAMES_FOLDER'], submission['id'])
            if os.path.exists(frames_folder):
                try:
                    shutil.rmtree(frames_folder)
                except OSError:
                    pass
        
        return jsonify({'success': True, 'message': 'Task and all related submissions deleted successfully'})

@app.route('/api/submissions', methods=['POST'])
def create_submission():
    task_id = request.form.get('task_id')
    applicant_email = request.form.get('applicant_email')
    
    # Handle file uploads
    video_file = request.files.get('video')
    code_file = request.files.get('code')
    
    if not video_file or not code_file:
        return jsonify({'error': 'Both video and code files are required'}), 400
    
    # Create submission ID
    submission_id = str(uuid.uuid4())
    
    # Save files
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{submission_id}_video.mp4")
    code_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{submission_id}_code.zip")
    
    video_file.save(video_path)
    code_file.save(code_path)
    
    # Extract key frames from video
    frames_folder = os.path.join(app.config['FRAMES_FOLDER'], submission_id)
    os.makedirs(frames_folder, exist_ok=True)
    key_frames = extract_key_frames(video_path, frames_folder)
    
    # Get user name from database
    user = db.get_user(applicant_email)
    applicant_name = user['name'] if user else 'Unknown'
    
    # Create submission record
    submission = {
        'id': submission_id,
        'task_id': task_id,
        'applicant_email': applicant_email,
        'applicant_name': applicant_name,
        'video_path': video_path,
        'code_path': code_path,
        'key_frames': key_frames,
        'submitted_at': datetime.now().isoformat(),
        'rank': None,
        'percentile': None,
        'feedback': None,
        'pros_cons': None
    }
    
    db.create_submission(submission)
    
    return jsonify({'success': True, 'submission_id': submission_id}), 201

@app.route('/api/submissions/<task_id>', methods=['GET'])
def get_submissions(task_id):
    submissions = db.get_submissions(task_id)
    return jsonify(submissions)

@app.route('/api/extract-frames/<task_id>', methods=['POST'])
def extract_frames_for_task(task_id):
    task = db.get_task(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    submissions = db.get_submissions(task_id)
    
    if len(submissions) == 0:
        return jsonify({'error': 'No submissions found for this task'}), 400
    
    # Extract frames for all submissions
    extracted_count = 0
    for submission in submissions:
        frames_folder = os.path.join(app.config['FRAMES_FOLDER'], submission['id'])
        video_path = submission['video_path']
        
        # Extract key frames with new algorithm
        new_key_frames = extract_key_frames(video_path, frames_folder)
        
        # Update the submission in database
        db.update_submission(submission['id'], {'key_frames': new_key_frames})
        extracted_count += 1
    
    return jsonify({
        'success': True, 
        'message': f'Extracted frames for {extracted_count} submissions',
        'submissions_processed': extracted_count
    })

# Global progress storage for SSE
evaluation_progress = {}

@app.route('/api/evaluate/<task_id>', methods=['POST'])
def evaluate_task(task_id):
    task = db.get_task(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    submissions = db.get_submissions(task_id)
    
    if len(submissions) < 2:
        return jsonify({'error': 'Need at least 2 submissions to evaluate'}), 400
    
    # Initialize progress tracking
    evaluation_progress[task_id] = {'message': 'Starting evaluation...', 'completed': False}
    
    def progress_callback(message):
        evaluation_progress[task_id] = {'message': message, 'completed': False}
        print(f"Progress: {message}")
    
    try:
        # Re-extract frames for all submissions with improved algorithm
        for i, submission in enumerate(submissions):
            progress_callback(f"Extracting frames for {submission['applicant_name']} ({i+1}/{len(submissions)})")
            frames_folder = os.path.join(app.config['FRAMES_FOLDER'], submission['id'])
            video_path = submission['video_path']
            
            # Re-extract key frames with new algorithm (this will clean up old frames)
            new_key_frames = extract_key_frames(video_path, frames_folder)
            submission['key_frames'] = new_key_frames
            
            # Update the submission in database
            db.update_submission(submission['id'], {'key_frames': new_key_frames})
        
        # Perform evaluation using decision tree sorting
        ranked_submissions = evaluation_service.rank_submissions(
            submissions, 
            task['description'], 
            task['criteria'],
            llm_service,
            progress_callback
        )
        
        # Update submissions with rankings and feedback
        for idx, sub in enumerate(ranked_submissions):
            updates = {
                'rank': idx + 1,
                'percentile': sub['percentile'],
                'feedback': sub['feedback'],
                'pros_cons': sub['pros_cons']
            }
            db.update_submission(sub['id'], updates)
            
            # Update applicant's portfolio
            portfolio_entry = {
                'task_id': task_id,
                'task_title': task['title'],
                'submission_id': sub['id'],
                'rank': idx + 1,
                'total_submissions': len(submissions),
                'percentile': sub['percentile'],
                'feedback': sub['feedback'],
                'pros_cons': sub['pros_cons'],
                'submitted_at': sub['submitted_at']
            }
            db.update_user_portfolio(sub['applicant_email'], portfolio_entry)
        
        # Mark evaluation as completed
        evaluation_progress[task_id] = {'message': 'Evaluation completed!', 'completed': True}
        
        return jsonify({'success': True, 'ranked_submissions': ranked_submissions})
    
    except Exception as e:
        evaluation_progress[task_id] = {'message': f'Evaluation failed: {str(e)}', 'completed': True}
        return jsonify({'error': str(e)}), 500

@app.route('/api/evaluation-progress/<task_id>')
def get_evaluation_progress(task_id):
    """Get current evaluation progress for a task"""
    progress = evaluation_progress.get(task_id, {'message': 'No evaluation in progress', 'completed': True})
    return jsonify(progress)

@app.route('/api/portfolio/<email>', methods=['GET'])
def get_portfolio(email):
    user = db.get_user(email)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if user['type'] != 'applicant':
        return jsonify({'error': 'Only applicants have portfolios'}), 400
    
    return jsonify({
        'name': user['name'],
        'email': email,
        'portfolio': user['portfolio']
    })

@app.route('/api/user-submissions/<email>', methods=['GET'])
def get_user_submissions(email):
    submissions = db.get_user_submissions(email)
    return jsonify(submissions)

@app.route('/api/company-tasks/<email>', methods=['GET'])
def get_company_tasks(email):
    # For demo, return all tasks since we only have one company
    tasks = db.get_tasks('active')
    return jsonify(tasks)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['FRAMES_FOLDER'], exist_ok=True)
    app.run(debug=True, port=5000)
