import React, { useState } from 'react';
import { X, Plus, Trash2 } from 'lucide-react';
import { useToast } from '../ui/Toast';
import Modal from '../ui/Modal';
import Button from '../ui/Button';
import Input from '../ui/Input';
import apiService from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';

const TaskCreation = ({ isOpen, onClose, onTaskCreated }) => {
  const { user } = useAuth();
  const { message } = useToast();
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [criteria, setCriteria] = useState(['']);
  const [deadline, setDeadline] = useState('');
  const [loading, setLoading] = useState(false);

  const addCriterion = () => {
    setCriteria([...criteria, '']);
  };

  const updateCriterion = (index, value) => {
    const updated = [...criteria];
    updated[index] = value;
    setCriteria(updated);
  };

  const removeCriterion = (index) => {
    setCriteria(criteria.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const filteredCriteria = criteria.filter(c => c.trim());
    
    if (filteredCriteria.length === 0) {
      message.warning('Please add at least one evaluation criterion');
      return;
    }

    setLoading(true);
    try {
      const taskData = {
        title,
        description,
        criteria: filteredCriteria,
        deadline: deadline || null,
        company: user.email
      };

      const newTask = await apiService.createTask(taskData);
      onTaskCreated(newTask);
      resetForm();
    } catch (error) {
      message.error('Failed to create task: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setTitle('');
    setDescription('');
    setCriteria(['']);
    setDeadline('');
  };

  const handleClose = () => {
    resetForm();
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Create New Task">
      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          label="Task Title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
        />

        <div>
          <label className="block text-sm font-medium text-zinc-300 mb-2">Description</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={4}
            className="w-full px-4 py-2 bg-black border border-zinc-700 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none text-white"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-zinc-300 mb-2">Evaluation Criteria</label>
          <div className="space-y-2">
            {criteria.map((criterion, index) => (
              <div key={index} className="flex space-x-2">
                <input
                  type="text"
                  value={criterion}
                  onChange={(e) => updateCriterion(index, e.target.value)}
                  placeholder={`Criterion ${index + 1}`}
                  className="flex-1 px-4 py-2 bg-black border border-zinc-700 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none text-white"
                />
                {criteria.length > 1 && (
                  <Button
                    type="button"
                    onClick={() => removeCriterion(index)}
                    variant="secondary"
                    size="sm"
                  >
                    <X className="w-4 h-4" />
                  </Button>
                )}
              </div>
            ))}
            <Button
              type="button"
              onClick={addCriterion}
              variant="secondary"
              size="sm"
            >
              <Plus className="w-4 h-4 mr-2" />
              Add Criterion
            </Button>
          </div>
        </div>

        <Input
          label="Deadline (Optional)"
          type="date"
          value={deadline}
          onChange={(e) => setDeadline(e.target.value)}
        />

        <div className="flex justify-end space-x-3 pt-4">
          <Button
            type="button"
            onClick={handleClose}
            variant="secondary"
          >
            Cancel
          </Button>
          <Button type="submit">
            Create Task
          </Button>
        </div>
      </form>
    </Modal>
  );
};

export default TaskCreation;
