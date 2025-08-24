const API_BASE_URL = 'http://localhost:5000/api';

class ApiService {
  getFrameUrl(framePath) {
    // Extract the relative path from the full path
    // Frame paths are stored as full paths but need to be served relative to frames folder
    if (framePath.includes('/')) {
      const pathParts = framePath.split('/');
      // Get the last two parts: submission_id/frame_xxxx.jpg
      const relativePath = pathParts.slice(-2).join('/');
      return `${API_BASE_URL}/frames/${relativePath}`;
    }
    return `${API_BASE_URL}/frames/${framePath}`;
  }
  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || `HTTP error! status: ${response.status}`);
      }
      
      return data;
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Authentication
  async login(email, password) {
    return this.request('/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  // Task Management (Legacy)
  async getTasks(status = 'active') {
    return this.request(`/tasks?status=${status}`);
  }

  async createTask(taskData) {
    return this.request('/tasks', {
      method: 'POST',
      body: JSON.stringify(taskData),
    });
  }

  async getTask(taskId) {
    return this.request(`/tasks/${taskId}`);
  }

  async getCompanyTasks(email) {
    return this.request(`/company-tasks/${email}`);
  }

  async deleteTask(taskId) {
    return this.request(`/tasks/${taskId}`, {
      method: 'DELETE',
    });
  }

  async clearAllTasks() {
    return this.request('/tasks/clear-all', {
      method: 'DELETE',
    });
  }

  // Job Posting Management (New Pipeline)
  async getPostings(status = 'active') {
    return this.request(`/postings?status=${status}`);
  }

  async createPosting(postingData) {
    return this.request('/postings', {
      method: 'POST',
      body: JSON.stringify(postingData),
    });
  }

  async getPosting(postingId) {
    return this.request(`/postings/${postingId}`);
  }

  async getCompanyPostings(email) {
    return this.request(`/company-postings/${email}`);
  }

  async deletePosting(postingId) {
    return this.request(`/postings/${postingId}`, {
      method: 'DELETE',
    });
  }

  async processExampleTask(taskData) {
    return this.request('/process-example-task', {
      method: 'POST',
      body: JSON.stringify(taskData),
    });
  }

  async clearAllPostings() {
    return this.request('/postings/clear-all', {
      method: 'DELETE',
    });
  }

  // Submissions
  async createSubmission(formData) {
    return this.request('/submissions', {
      method: 'POST',
      headers: {}, // Remove Content-Type to let browser set it for FormData
      body: formData,
    });
  }

  async getSubmissions(taskId) {
    return this.request(`/submissions/${taskId}`);
  }

  async getUserSubmissions(email) {
    return this.request(`/user-submissions/${email}`);
  }

  async getUserSubmissionStatus(email) {
    return this.request(`/user-submission-status/${email}`);
  }

  // Evaluation
  async evaluateTask(taskId) {
    return this.request(`/evaluate/${taskId}`, {
      method: 'POST',
    });
  }

  async getEvaluationProgress(taskId) {
    return this.request(`/evaluation-progress/${taskId}`);
  }

  // Frame Extraction
  async extractFrames(taskId) {
    return this.request(`/extract-frames/${taskId}`, {
      method: 'POST',
    });
  }

  // Portfolio
  async getPortfolio(email) {
    return this.request(`/portfolio/${email}`);
  }
}

export default new ApiService();
