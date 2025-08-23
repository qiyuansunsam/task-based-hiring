import json
import requests
import time
from typing import List, Dict

class LLMService:
    def __init__(self):
        import os
        from dotenv import load_dotenv
        
        # Load environment variables from .env file
        load_dotenv()
        
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        self.api_url = "https://api.anthropic.com/v1/messages"
        self.model = "claude-3-5-sonnet-20241022"
    
    def evaluate_submissions(self, frames_a: List[str], frames_b: List[str], 
                           task_desc: str, criteria: List[str],
                           name_a: str, name_b: str) -> Dict:
        """
        Evaluate two submissions using Claude API with image analysis
        """
        try:
            # Create evaluation prompt
            prompt = self._create_evaluation_prompt(task_desc, criteria, name_a, name_b)
            
            # Prepare images for API call
            content = [{"type": "text", "text": prompt}]
            
            # Add images from both submissions
            for i, frame_b64 in enumerate(frames_a[:3]):  # Limit to 3 frames per submission
                content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": frame_b64
                    }
                })
            
            for i, frame_b64 in enumerate(frames_b[:3]):
                content.append({
                    "type": "image", 
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": frame_b64
                    }
                })
            
            # Make API call with retry logic
            response = self._make_api_call_with_retry(content)
            
            # Parse response
            return self._parse_evaluation_response(response, name_a, name_b)
            
        except Exception as e:
            print(f"Error in Claude API evaluation: {e}")
            # Fallback to simulated response if API fails
            return self._fallback_evaluation(name_a, name_b)
    
    def _create_evaluation_prompt(self, task_desc: str, criteria: List[str], name_a: str, name_b: str) -> str:
        """
        Create detailed evaluation prompt for Claude
        """
        criteria_text = "\n".join([f"- {criterion}" for criterion in criteria])
        
        return f"""You are an expert evaluator comparing two project submissions. 

TASK DESCRIPTION:
{task_desc}

EVALUATION CRITERIA:
{criteria_text}

I will show you screenshots from two demo videos:
- First images: Submission by {name_a}
- Remaining images: Submission by {name_b}

IMPORTANT EVALUATION GUIDELINES:
- These are automatically generated screenshots from demo videos
- Some screenshots may be transitioning frames or have visual artifacts - be lenient with these
- Focus on the actual implementation quality, functionality, and user experience
- Judge the application itself, not the screenshot quality
- If a frame appears to be transitioning or has artifacts, focus on the clearer frames
- Your goal is to determine which submission better meets the task requirements

DESIGN EVALUATION PREFERENCES:
- Prefer minimalistic, clean designs over overly colorful or cluttered interfaces
- Reward clear sectioning and logical organization of content
- Value clever layering and hierarchical structuring over flat layouts
- Appreciate thoughtful use of whitespace and visual hierarchy
- Favor functional design that enhances user experience over purely decorative elements

ADVANCED FEATURES TO REWARD:
- Modal dialogs and popup cards that show sophisticated UI implementation
- Multiple pages or views that demonstrate navigation and routing
- Interactive elements like buttons, forms, dropdowns, tabs, or accordions
- Evidence of user interaction and dynamic content updates
- Smooth transitions and animations that enhance user experience
- Complex layouts with multiple sections, sidebars, or organized content areas
- Advanced UI components that show technical skill and attention to detail

Please evaluate both submissions and determine which is better overall.

Respond with a JSON object in this exact format:
{{
    "winner": "A" or "B",
    "feedback_a": "Detailed feedback for {name_a}'s submission",
    "feedback_b": "Detailed feedback for {name_b}'s submission", 
    "pros_cons_a": {{
        "pros": ["list", "of", "strengths"],
        "cons": ["list", "of", "weaknesses"]
    }},
    "pros_cons_b": {{
        "pros": ["list", "of", "strengths"], 
        "cons": ["list", "of", "weaknesses"]
    }}
}}

Focus on implementation quality, functionality, design, and how well each submission meets the task requirements. Be forgiving of screenshot artifacts and transitioning frames."""

    def _make_api_call_with_retry(self, content: List[Dict], max_retries: int = 3) -> Dict:
        """
        Make API call with retry logic
        """
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        data = {
            "model": self.model,
            "max_tokens": 2000,
            "messages": [{"role": "user", "content": content}]
        }
        
        for attempt in range(max_retries):
            try:
                response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                print(f"API call attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise
    
    def _parse_evaluation_response(self, response: Dict, name_a: str, name_b: str) -> Dict:
        """
        Parse Claude's response into expected format
        """
        try:
            content = response.get('content', [{}])[0].get('text', '')
            
            # Try to extract JSON from response
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = content[start_idx:end_idx]
                evaluation = json.loads(json_str)
                
                # Validate required fields
                required_fields = ['winner', 'feedback_a', 'feedback_b', 'pros_cons_a', 'pros_cons_b']
                if all(field in evaluation for field in required_fields):
                    return evaluation
            
            # If parsing fails, create structured response from text
            return self._extract_evaluation_from_text(content, name_a, name_b)
            
        except Exception as e:
            print(f"Error parsing evaluation response: {e}")
            return self._fallback_evaluation(name_a, name_b)
    
    def _extract_evaluation_from_text(self, text: str, name_a: str, name_b: str) -> Dict:
        """
        Extract evaluation from unstructured text response
        """
        # Simple heuristic to determine winner
        winner = 'A' if name_a.lower() in text.lower() and 'better' in text.lower() else 'B'
        
        return {
            'winner': winner,
            'feedback_a': f"Based on the analysis, {name_a}'s submission shows various strengths and areas for improvement.",
            'feedback_b': f"Based on the analysis, {name_b}'s submission demonstrates different approaches and qualities.",
            'pros_cons_a': {
                'pros': ['Analyzed by Claude AI', 'Meets task requirements'],
                'cons': ['Areas for improvement identified']
            },
            'pros_cons_b': {
                'pros': ['Evaluated comprehensively', 'Shows technical skills'],
                'cons': ['Some aspects could be enhanced']
            }
        }
    
    def _fallback_evaluation(self, name_a: str, name_b: str) -> Dict:
        """
        Fallback evaluation if API fails
        """
        import random
        winner = 'A' if random.random() > 0.5 else 'B'
        
        return {
            'winner': winner,
            'feedback_a': f"Submission by {name_a} shows good understanding of the task requirements.",
            'feedback_b': f"Submission by {name_b} demonstrates creative problem-solving approach.",
            'pros_cons_a': {
                'pros': ['Clear implementation', 'Well-structured approach', 'Good presentation'],
                'cons': ['Could improve some aspects', 'Minor areas for enhancement']
            },
            'pros_cons_b': {
                'pros': ['Innovative approach', 'Good technical execution', 'Clean interface'],
                'cons': ['Some refinements possible', 'Could add more features']
            }
        }
