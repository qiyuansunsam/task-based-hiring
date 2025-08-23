const API_BASE_URL = 'http://localhost:5000/api';

class ApiService {
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

  // Task Management
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
