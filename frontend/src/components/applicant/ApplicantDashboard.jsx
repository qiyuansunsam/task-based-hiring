import React, { useState, useEffect } from 'react';
import { Send, Briefcase, Clock } from 'lucide-react';
import Layout from '../common/Layout';
import TaskSubmission from './TaskSubmission';
import Portfolio from './Portfolio';
import Button from '../ui/Button';
import { useAuth } from '../../contexts/AuthContext';
import apiService from '../../services/api';

const ApplicantDashboard = () => {
  const { user } = useAuth();
  const [tasks, setTasks] = useState([]);
  const [portfolio, setPortfolio] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedTask, setSelectedTask] = useState(null);
  const [showSubmission, setShowSubmission] = useState(false);

  useEffect(() => {
    loadData();
  }, [user]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [tasksData, portfolioData] = await Promise.all([
        apiService.getTasks('active'),
        apiService.getPortfolio(user.email)
      ]);
      setTasks(tasksData);
      setPortfolio(portfolioData.portfolio || []);
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

        <div>
          <h3 className="text-xl font-bold mb-4">Available Tasks</h3>
          <div className="grid gap-4">
            {tasks.map(task => (
              <div key={task.id} className="bg-zinc-900 rounded-lg border border-zinc-800 p-6">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h4 className="text-lg font-semibold text-white mb-2">{task.title}</h4>
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
                  <Button onClick={() => handleSubmissionClick(task)}>
                    <Send className="w-4 h-4 mr-2" />
                    Submit
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </div>

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
