import React, { useState, useEffect } from 'react';
import { Trophy, Star, ThumbsUp, ThumbsDown, User, Calendar, ChevronDown, ChevronUp, Image } from 'lucide-react';
import Modal from '../ui/Modal';
import Button from '../ui/Button';
import apiService from '../../services/api';

const EvaluationResults = ({ taskId, isOpen, onClose }) => {
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedSubmissions, setExpandedSubmissions] = useState(new Set());

  useEffect(() => {
    if (isOpen && taskId) {
      loadSubmissions();
    }
  }, [isOpen, taskId]);

  const loadSubmissions = async () => {
    try {
      setLoading(true);
      const data = await apiService.getSubmissions(taskId);
      // Sort by rank (lower rank number = better position)
      const sortedSubmissions = data.sort((a, b) => (a.rank || 999) - (b.rank || 999));
      setSubmissions(sortedSubmissions);
    } catch (error) {
      console.error('Failed to load submissions:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRankColor = (rank) => {
    if (rank === 1) return 'text-yellow-400';
    if (rank === 2) return 'text-gray-300';
    if (rank === 3) return 'text-amber-600';
    return 'text-zinc-400';
  };

  const getRankIcon = (rank) => {
    if (rank <= 3) {
      return <Trophy className={`w-5 h-5 ${getRankColor(rank)}`} />;
    }
    return <span className="w-5 h-5 flex items-center justify-center text-zinc-400 font-bold">#{rank}</span>;
  };

  const toggleSubmissionDetails = (submissionId) => {
    setExpandedSubmissions(prev => {
      const newSet = new Set(prev);
      if (newSet.has(submissionId)) {
        newSet.delete(submissionId);
      } else {
        newSet.add(submissionId);
      }
      return newSet;
    });
  };

  const getScreenshots = (submission) => {
    if (!submission.key_frames || submission.key_frames.length === 0) {
      return [];
    }
    
    // Take first 3 screenshots
    return submission.key_frames.slice(0, 3);
  };

  if (!isOpen) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Evaluation Results" size="large">
      <div className="space-y-6">
        {loading ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500 mx-auto"></div>
            <p className="text-zinc-400 mt-2">Loading results...</p>
          </div>
        ) : submissions.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-zinc-400">No submissions found for this task.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {submissions.map((submission, index) => (
              <div key={submission.id} className="bg-zinc-900 rounded-lg border border-zinc-800 p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    {getRankIcon(submission.rank)}
                    <div>
                      <h3 className="text-lg font-semibold text-white flex items-center">
                        <User className="w-4 h-4 mr-2" />
                        {submission.applicant_name}
                      </h3>
                      <p className="text-sm text-zinc-400 flex items-center">
                        <Calendar className="w-4 h-4 mr-1" />
                        Submitted: {new Date(submission.submitted_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="text-right">
                      <div className="flex items-center space-x-2">
                        <Star className="w-5 h-5 text-yellow-400" />
                        <span className="text-xl font-bold text-white">
                          {submission.percentile ? `${submission.percentile}%` : 'N/A'}
                        </span>
                      </div>
                      <p className="text-sm text-zinc-400">Percentile</p>
                    </div>
                    <Button
                      onClick={() => toggleSubmissionDetails(submission.id)}
                      variant="secondary"
                      size="sm"
                    >
                      {expandedSubmissions.has(submission.id) ? (
                        <>
                          <ChevronUp className="w-4 h-4 mr-1" />
                          Hide Screenshots
                        </>
                      ) : (
                        <>
                          <ChevronDown className="w-4 h-4 mr-1" />
                          Show Screenshots
                        </>
                      )}
                    </Button>
                  </div>
                </div>

                {submission.feedback && (
                  <div className="mb-4">
                    <h4 className="text-sm font-medium text-zinc-300 mb-2">Feedback:</h4>
                    <p className="text-zinc-400 bg-zinc-800 rounded p-3">{submission.feedback}</p>
                  </div>
                )}

                {submission.pros_cons && (
                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <h4 className="text-sm font-medium text-green-400 mb-2 flex items-center">
                        <ThumbsUp className="w-4 h-4 mr-1" />
                        Strengths
                      </h4>
                      <ul className="space-y-1">
                        {submission.pros_cons.pros?.map((pro, idx) => (
                          <li key={idx} className="text-sm text-zinc-400 flex items-start">
                            <span className="text-green-400 mr-2">•</span>
                            {pro}
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <h4 className="text-sm font-medium text-red-400 mb-2 flex items-center">
                        <ThumbsDown className="w-4 h-4 mr-1" />
                        Areas for Improvement
                      </h4>
                      <ul className="space-y-1">
                        {submission.pros_cons.cons?.map((con, idx) => (
                          <li key={idx} className="text-sm text-zinc-400 flex items-start">
                            <span className="text-red-400 mr-2">•</span>
                            {con}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}

                {expandedSubmissions.has(submission.id) && (
                  <div className="mt-4 pt-4 border-t border-zinc-800">
                    <h4 className="text-sm font-medium text-zinc-300 mb-3 flex items-center">
                      <Image className="w-4 h-4 mr-2" />
                      Video Screenshots
                    </h4>
                    {getScreenshots(submission).length > 0 ? (
                      <div className="grid grid-cols-3 gap-4">
                        {getScreenshots(submission).map((frame, idx) => (
                          <div key={idx} className="aspect-video bg-zinc-800 rounded-lg overflow-hidden border border-zinc-700">
                            <img
                              src={apiService.getFrameUrl(frame)}
                              alt={`Screenshot ${idx + 1}`}
                              className="w-full h-full object-cover"
                              onError={(e) => {
                                e.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjEwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjMzc0MTUxIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzljYTNhZiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkltYWdlIG5vdCBmb3VuZDwvdGV4dD48L3N2Zz4=';
                              }}
                            />
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-8 text-zinc-400">
                        <Image className="w-12 h-12 mx-auto mb-2 opacity-50" />
                        <p>No screenshots available</p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        <div className="flex justify-end pt-4">
          <Button onClick={onClose} variant="secondary">
            Close
          </Button>
        </div>
      </div>
    </Modal>
  );
};

export default EvaluationResults;
