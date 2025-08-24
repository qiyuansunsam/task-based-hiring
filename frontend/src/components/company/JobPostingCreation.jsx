import React, { useState } from 'react';
import { Sparkles, Eye, X } from 'lucide-react';
import { useToast } from '../ui/Toast';
import Modal from '../ui/Modal';
import Button from '../ui/Button';
import Input from '../ui/Input';
import apiService from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';

const JobPostingCreation = ({ isOpen, onClose, onPostingCreated }) => {
  const { user } = useAuth();
  const { message } = useToast();
  const [jobTitle, setJobTitle] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [exampleTask, setExampleTask] = useState('');
  const [processedCriteria, setProcessedCriteria] = useState([]);
  const [deadline, setDeadline] = useState('');
  const [loading, setLoading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [showPreview, setShowPreview] = useState(false);

  const processExampleTask = async () => {
    if (!jobTitle.trim() || !jobDescription.trim() || !exampleTask.trim()) {
      message.warning('Please fill in job title, description, and example task before processing');
      return;
    }

    setProcessing(true);
    try {
      const result = await apiService.processExampleTask({
        job_title: jobTitle,
        job_description: jobDescription,
        example_task: exampleTask
      });

      if (result.success) {
        setProcessedCriteria(result.processed_criteria);
        setShowPreview(true);
        message.success('Example task processed successfully!');
      } else {
        message.error('Failed to process example task');
      }
    } catch (error) {
      message.error('Error processing example task: ' + error.message);
    } finally {
      setProcessing(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (processedCriteria.length === 0 && exampleTask.trim()) {
      message.warning('Please process the example task first or remove it');
      return;
    }

    setLoading(true);
    try {
      const postingData = {
        job_title: jobTitle,
        job_description: jobDescription,
        example_task: exampleTask || null,
        deadline: deadline || null,
        company: user.email
      };

      const newPosting = await apiService.createPosting(postingData);
      onPostingCreated(newPosting);
      resetForm();
      message.success('Job posting created successfully!');
    } catch (error) {
      message.error('Failed to create job posting: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setJobTitle('');
    setJobDescription('');
    setExampleTask('');
    setProcessedCriteria([]);
    setDeadline('');
    setShowPreview(false);
  };

  const handleClose = () => {
    resetForm();
    onClose();
  };

  const removeCriterion = (index) => {
    setProcessedCriteria(prev => prev.filter((_, i) => i !== index));
  };

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Create Job Posting" maxWidth="2xl">
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Component 1: Manual Job Input */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-white mb-3">Job Information</h3>
          
          <Input
            label="Job Title"
            value={jobTitle}
            onChange={(e) => setJobTitle(e.target.value)}
            required
            placeholder="e.g., Frontend Developer, Data Analyst, UX Designer"
          />

          <div>
            <label className="block text-sm font-medium text-zinc-300 mb-2">Job Description</label>
            <textarea
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              rows={4}
              className="w-full px-4 py-2 bg-black border border-zinc-700 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none text-white"
              placeholder="Describe the role, responsibilities, and requirements..."
              required
            />
          </div>
        </div>

        {/* Component 2: AI-Processed Criteria */}
        <div className="border-t border-zinc-700 pt-6">
          <h3 className="text-lg font-semibold text-white mb-3">Evaluation Criteria (AI-Powered)</h3>
          
          <div>
            <label className="block text-sm font-medium text-zinc-300 mb-2">
              Example Task (Optional)
              <span className="text-xs text-zinc-500 ml-2">
                Provide an example task - AI will generate filtered evaluation criteria
              </span>
            </label>
            <textarea
              value={exampleTask}
              onChange={(e) => setExampleTask(e.target.value)}
              rows={4}
              className="w-full px-4 py-2 bg-black border border-zinc-700 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none text-white"
              placeholder="Example: Create a responsive dashboard showing sales metrics with filtering capabilities..."
            />
            
            {exampleTask.trim() && (
              <div className="mt-3 flex space-x-3">
                <Button
                  type="button"
                  onClick={processExampleTask}
                  disabled={processing}
                  variant="secondary"
                  size="sm"
                >
                  <Sparkles className="w-4 h-4 mr-2" />
                  {processing ? 'Processing...' : 'Process with AI'}
                </Button>
                
                {processedCriteria.length > 0 && (
                  <Button
                    type="button"
                    onClick={() => setShowPreview(!showPreview)}
                    variant="secondary"
                    size="sm"
                  >
                    <Eye className="w-4 h-4 mr-2" />
                    {showPreview ? 'Hide' : 'Show'} Criteria
                  </Button>
                )}
              </div>
            )}
          </div>

          {/* AI-Generated Criteria Preview */}
          {showPreview && processedCriteria.length > 0 && (
            <div className="mt-4 p-4 bg-zinc-900 border border-zinc-700 rounded-lg">
              <h4 className="text-sm font-medium text-zinc-300 mb-3">
                AI-Generated Evaluation Criteria:
              </h4>
              <div className="space-y-2">
                {processedCriteria.map((criterion, index) => (
                  <div key={index} className="flex items-center justify-between bg-black px-3 py-2 rounded border border-zinc-800">
                    <span className="text-sm text-white">{criterion}</span>
                    <Button
                      type="button"
                      onClick={() => removeCriterion(index)}
                      variant="secondary"
                      size="sm"
                    >
                      <X className="w-3 h-3" />
                    </Button>
                  </div>
                ))}
              </div>
              <p className="text-xs text-zinc-500 mt-2">
                ✓ Sensitive information filtered • ✓ Criteria standardized
              </p>
            </div>
          )}
        </div>

        <Input
          label="Application Deadline (Optional)"
          type="date"
          value={deadline}
          onChange={(e) => setDeadline(e.target.value)}
        />

        <div className="flex justify-end space-x-3 pt-4 border-t border-zinc-700">
          <Button
            type="button"
            onClick={handleClose}
            variant="secondary"
          >
            Cancel
          </Button>
          <Button 
            type="submit"
            disabled={loading}
          >
            {loading ? 'Creating...' : 'Create Job Posting'}
          </Button>
        </div>
      </form>
    </Modal>
  );
};

export default JobPostingCreation;