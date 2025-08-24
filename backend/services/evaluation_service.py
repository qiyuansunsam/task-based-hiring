import base64
import os
from typing import List, Dict, Any, Optional

class EvaluationService:
    def __init__(self):
        self.comparison_cache = {}
        self.progress_callback = None
    
    def rank_submissions(self, submissions: List[Dict], task_description: str, 
                        criteria: List[str], llm_service, progress_callback=None) -> List[Dict]:
        """
        Use tournament-style sorting for reliable ranking
        """
        if len(submissions) <= 1:
            if len(submissions) == 1:
                submissions[0]['percentile'] = 100.0
            return submissions
        
        self.progress_callback = progress_callback
        self.total_submissions = len(submissions)
        self.comparison_count = 0
        
        # Use tournament sorting for more reliable results
        ranked = self._tournament_sort_submissions(submissions, task_description, criteria, llm_service)
        
        # Assign percentiles based on ranking (best to worst)
        total = len(ranked)
        for idx, sub in enumerate(ranked):
            # Calculate percentile: top submission = 100th percentile, bottom = lowest percentile
            percentile = round(100 * (total - idx) / total, 1)
            sub['percentile'] = percentile
            # Remove old score field if it exists
            if 'score' in sub:
                del sub['score']
        
        return ranked
    
    def _tournament_sort_submissions(self, submissions: List[Dict], task_desc: str, 
                                   criteria: List[str], llm_service) -> List[Dict]:
        """
        Sort submissions using tournament-style comparisons for reliable ranking
        """
        if not submissions:
            return []
        
        # Create a copy to avoid modifying original
        remaining = submissions.copy()
        ranked = []
        
        # Build win matrix to track head-to-head results
        win_matrix = {}
        for sub in submissions:
            win_matrix[sub['id']] = {'wins': 0, 'total_comparisons': 0}
        
        # Perform round-robin comparisons to build reliable rankings
        for i in range(len(remaining)):
            for j in range(i + 1, len(remaining)):
                sub_a = remaining[i]
                sub_b = remaining[j]
                
                self.comparison_count += 1
                if self.progress_callback:
                    self.progress_callback(f"Comparing {sub_a['applicant_name']} vs {sub_b['applicant_name']} (Comparison {self.comparison_count})")
                
                comparison = self._compare_submissions(sub_a, sub_b, task_desc, criteria, llm_service)
                
                # Store feedback for both submissions (only if not already set)
                if 'feedback' not in sub_a:
                    sub_a['feedback'] = comparison['feedback_a']
                    sub_a['pros_cons'] = comparison['pros_cons_a']
                if 'feedback' not in sub_b:
                    sub_b['feedback'] = comparison['feedback_b']
                    sub_b['pros_cons'] = comparison['pros_cons_b']
                
                # Update win matrix
                if comparison['winner'] == 'A':
                    win_matrix[sub_a['id']]['wins'] += 1
                else:
                    win_matrix[sub_b['id']]['wins'] += 1
                
                win_matrix[sub_a['id']]['total_comparisons'] += 1
                win_matrix[sub_b['id']]['total_comparisons'] += 1
        
        # Calculate win rates and sort by them
        for sub in remaining:
            total_comps = win_matrix[sub['id']]['total_comparisons']
            if total_comps > 0:
                win_rate = win_matrix[sub['id']]['wins'] / total_comps
            else:
                win_rate = 0.0
            sub['_win_rate'] = win_rate
        
        # Sort by win rate (highest first)
        ranked = sorted(remaining, key=lambda x: x['_win_rate'], reverse=True)
        
        # Clean up temporary win rate field
        for sub in ranked:
            if '_win_rate' in sub:
                del sub['_win_rate']
        
        return ranked
    
    def _compare_submissions(self, sub_a: Dict, sub_b: Dict, task_desc: str, 
                           criteria: List[str], llm_service) -> Dict:
        """
        Compare two submissions using LLM
        """
        # Create comparison key for caching
        key = f"{sub_a['id']}_{sub_b['id']}"
        if key in self.comparison_cache:
            return self.comparison_cache[key]
        
        # Prepare frame data - use more frames now that we extract 8
        frames_a = self._encode_frames(sub_a['key_frames'][:4])  # Use top 4 frames
        frames_b = self._encode_frames(sub_b['key_frames'][:4])
        
        # Get LLM evaluation
        result = llm_service.evaluate_submissions(
            frames_a, frames_b, task_desc, criteria,
            sub_a['applicant_name'], sub_b['applicant_name']
        )
        
        self.comparison_cache[key] = result
        return result
    
    def _encode_frames(self, frame_paths: List[str]) -> List[str]:
        """
        Encode frames as base64 for LLM processing
        """
        encoded = []
        for path in frame_paths:
            if os.path.exists(path):
                with open(path, 'rb') as f:
                    encoded.append(base64.b64encode(f.read()).decode('utf-8'))
        return encoded
