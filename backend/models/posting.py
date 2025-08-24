class Posting:
    """
    Job Posting model for the upgraded pipeline
    Replaces the task model with enhanced structure for AI-processed criteria
    """
    def __init__(self, id, job_title, job_description, example_task, 
                 processed_criteria, deadline=None, company=None, 
                 created_at=None, status='active'):
        self.id = id
        self.job_title = job_title
        self.job_description = job_description
        self.example_task = example_task
        self.processed_criteria = processed_criteria  # AI-generated criteria
        self.deadline = deadline
        self.company = company
        self.created_at = created_at
        self.status = status
    
    def to_dict(self):
        """Convert posting to dictionary format"""
        return {
            'id': self.id,
            'job_title': self.job_title,
            'job_description': self.job_description,
            'example_task': self.example_task,
            'processed_criteria': self.processed_criteria,
            'deadline': self.deadline,
            'company': self.company,
            'created_at': self.created_at,
            'status': self.status
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create posting from dictionary"""
        return cls(
            id=data['id'],
            job_title=data['job_title'],
            job_description=data['job_description'],
            example_task=data['example_task'],
            processed_criteria=data['processed_criteria'],
            deadline=data.get('deadline'),
            company=data.get('company'),
            created_at=data.get('created_at'),
            status=data.get('status', 'active')
        )