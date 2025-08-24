import React, { useState, useEffect } from 'react';
import { Send, Briefcase, Clock, ChevronDown, ChevronUp, CheckCircle } from 'lucide-react';
import Layout from '../common/Layout';
import TaskSubmission from './TaskSubmission';
import Portfolio from './Portfolio';
import Button from '../ui/Button';
import { useAuth } from '../../contexts/AuthContext';
import apiService from '../../services/api';

const ApplicantDashboard = () => {
  const { user } = useAuth();
  const [tasks, setTasks] = useState([]);
  const [postings, setPostings] = useState([]);
  const [portfolio, setPortfolio] = useState([]);
  const [submissionStatus, setSubmissionStatus] = useState({});
  const [loading, setLoading] = useState(true);
  const [selectedTask, setSelectedTask] = useState(null);
  const [showSubmission, setShowSubmission] = useState(false);
  const [expandedTasks, setExpandedTasks] = useState(new Set());
  const [expandedPostings, setExpandedPostings] = useState(new Set());

  useEffect(() => {
    loadData();
  }, [user]);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // Load core data
      const [tasksData, postingsData, portfolioData] = await Promise.all([
        apiService.getTasks('active'),
        apiService.getPostings('active'),
        apiService.getPortfolio(user.email)
      ]);
      
      setTasks(tasksData);
      setPostings(postingsData);
      setPortfolio(portfolioData.portfolio || []);
      
      // Try to load submission status separately - don't fail if this errors
      try {
        const submissionStatusData = await apiService.getUserSubmissionStatus(user.email);
        setSubmissionStatus(submissionStatusData);
      } catch (statusError) {
        console.warn('Failed to load submission status:', statusError);
        setSubmissionStatus({}); // Set empty object as fallback
      }
      
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmissionClick = (task) => {
    setSelectedTask(task);
    setShowSubmission(true);
  };

  const handleSubmissionClose = () => {
    setShowSubmission(false);
    setSelectedTask(null);
    // Refresh submission status after submission
    loadData();
  };

  const toggleTaskDetails = (taskId) => {
    setExpandedTasks(prev => {
      const newSet = new Set(prev);
      if (newSet.has(taskId)) {
        newSet.delete(taskId);
      } else {
        newSet.add(taskId);
      }
      return newSet;
    });
  };

  const togglePostingDetails = (postingId) => {
    setExpandedPostings(prev => {
      const newSet = new Set(prev);
      if (newSet.has(postingId)) {
        newSet.delete(postingId);
      } else {
        newSet.add(postingId);
      }
      return newSet;
    });
  };

  const getStatusBadge = (taskId) => {
    const status = submissionStatus[taskId]?.status;
    if (!status) return null;

    const statusConfig = {
      pending: { text: 'Pending', color: 'bg-yellow-900 text-yellow-400' },
      evaluating: { text: 'Evaluating', color: 'bg-purple-900 text-purple-400' },
      completed: { text: 'Completed', color: 'bg-green-900 text-green-400' }
    };

    const config = statusConfig[status];
    if (!config) return null;

    return (
      <span className={`px-2 py-1 ${config.color} rounded-full text-xs`}>
        {config.text}
      </span>
    );
  };

  return (
    <Layout>
      <div className="space-y-6">
        <div className="bg-gradient-to-r from-purple-900 to-purple-600 rounded-xl p-6">
          <h2 className="text-2xl font-bold mb-2">Welcome back, {user.name}!</h2>
          <div className="flex space-x-6 mt-4">
            <div>
              <p className="text-purple-200">Tasks Completed</p>
              <p className="text-3xl font-bold">{portfolio.length}</p>
            </div>
            <div>
              <p className="text-purple-200">Average Percentile</p>
              <p className="text-3xl font-bold">
                {portfolio.length > 0 
                  ? (portfolio.reduce((acc, p) => acc + (p.percentile || p.score || 0), 0) / portfolio.length).toFixed(1) + '%'
                  : '-'}
              </p>
            </div>
          </div>
        </div>

        {/* Job Postings Section */}
        <div>
          <h3 className="text-xl font-bold mb-4">Available Job Opportunities</h3>
          {loading ? (
            <div className="text-center py-8">
              <p className="text-zinc-400">Loading job opportunities...</p>
            </div>
          ) : postings.length > 0 ? (
            <div className="grid gap-4">
              {postings.map(posting => (
                <div key={posting.id} className="bg-zinc-900 rounded-lg border border-zinc-800 p-6">
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <h4 className="text-lg font-semibold text-white">{posting.job_title}</h4>
                        <span className="px-2 py-1 bg-blue-900 text-blue-400 rounded-full text-xs">
                          Job Posting
                        </span>
                        {getStatusBadge(posting.id)}
                      </div>
                      <p className="text-zinc-400 mb-3">{posting.job_description}</p>

                      <div className="flex items-center space-x-4 text-sm text-zinc-500">
                        <span className="flex items-center">
                          <Briefcase className="w-4 h-4 mr-1" />
                          {posting.company}
                        </span>
                        {posting.deadline && (
                          <span className="flex items-center">
                            <Clock className="w-4 h-4 mr-1" />
                            {new Date(posting.deadline).toLocaleDateString()}
                          </span>
                        )}
                      </div>
                    </div>
                    <Button 
                      onClick={() => handleSubmissionClick(posting)}
                      disabled={submissionStatus[posting.id]?.status}
                    >
                      <Send className="w-4 h-4 mr-2" />
                      {submissionStatus[posting.id]?.status ? 'Applied' : 'Apply'}
                    </Button>
                  </div>

                  {posting.example_task && (
                    <div className="mb-4">
                      <h5 className="font-medium mb-2 text-zinc-300">Example Task:</h5>
                      <p className="text-zinc-400 text-sm bg-zinc-800 p-3 rounded-lg">{posting.example_task}</p>
                    </div>
                  )}

                  <div className="flex justify-end">
                    <Button 
                      onClick={() => togglePostingDetails(posting.id)}
                      variant="secondary"
                      size="sm"
                    >
                      {expandedPostings.has(posting.id) ? (
                        <>
                          <ChevronUp className="w-4 h-4 mr-2" />
                          Hide Criteria
                        </>
                      ) : (
                        <>
                          <ChevronDown className="w-4 h-4 mr-2" />
                          Show Criteria
                        </>
                      )}
                    </Button>
                  </div>

                  {expandedPostings.has(posting.id) && (
                    <div className="mt-4 pt-4 border-t border-zinc-800">
                      {posting.processed_criteria && posting.processed_criteria.length > 0 && (
                        <div>
                          <h5 className="font-medium mb-2 text-zinc-300">Evaluation Criteria:</h5>
                          <ul className="space-y-1">
                            {posting.processed_criteria.map((criterion, idx) => (
                              <li key={idx} className="text-zinc-400 flex items-center text-sm">
                                <CheckCircle className="w-4 h-4 text-blue-500 mr-2 flex-shrink-0" />
                                {criterion}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 bg-zinc-900 rounded-lg border border-zinc-800">
              <p className="text-zinc-400 mb-2">No job opportunities available at the moment</p>
              <p className="text-sm text-zinc-500">Check back later for new opportunities!</p>
            </div>
          )}
        </div>

        {/* Legacy Tasks Section */}
        {tasks.length > 0 && (
          <div>
            <h3 className="text-xl font-bold mb-4">Available Tasks</h3>
            <div className="grid gap-4">
              {tasks.map(task => (
                <div key={task.id} className="bg-zinc-900 rounded-lg border border-zinc-800 p-6">
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <h4 className="text-lg font-semibold text-white">{task.title}</h4>
                        <span className="px-2 py-1 bg-zinc-700 text-zinc-400 rounded-full text-xs">
                          Legacy Task
                        </span>
                        {getStatusBadge(task.id)}
                      </div>
                      <p className="text-zinc-400 mb-3">{task.description}</p>
                      <div className="flex items-center space-x-4 text-sm text-zinc-500">
                        <span className="flex items-center">
                          <Briefcase className="w-4 h-4 mr-1" />
                          {task.company}
                        </span>
                        {task.deadline && (
                          <span className="flex items-center">
                            <Clock className="w-4 h-4 mr-1" />
                            {new Date(task.deadline).toLocaleDateString()}
                          </span>
                        )}
                      </div>
                    </div>
                    <Button 
                      onClick={() => handleSubmissionClick(task)} 
                      variant="secondary"
                      disabled={submissionStatus[task.id]?.status}
                    >
                      <Send className="w-4 h-4 mr-2" />
                      {submissionStatus[task.id]?.status ? 'Submitted' : 'Submit'}
                    </Button>
                  </div>

                  <div className="flex justify-end">
                    <Button 
                      onClick={() => toggleTaskDetails(task.id)}
                      variant="secondary"
                      size="sm"
                    >
                      {expandedTasks.has(task.id) ? (
                        <>
                          <ChevronUp className="w-4 h-4 mr-2" />
                          Hide Criteria
                        </>
                      ) : (
                        <>
                          <ChevronDown className="w-4 h-4 mr-2" />
                          Show Criteria
                        </>
                      )}
                    </Button>
                  </div>

                  {expandedTasks.has(task.id) && (
                    <div className="mt-4 pt-4 border-t border-zinc-800">
                      {task.criteria && task.criteria.length > 0 && (
                        <div>
                          <h5 className="font-medium mb-2 text-zinc-300">Evaluation Criteria:</h5>
                          <ul className="space-y-1">
                            {task.criteria.map((criterion, idx) => (
                              <li key={idx} className="text-zinc-400 flex items-center text-sm">
                                <CheckCircle className="w-4 h-4 text-purple-500 mr-2 flex-shrink-0" />
                                {criterion}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        <Portfolio portfolio={portfolio} />

        <TaskSubmission 
          task={selectedTask} 
          isOpen={showSubmission}
          onClose={handleSubmissionClose}
        />
      </div>
    </Layout>
  );
};

export default ApplicantDashboard;
