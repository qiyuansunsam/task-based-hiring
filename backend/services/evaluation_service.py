import base64
import os
from typing import List, Dict, Any, Optional

class BSTNode:
    """Binary Search Tree Node for submission ranking"""
    def __init__(self, submission: Dict):
        self.submission = submission
        self.left: Optional['BSTNode'] = None
        self.right: Optional['BSTNode'] = None

class EvaluationService:
    def __init__(self):
        self.comparison_cache = {}
        self.progress_callback = None
    
    def rank_submissions(self, submissions: List[Dict], task_description: str, 
                        criteria: List[str], llm_service, progress_callback=None) -> List[Dict]:
        """
        Use BST-based sorting for guaranteed O(n log n) average complexity
        """
        if len(submissions) <= 1:
            if len(submissions) == 1:
                submissions[0]['percentile'] = 100.0
            return submissions
        
        self.progress_callback = progress_callback
        self.current_submission = 0
        self.total_submissions = len(submissions)
        self.comparison_count = 0
        
        # Build BST with LLM comparisons
        ranked = self._bst_sort_submissions(submissions, task_description, criteria, llm_service)
        
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
    
    def _bst_sort_submissions(self, submissions: List[Dict], task_desc: str, 
                             criteria: List[str], llm_service) -> List[Dict]:
        """
        Sort submissions using BST with LLM comparisons
        """
        if not submissions:
            return []
        
        # Initialize BST with first submission
        root = BSTNode(submissions[0])
        if self.progress_callback:
            self.progress_callback(f"Evaluating submission 1/{self.total_submissions}: {submissions[0]['applicant_name']}")
        
        # Insert remaining submissions into BST
        for i, submission in enumerate(submissions[1:], 2):
            self.current_submission = i
            if self.progress_callback:
                self.progress_callback(f"Evaluating submission {i}/{self.total_submissions}: {submission['applicant_name']}")
            self._insert_into_bst(root, submission, task_desc, criteria, llm_service)
        
        # Perform in-order traversal to get sorted list (best to worst)
        ranked = []
        self._inorder_traversal_reverse(root, ranked)
        
        return ranked
    
    def _insert_into_bst(self, root: BSTNode, submission: Dict, task_desc: str, 
                        criteria: List[str], llm_service):
        """
        Insert submission into BST based on LLM comparison
        """
        self.comparison_count += 1
        
        # Report progress for each comparison (API call)
        if self.progress_callback:
            self.progress_callback(f"Comparing {submission['applicant_name']} vs {root.submission['applicant_name']} (API call {self.comparison_count})")
        
        comparison = self._compare_submissions(submission, root.submission, task_desc, criteria, llm_service)
        
        # Store feedback for both submissions
        submission['feedback'] = comparison['feedback_a']
        submission['pros_cons'] = comparison['pros_cons_a']
        root.submission['feedback'] = comparison['feedback_b']
        root.submission['pros_cons'] = comparison['pros_cons_b']
        
        if comparison['winner'] == 'A':  # New submission is better
            if root.right is None:
                root.right = BSTNode(submission)
            else:
                self._insert_into_bst(root.right, submission, task_desc, criteria, llm_service)
        else:  # Current root submission is better
            if root.left is None:
                root.left = BSTNode(submission)
            else:
                self._insert_into_bst(root.left, submission, task_desc, criteria, llm_service)
    
    def _inorder_traversal_reverse(self, node: BSTNode, result: List[Dict]):
        """
        Reverse in-order traversal to get submissions from best to worst
        """
        if node is not None:
            # Visit right subtree first (better submissions)
            self._inorder_traversal_reverse(node.right, result)
            # Visit current node
            result.append(node.submission)
            # Visit left subtree (worse submissions)
            self._inorder_traversal_reverse(node.left, result)
    
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
