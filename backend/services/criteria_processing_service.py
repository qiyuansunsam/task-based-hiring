import json
import requests
import time
import re
from typing import List, Dict

class CriteriaProcessingService:
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
    
    def process_example_task(self, example_task: str, job_title: str, job_description: str) -> List[str]:
        """
        Process example task through Claude API to generate well-defined criteria
        with sensitive information filtering
        """
        try:
            # Create processing prompt
            prompt = self._create_criteria_prompt(example_task, job_title, job_description)
            
            # Make API call with retry logic
            response = self._make_api_call_with_retry(prompt)
            
            # Parse and clean criteria
            criteria = self._parse_criteria_response(response)
            
            # Apply sensitive information filtering
            filtered_criteria = self._filter_sensitive_information(criteria)
            
            return filtered_criteria
            
        except Exception as e:
            print(f"Error in criteria processing: {e}")
            # Fallback to basic criteria if API fails
            return self._fallback_criteria(job_title)
    
    def _create_criteria_prompt(self, example_task: str, job_title: str, job_description: str) -> str:
        """
        Create detailed prompt for criteria generation
        """
        return f"""You are an expert HR professional tasked with creating evaluation criteria for job applicants. 

JOB TITLE: {job_title}

JOB DESCRIPTION: {job_description}

EXAMPLE TASK PROVIDED BY EMPLOYER:
{example_task}

Based on the job requirements and the example task, generate 4-6 specific, measurable evaluation criteria that can be used to assess applicant submissions. Each criterion should be:

1. SPECIFIC: Clear and unambiguous
2. MEASURABLE: Can be objectively evaluated
3. RELEVANT: Directly related to job requirements
4. PROFESSIONAL: Use formal, standardized language

IMPORTANT FILTERING REQUIREMENTS:
- Remove any company names, proprietary information, or internal processes
- Remove personal information, email addresses, phone numbers
- Remove specific client names or confidential business details
- Generalize any industry-specific jargon to be more universally applicable
- Focus on skills, competencies, and deliverable quality rather than company-specific requirements

Return your response as a JSON array of strings, with each string being one evaluation criterion.

Example format:
["Technical implementation quality and code structure", "User interface design and user experience", "Problem-solving approach and creativity", "Documentation quality and clarity"]

Criteria:"""

    def _make_api_call_with_retry(self, prompt: str, max_retries: int = 3) -> Dict:
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
            "max_tokens": 1000,
            "messages": [{"role": "user", "content": prompt}]
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
    
    def _parse_criteria_response(self, response: Dict) -> List[str]:
        """
        Parse Claude's response into criteria list
        """
        try:
            content = response.get('content', [{}])[0].get('text', '')
            
            # Try to extract JSON from response
            start_idx = content.find('[')
            end_idx = content.rfind(']') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = content[start_idx:end_idx]
                criteria = json.loads(json_str)
                
                # Ensure we have a list of strings
                if isinstance(criteria, list) and all(isinstance(c, str) for c in criteria):
                    return criteria
            
            # If JSON parsing fails, try to extract criteria from text
            return self._extract_criteria_from_text(content)
            
        except Exception as e:
            print(f"Error parsing criteria response: {e}")
            return []
    
    def _extract_criteria_from_text(self, text: str) -> List[str]:
        """
        Extract criteria from unstructured text response
        """
        criteria = []
        
        # Look for numbered lists or bullet points
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            # Match numbered lists (1., 2., etc.) or bullet points (-, *, •)
            if re.match(r'^[\d]+\.|\-|\*|•', line):
                # Clean up the line by removing numbering/bullets and quotes
                clean_line = re.sub(r'^[\d]+\.|\-|\*|•|"', '', line).strip()
                clean_line = clean_line.strip('"').strip()
                if len(clean_line) > 10 and len(clean_line) < 150:  # Reasonable length
                    criteria.append(clean_line)
        
        return criteria[:6] if criteria else []  # Limit to 6 criteria
    
    def _filter_sensitive_information(self, criteria: List[str]) -> List[str]:
        """
        Filter out sensitive information from criteria
        """
        filtered_criteria = []
        
        # Patterns to identify and remove sensitive information
        sensitive_patterns = [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email addresses
            r'\b\d{3}-\d{3}-\d{4}\b',  # Phone numbers
            r'\b\d{3}\.\d{3}\.\d{4}\b',  # Phone numbers with dots
            r'\([0-9]{3}\)\s*[0-9]{3}-[0-9]{4}',  # Phone numbers with parentheses
            r'\b[A-Z][a-z]+ (?:Inc|LLC|Corp|Ltd|Company)\b',  # Company names
            r'\bconfidential\b|\bproprietary\b|\binternal\b',  # Sensitive keywords
        ]
        
        # Generic replacements
        generic_replacements = {
            'our company': 'the organization',
            'our client': 'the client',
            'our team': 'the team',
            'our product': 'the product',
            'our system': 'the system',
            'our platform': 'the platform',
        }
        
        for criterion in criteria:
            if not criterion or len(criterion.strip()) < 10:
                continue
                
            filtered_criterion = criterion.lower()
            
            # Remove sensitive patterns
            for pattern in sensitive_patterns:
                filtered_criterion = re.sub(pattern, '[REDACTED]', filtered_criterion, flags=re.IGNORECASE)
            
            # Apply generic replacements
            for specific, generic in generic_replacements.items():
                filtered_criterion = filtered_criterion.replace(specific, generic)
            
            # Skip if too much was redacted
            if '[REDACTED]' in filtered_criterion and filtered_criterion.count('[REDACTED]') > 2:
                continue
            
            # Capitalize first letter
            filtered_criterion = filtered_criterion[0].upper() + filtered_criterion[1:] if filtered_criterion else ""
            
            filtered_criteria.append(filtered_criterion)
        
        return filtered_criteria
    
    def _fallback_criteria(self, job_title: str) -> List[str]:
        """
        Fallback criteria if API processing fails
        """
        generic_criteria = [
            "Technical implementation quality and code structure",
            "Problem-solving approach and methodology",
            "User interface design and user experience",
            "Code documentation and clarity",
            "Creative solution and innovation",
            "Overall project presentation and completeness"
        ]
        
        # Try to customize based on job title
        if 'developer' in job_title.lower() or 'engineer' in job_title.lower():
            return generic_criteria
        elif 'designer' in job_title.lower():
            return [
                "Visual design quality and aesthetics",
                "User experience and interface usability",
                "Creative problem-solving approach",
                "Design consistency and attention to detail",
                "Presentation and communication of design decisions"
            ]
        elif 'data' in job_title.lower() or 'analyst' in job_title.lower():
            return [
                "Data analysis accuracy and methodology",
                "Visualization clarity and effectiveness",
                "Problem-solving approach and insights",
                "Documentation and explanation quality",
                "Technical implementation and tools usage"
            ]
        else:
            return generic_criteria