import React, { useState, useEffect } from 'react';
import { PlusCircle, FileText, Trophy, CheckCircle, BarChart3, Camera, Loader2, Trash2, RefreshCw } from 'lucide-react';
import { useToast } from '../ui/Toast';
import Layout from '../common/Layout';
import TaskCreation from './TaskCreation';
import JobPostingCreation from './JobPostingCreation';
import EvaluationResults from './EvaluationResults';
import Button from '../ui/Button';
import Modal from '../ui/Modal';
import apiService from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';

const CompanyDashboard = () => {
  const { user } = useAuth();
  const { message } = useToast();
  const [tasks, setTasks] = useState([]);
  const [postings, setPostings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showTaskCreation, setShowTaskCreation] = useState(false);
  const [showJobPostingCreation, setShowJobPostingCreation] = useState(false);
  const [selectedTask, setSelectedTask] = useState(null);
  const [showEvaluationResults, setShowEvaluationResults] = useState(false);
  const [evaluationTaskId, setEvaluationTaskId] = useState(null);
  const [evaluatingTaskId, setEvaluatingTaskId] = useState(null);
  const [evaluationProgress, setEvaluationProgress] = useState('');
  const [showClearConfirmation, setShowClearConfirmation] = useState(false);
  const [taskToDelete, setTaskToDelete] = useState(null);
  const [postingToDelete, setPostingToDelete] = useState(null);
  const [deletingTaskId, setDeletingTaskId] = useState(null);
  const [deletingPostingId, setDeletingPostingId] = useState(null);

  useEffect(() => {
    loadTasks();
    loadPostings();
  }, [user]);

  const loadTasks = async () => {
    try {
      setLoading(true);
      const tasksData = await apiService.getCompanyTasks(user.email);
      setTasks(tasksData);
    } catch (error) {
      console.error('Failed to load tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadPostings = async () => {
    try {
      const postingsData = await apiService.getCompanyPostings(user.email);
      setPostings(postingsData);
    } catch (error) {
      console.error('Failed to load postings:', error);
    }
  };

  const handleTaskCreated = (newTask) => {
    setTasks(prev => [newTask, ...prev]);
    setShowTaskCreation(false);
  };

  const handlePostingCreated = (newPosting) => {
    setPostings(prev => [newPosting, ...prev]);
    setShowJobPostingCreation(false);
  };

  const evaluateTask = async (taskId) => {
    try {
      setEvaluatingTaskId(taskId);
      setEvaluationProgress('Starting evaluation...');
      
      // Start polling for progress updates
      const progressInterval = setInterval(async () => {
        try {
          const progress = await apiService.getEvaluationProgress(taskId);
          setEvaluationProgress(progress.message);
          
          if (progress.completed) {
            clearInterval(progressInterval);
            setEvaluationProgress('');
            setEvaluatingTaskId(null);
            
            if (progress.message.includes('failed')) {
              message.error('Evaluation failed: ' + progress.message);
            } else {
              message.success('Evaluation completed successfully!');
              loadTasks(); // Refresh tasks to show updated submission data
              loadPostings(); // Refresh postings to show updated submission data
            }
          }
        } catch (error) {
          console.error('Failed to get progress:', error);
        }
      }, 1000); // Poll every second
      
      // Start the evaluation
      await apiService.evaluateTask(taskId);
      
    } catch (error) {
      setEvaluationProgress('');
      setEvaluatingTaskId(null);
      message.error('Evaluation failed: ' + error.message);
    }
  };

  const extractFrames = async (taskId) => {
    try {
      const result = await apiService.extractFrames(taskId);
      message.success(`Frame extraction completed! Processed ${result.submissions_processed} submissions.`);
      // Refresh both tasks and postings to show updated data
      loadTasks();
      loadPostings();
    } catch (error) {
      message.error('Frame extraction failed: ' + error.message);
    }
  };

  const handleDeleteTask = (task) => {
    setTaskToDelete(task);
    setShowClearConfirmation(true);
  };

  const handleDeletePosting = (posting) => {
    setPostingToDelete(posting);
    setShowClearConfirmation(true);
  };

  const confirmDeleteTask = async () => {
    try {
      if (taskToDelete) {
        // Single task deletion
        setDeletingTaskId(taskToDelete.id);
        await apiService.deleteTask(taskToDelete.id);
        setTasks(prev => prev.filter(t => t.id !== taskToDelete.id));
        message.success('Task and all related submissions deleted successfully!');
      } else if (postingToDelete) {
        // Single posting deletion
        setDeletingPostingId(postingToDelete.id);
        await apiService.deletePosting(postingToDelete.id);
        setPostings(prev => prev.filter(p => p.id !== postingToDelete.id));
        message.success('Job posting and all related submissions deleted successfully!');
      } else {
        // Bulk deletion - clear all tasks
        await apiService.clearAllTasks();
        setTasks([]);
        message.success('All tasks cleared successfully!');
      }
      
      setShowClearConfirmation(false);
      setTaskToDelete(null);
      setPostingToDelete(null);
    } catch (error) {
      const errorTarget = taskToDelete ? 'task' : postingToDelete ? 'posting' : 'tasks';
      message.error(`Failed to delete ${errorTarget}: ` + error.message);
    } finally {
      setDeletingTaskId(null);
      setDeletingPostingId(null);
    }
  };

  const cancelDeleteTask = () => {
    setShowClearConfirmation(false);
    setTaskToDelete(null);
    setPostingToDelete(null);
  };

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold">Company Dashboard</h2>
          <div className="flex space-x-3">
            <Button 
              onClick={() => {
                loadTasks();
                loadPostings();
              }}
              variant="secondary"
            >
              <RefreshCw className="w-5 h-5 mr-2" />
              Refresh
            </Button>
            {postings.length > 0 && (
              <Button 
                onClick={async () => {
                  try {
                    await apiService.clearAllPostings();
                    setPostings([]);
                    message.success('All job postings cleared successfully!');
                  } catch (error) {
                    message.error('Failed to clear postings: ' + error.message);
                  }
                }}
                variant="secondary"
              >
                <Trash2 className="w-5 h-5 mr-2" />
                Clear All Postings
              </Button>
            )}
            {tasks.length > 0 && (
              <Button 
                onClick={async () => {
                  try {
                    await apiService.clearAllTasks();
                    setTasks([]);
                    message.success('All tasks cleared successfully!');
                  } catch (error) {
                    message.error('Failed to clear tasks: ' + error.message);
                  }
                }}
                variant="secondary"
              >
                <Trash2 className="w-5 h-5 mr-2" />
                Clear All Tasks
              </Button>
            )}
            <Button onClick={() => setShowJobPostingCreation(true)}>
              <PlusCircle className="w-5 h-5 mr-2" />
              Create Job Posting
            </Button>
          </div>
        </div>

        <TaskCreation 
          isOpen={showTaskCreation}
          onClose={() => setShowTaskCreation(false)}
          onTaskCreated={handleTaskCreated}
        />

        <JobPostingCreation
          isOpen={showJobPostingCreation}
          onClose={() => setShowJobPostingCreation(false)}
          onPostingCreated={handlePostingCreated}
        />

        <EvaluationResults
          taskId={evaluationTaskId}
          isOpen={showEvaluationResults}
          onClose={() => {
            setShowEvaluationResults(false);
            setEvaluationTaskId(null);
          }}
        />

        {/* Job Postings Section */}
        {postings.length > 0 && (
          <div className="space-y-4">
            <h3 className="text-xl font-semibold text-white">Job Postings</h3>
            <div className="grid gap-4">
              {postings.map(posting => (
                <div key={posting.id} className="bg-zinc-900 rounded-lg border border-zinc-800 p-6">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h4 className="text-xl font-semibold text-white mb-2">{posting.job_title}</h4>
                      <p className="text-zinc-400">{posting.job_description}</p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="px-3 py-1 bg-zinc-800 rounded-full text-sm">
                        {posting.submissions?.length || 0} submissions
                      </span>
                      <span className="px-3 py-1 bg-blue-900 text-blue-400 rounded-full text-sm">
                        Job Posting
                      </span>
                      <Button
                        onClick={() => handleDeletePosting(posting)}
                        variant="secondary"
                        size="sm"
                        disabled={deletingPostingId === posting.id}
                      >
                        {deletingPostingId === posting.id ? (
                          <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                          <Trash2 className="w-4 h-4" />
                        )}
                      </Button>
                    </div>
                  </div>
                  
                  {posting.example_task && (
                    <div className="mb-4">
                      <h5 className="font-medium mb-2 text-zinc-300">Example Task:</h5>
                      <p className="text-zinc-400 text-sm bg-zinc-800 p-3 rounded-lg">{posting.example_task}</p>
                    </div>
                  )}

                  {posting.processed_criteria && posting.processed_criteria.length > 0 && (
                    <div className="mb-4">
                      <h5 className="font-medium mb-2 text-zinc-300">AI-Generated Criteria:</h5>
                      <ul className="space-y-1">
                        {posting.processed_criteria.map((criterion, idx) => (
                          <li key={idx} className="text-zinc-400 flex items-center">
                            <CheckCircle className="w-4 h-4 text-blue-500 mr-2" />
                            {criterion}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  <div className="flex space-x-3">
                    {posting.submissions?.length > 0 && (
                      <Button 
                        onClick={() => extractFrames(posting.id)}
                        variant="secondary"
                      >
                        <Camera className="w-4 h-4 mr-2" />
                        Extract Frames
                      </Button>
                    )}
                    {posting.submissions?.length >= 2 && (
                      evaluatingTaskId === posting.id ? (
                        <div className="flex items-center space-x-2 px-4 py-2 bg-purple-900 text-purple-300 rounded-lg">
                          <Loader2 className="w-4 h-4 animate-spin" />
                          <span className="text-sm">{evaluationProgress}</span>
                        </div>
                      ) : (
                        <Button onClick={() => evaluateTask(posting.id)}>
                          <Trophy className="w-4 h-4 mr-2" />
                          Evaluate Submissions
                        </Button>
                      )
                    )}
                    {posting.submissions?.length > 0 && (
                      <Button 
                        onClick={() => {
                          setEvaluationTaskId(posting.id);
                          setShowEvaluationResults(true);
                        }}
                        variant="secondary"
                      >
                        <BarChart3 className="w-4 h-4 mr-2" />
                        View Results
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tasks Section */}
        {tasks.length > 0 && (
          <div className="space-y-4">
            <h3 className="text-xl font-semibold text-white">Legacy Tasks</h3>
            <div className="grid gap-4">
              {tasks.map(task => (
            <div key={task.id} className="bg-zinc-900 rounded-lg border border-zinc-800 p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">{task.title}</h3>
                  <p className="text-zinc-400">{task.description}</p>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="px-3 py-1 bg-zinc-800 rounded-full text-sm">
                    {task.submissions?.length || 0} submissions
                  </span>
                  {task.status === 'active' && (
                    <span className="px-3 py-1 bg-green-900 text-green-400 rounded-full text-sm">
                      Active
                    </span>
                  )}
                  <Button
                    onClick={() => handleDeleteTask(task)}
                    variant="secondary"
                    size="sm"
                    disabled={deletingTaskId === task.id}
                  >
                    {deletingTaskId === task.id ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Trash2 className="w-4 h-4" />
                    )}
                  </Button>
                </div>
              </div>
              
              <div className="flex space-x-3">
                <Button
                  onClick={() => setSelectedTask(selectedTask === task.id ? null : task.id)}
                  variant="secondary"
                >
                  <FileText className="w-4 h-4 mr-2" />
                  View Details
                </Button>
                {task.submissions?.length > 0 && (
                  <Button 
                    onClick={() => extractFrames(task.id)}
                    variant="secondary"
                  >
                    <Camera className="w-4 h-4 mr-2" />
                    Extract Frames
                  </Button>
                )}
                {task.submissions?.length >= 2 && (
                  evaluatingTaskId === task.id ? (
                    <div className="flex items-center space-x-2 px-4 py-2 bg-purple-900 text-purple-300 rounded-lg">
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span className="text-sm">{evaluationProgress}</span>
                    </div>
                  ) : (
                    <Button onClick={() => evaluateTask(task.id)}>
                      <Trophy className="w-4 h-4 mr-2" />
                      Evaluate Submissions
                    </Button>
                  )
                )}
                {task.submissions?.length > 0 && (
                  <Button 
                    onClick={() => {
                      setEvaluationTaskId(task.id);
                      setShowEvaluationResults(true);
                    }}
                    variant="secondary"
                  >
                    <BarChart3 className="w-4 h-4 mr-2" />
                    View Results
                  </Button>
                )}
              </div>

              {selectedTask === task.id && (
                <div className="mt-4 pt-4 border-t border-zinc-800">
                  <h4 className="font-medium mb-2">Evaluation Criteria:</h4>
                  <ul className="space-y-1">
                    {task.criteria?.map((criterion, idx) => (
                      <li key={idx} className="text-zinc-400 flex items-center">
                        <CheckCircle className="w-4 h-4 text-purple-500 mr-2" />
                        {criterion}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
            </div>
          </div>
        )}

        {/* Delete Confirmation Modal */}
        <Modal
          isOpen={showClearConfirmation}
          onClose={cancelDeleteTask}
          title={taskToDelete ? "Delete Task" : postingToDelete ? "Delete Job Posting" : "Delete All Tasks"}
          maxWidth="md"
        >
          <div className="space-y-4">
            <div className="text-zinc-300">
              {taskToDelete ? (
                <div>
                  <p className="mb-2">Are you sure you want to delete this task?</p>
                  <div className="bg-zinc-800 p-3 rounded-lg mb-4">
                    <h4 className="font-semibold text-white">{taskToDelete.title}</h4>
                    <p className="text-sm text-zinc-400 mt-1">{taskToDelete.description}</p>
                    <p className="text-sm text-zinc-500 mt-2">
                      {taskToDelete.submissions?.length || 0} submission(s) will also be deleted
                    </p>
                  </div>
                  <p className="text-red-400 text-sm">
                    This action cannot be undone. All related submissions, files, and portfolio entries will be permanently deleted.
                  </p>
                </div>
              ) : postingToDelete ? (
                <div>
                  <p className="mb-2">Are you sure you want to delete this job posting?</p>
                  <div className="bg-zinc-800 p-3 rounded-lg mb-4">
                    <h4 className="font-semibold text-white">{postingToDelete.job_title}</h4>
                    <p className="text-sm text-zinc-400 mt-1">{postingToDelete.job_description}</p>
                    <p className="text-sm text-zinc-500 mt-2">
                      {postingToDelete.submissions?.length || 0} submission(s) will also be deleted
                    </p>
                  </div>
                  <p className="text-red-400 text-sm">
                    This action cannot be undone. All related submissions, files, and portfolio entries will be permanently deleted.
                  </p>
                </div>
              ) : (
                <p>Are you sure you want to delete all tasks? This will remove all tasks and their related submissions permanently.</p>
              )}
            </div>
            
            <div className="flex justify-end space-x-3 pt-4">
              <Button
                onClick={cancelDeleteTask}
                variant="secondary"
              >
                Cancel
              </Button>
              <Button
                onClick={confirmDeleteTask}
                disabled={deletingTaskId !== null || deletingPostingId !== null}
                className="bg-red-600 hover:bg-red-700"
              >
                {(deletingTaskId || deletingPostingId) ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Deleting...
                  </>
                ) : (
                  <>
                    <Trash2 className="w-4 h-4 mr-2" />
                    {taskToDelete ? 'Delete Task' : postingToDelete ? 'Delete Job Posting' : 'Delete All Tasks'}
                  </>
                )}
              </Button>
            </div>
          </div>
        </Modal>
      </div>
    </Layout>
  );
};

export default CompanyDashboard;
