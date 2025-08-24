import React, { useState } from 'react';
import { Trophy, ChevronDown, ChevronUp, CheckCircle, X } from 'lucide-react';

const Portfolio = ({ portfolio }) => {
  const [expandedItem, setExpandedItem] = useState(null);

  if (portfolio.length === 0) {
    return (
      <div>
        <h3 className="text-xl font-bold mb-4">My Portfolio</h3>
        <div className="bg-zinc-900 rounded-lg border border-zinc-800 p-8 text-center">
          <Trophy className="w-12 h-12 mx-auto mb-3 text-zinc-600" />
          <p className="text-zinc-400">No completed tasks yet. Start submitting to build your portfolio!</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <h3 className="text-xl font-bold mb-4">My Portfolio</h3>
      <div className="space-y-3">
        {portfolio.map((item, idx) => (
          <div key={idx} className="bg-zinc-900 rounded-lg border border-zinc-800 overflow-hidden">
            <button
              onClick={() => setExpandedItem(expandedItem === idx ? null : idx)}
              className="w-full p-4 flex items-center justify-between hover:bg-zinc-800 transition"
            >
              <div className="flex items-center space-x-4">
                <div className={`p-2 rounded-lg ${
                  item.rank === 1 ? 'bg-yellow-900 text-yellow-400' :
                  item.rank === 2 ? 'bg-gray-700 text-gray-300' :
                  item.rank === 3 ? 'bg-orange-900 text-orange-400' :
                  'bg-zinc-800 text-zinc-400'
                }`}>
                  <Trophy className="w-5 h-5" />
                </div>
                <div className="text-left">
                  <h4 className="font-semibold text-white">{item.task_title}</h4>
                  <p className="text-sm text-zinc-400">
                    Rank #{item.rank} of {item.total_submissions} • Percentile: {item.percentile || item.score}%
                  </p>
                </div>
              </div>
              {expandedItem === idx ? <ChevronUp /> : <ChevronDown />}
            </button>
            
            {expandedItem === idx && (
              <div className="p-4 border-t border-zinc-800">
                <div className="space-y-3">
                  <div>
                    <h5 className="font-medium text-purple-400 mb-1">Feedback</h5>
                    <p className="text-zinc-300">{item.feedback}</p>
                  </div>
                  
                  {(() => {
                    let prosConsData = null;
                    
                    // Handle different data formats for pros_cons
                    if (item.pros_cons) {
                      if (typeof item.pros_cons === 'string') {
                        try {
                          prosConsData = JSON.parse(item.pros_cons);
                        } catch (e) {
                          console.warn('Failed to parse pros_cons JSON in portfolio:', e);
                          prosConsData = null;
                        }
                      } else if (typeof item.pros_cons === 'object') {
                        prosConsData = item.pros_cons;
                      }
                    }

                    // Only render if we have valid data
                    if (prosConsData && (
                      (prosConsData.pros && Array.isArray(prosConsData.pros) && prosConsData.pros.length > 0) ||
                      (prosConsData.cons && Array.isArray(prosConsData.cons) && prosConsData.cons.length > 0)
                    )) {
                      return (
                        <div className="grid md:grid-cols-2 gap-4">
                          {/* Pros */}
                          {prosConsData.pros && Array.isArray(prosConsData.pros) && prosConsData.pros.length > 0 && (
                            <div>
                              <h5 className="font-medium text-green-400 mb-2">Pros</h5>
                              <ul className="space-y-1">
                                {prosConsData.pros.map((pro, i) => (
                                  <li key={i} className="text-sm text-zinc-400 flex items-start">
                                    <CheckCircle className="w-4 h-4 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                                    <span>{pro}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                          
                          {/* Cons */}
                          {prosConsData.cons && Array.isArray(prosConsData.cons) && prosConsData.cons.length > 0 && (
                            <div>
                              <h5 className="font-medium text-red-400 mb-2">Areas for Improvement</h5>
                              <ul className="space-y-1">
                                {prosConsData.cons.map((con, i) => (
                                  <li key={i} className="text-sm text-zinc-400 flex items-start">
                                    <X className="w-4 h-4 text-red-500 mr-2 mt-0.5 flex-shrink-0" />
                                    <span>{con}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      );
                    }
                    
                    return null;
                  })()}
                  
                  <div className="text-sm text-zinc-500">
                    Submitted: {new Date(item.submitted_at).toLocaleDateString()}
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default Portfolio;
