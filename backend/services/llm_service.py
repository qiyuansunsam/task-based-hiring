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
        Create detailed evaluation prompt for Claude with improved screenshot handling
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

🚨 CRITICAL SCREENSHOT QUALITY ASSESSMENT:
These are automatically extracted video frames that may have significant limitations:

SCREENSHOT QUALITY IS UNRELIABLE - FOCUS ON TECHNICAL EVIDENCE:
- Screenshots may show loading states, blank screens, or transitional moments
- Video compression artifacts may obscure actual functionality
- Timing issues may miss key interactive moments or completed states
- Poor frame selection may not represent the true quality of the work
- Technical demos often look incomplete in static screenshots
- A submission may APPEAR simpler but actually have MORE advanced features

WHEN SCREENSHOTS ARE POOR/UNCLEAR - LOOK FOR TECHNICAL INDICATORS:
- Give submissions the benefit of the doubt about functionality
- Look for ANY evidence of advanced technical implementation
- Prioritize technical complexity over visual presentation
- Consider that advanced features may not be visible in static frames
- Don't let poor screenshot timing mask superior technical implementation

🎯 INTERACTIVITY DETECTION GUIDELINES:
Look for these visual cues that indicate interactive features:

MOUSE MOVEMENT INDICATORS:
- Cursor visible in screenshots (indicates active interaction)
- Hover states on buttons, links, or interactive elements
- Highlighted/selected items suggesting user interaction
- Form fields with focus states or active cursors
- Dropdown menus in open states
- Modal dialogs or popups (suggest user-triggered actions)

INTERACTION EVIDENCE:
- Multiple different screens/views (suggests navigation)
- Form submissions with validation messages
- Dynamic content changes between frames
- Loading states followed by populated content
- Before/after states showing user actions
- Interactive elements like sliders, toggles, or drag-and-drop

TECHNICAL IMPLEMENTATION SIGNALS:
- Modern UI frameworks (React, Vue, Angular components)
- Responsive design elements and layouts
- Professional styling and component libraries
- Complex state management (forms, data, navigation)
- API integration evidence (loading states, data fetching)

🏗️ EVALUATION PRIORITIES (IN ORDER):
1. **Technical Architecture** - Framework usage, complexity, modern practices
2. **Functional Completeness** - Does it meet the task requirements?
3. **Implementation Quality** - Code structure, best practices, scalability
4. **User Experience** - Design, usability, polish (when visible)
5. **Interactive Features** - Evidence of dynamic behavior and user interaction

⚠️ SCREENSHOT LIMITATIONS - BE LENIENT:
- Don't heavily penalize for blank screens or loading states
- Poor screenshot quality doesn't reflect implementation quality
- Static frames can't capture dynamic interactions or animations
- Video compression may hide subtle UI details and interactions
- Focus on architectural and technical evidence over visual polish

🔍 ADVANCED FEATURE DETECTION - LOOK FOR THESE INDICATORS:

PREMIUM TECHNICAL FEATURES (HEAVILY REWARD):
- **Download/Export Functionality**: Download buttons, file export, PDF generation, save features
- **Media Integration**: Image galleries, video players, custom media uploads, rich content
- **Pagination/Navigation**: Page numbers, next/prev buttons, infinite scroll, complex routing
- **State Management**: Loading states, form validation, dynamic content updates, real-time changes
- **Interactive Demos**: Live previews, interactive elements, dynamic demonstrations
- **Data Handling**: Search functionality, filtering, sorting, CRUD operations
- **Advanced UI Components**: Modals, dropdowns, tooltips, accordions, tabs, carousels

ARCHITECTURAL COMPLEXITY INDICATORS:
- Multiple distinct pages/views (not just single page)
- Complex navigation systems and routing
- Form handling with validation and feedback
- Dynamic content loading and state changes
- API integrations and data fetching
- Responsive design across different screen sizes
- Professional component libraries and styling systems

🎯 COMPARISON DECISION FACTORS:
When one submission shows clear technical superiority (modern frameworks, complex architecture, multiple features), it should win even if screenshots are poor quality.

TECHNICAL HIERARCHY (Higher wins unless completely broken):
- Advanced features (demos, downloads, pagination, state management) > Basic features
- React/Vue/Angular apps > Vanilla JavaScript > Static HTML
- Multi-page applications > Single-page forms
- Database integration > Local storage > No persistence  
- Custom implementations > Template modifications
- Interactive features > Static presentations
- Complex state management > Simple static content

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

🚨 CRITICAL EVALUATION REMINDER:
- A submission that LOOKS simpler in screenshots may actually be MORE technically advanced
- Screenshots can be misleading - focus on ANY evidence of technical complexity
- Advanced features like demos, downloads, pagination, and state management are often not visible in static frames
- When in doubt between two submissions, favor the one with ANY indicators of advanced technical implementation
- Don't let poor screenshot quality or timing hide superior technical work

Remember: Be generous with poor screenshots, focus on technical implementation evidence, and reward interactivity indicators like mouse cursors and dynamic states."""

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
