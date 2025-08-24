import React, { useState } from 'react';
import { Upload, X, FileVideo, FileArchive } from 'lucide-react';
import { useToast } from '../ui/Toast';
import Modal from '../ui/Modal';
import Button from '../ui/Button';
import apiService from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';

const TaskSubmission = ({ task, isOpen, onClose }) => {
  const { user } = useAuth();
  const { message } = useToast();
  const [videoFile, setVideoFile] = useState(null);
  const [codeFile, setCodeFile] = useState(null);
  const [uploading, setUploading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!videoFile || !codeFile) return;

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('task_id', task.id);
      formData.append('applicant_email', user.email);
      formData.append('video', videoFile);
      formData.append('code', codeFile);

      await apiService.createSubmission(formData);
      message.success('Submission successful!');
      setVideoFile(null);
      setCodeFile(null);
      onClose();
    } catch (error) {
      message.error('Submission failed: ' + error.message);
    } finally {
      setUploading(false);
    }
  };

  const handleClose = () => {
    setVideoFile(null);
    setCodeFile(null);
    setUploading(false);
    onClose();
  };

  if (!task) return null;

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title={`Submit Solution for: ${task.title || task.job_title}`}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-zinc-300 mb-2">
            Demo Video (MP4, max 100MB)
          </label>
          <div className="border-2 border-dashed border-zinc-700 rounded-lg p-6 text-center">
            <input
              type="file"
              accept="video/mp4"
              onChange={(e) => setVideoFile(e.target.files[0])}
              className="hidden"
              id="video-upload"
            />
            <label htmlFor="video-upload" className="cursor-pointer">
              <FileVideo className="w-12 h-12 mx-auto mb-2 text-zinc-500" />
              <p className="text-zinc-400">
                {videoFile ? videoFile.name : 'Click to upload video'}
              </p>
            </label>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-zinc-300 mb-2">
            Code/Artifacts (ZIP file)
          </label>
          <div className="border-2 border-dashed border-zinc-700 rounded-lg p-6 text-center">
            <input
              type="file"
              accept=".zip"
              onChange={(e) => setCodeFile(e.target.files[0])}
              className="hidden"
              id="code-upload"
            />
            <label htmlFor="code-upload" className="cursor-pointer">
              <FileArchive className="w-12 h-12 mx-auto mb-2 text-zinc-500" />
              <p className="text-zinc-400">
                {codeFile ? codeFile.name : 'Click to upload code'}
              </p>
            </label>
          </div>
        </div>

        <div className="flex justify-end space-x-3 pt-4">
          <Button
            type="button"
            onClick={handleClose}
            variant="secondary"
          >
            Cancel
          </Button>
          <Button
            type="submit"
            disabled={!videoFile || !codeFile || uploading}
          >
            {uploading ? 'Uploading...' : 'Submit'}
          </Button>
        </div>
      </form>
    </Modal>
  );
};

export default TaskSubmission;
