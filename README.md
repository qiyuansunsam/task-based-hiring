# SkillsFoundry 🚀

**AI-Powered Skills Assessment Platform**

SkillsFoundry is an innovative platform that uses AI to evaluate technical skills through practical task submissions. Companies can create coding challenges, and applicants submit video demonstrations of their solutions, which are then evaluated using advanced AI analysis.

## ✨ Features

### For Companies
- **Task Creation**: Design custom coding challenges and technical assessments
- **AI-Powered Evaluation**: Automated evaluation using Claude AI with advanced screenshot analysis
- **Intelligent Ranking**: Tournament-style comparison system for reliable candidate rankings
- **Detailed Feedback**: Comprehensive feedback and pros/cons analysis for each submission
- **Advanced Feature Detection**: Recognizes complex implementations like demos, downloads, pagination, and state management

### For Applicants
- **Video Submissions**: Submit screen recordings demonstrating your solutions
- **Portfolio Building**: Build a portfolio of completed technical challenges
- **Detailed Feedback**: Receive constructive feedback on your technical implementations
- **Percentile Rankings**: See how your submissions rank against other candidates

### AI Evaluation Capabilities
- **Screenshot Quality Handling**: Forgiving of poor video quality and timing issues
- **Technical Depth Detection**: Identifies advanced features that may not be visible in static frames
- **Interactivity Recognition**: Detects mouse movement, hover states, and dynamic interactions
- **Framework Recognition**: Distinguishes between React/Vue/Angular vs vanilla JavaScript implementations
- **Architecture Assessment**: Evaluates technical complexity and implementation sophistication

## 🛠️ Technology Stack

### Backend
- **Python 3.8+** with Flask
- **SQLite** database
- **OpenCV** for video frame extraction
- **Claude AI API** for intelligent evaluation
- **Base64 encoding** for image processing

### Frontend
- **React 18** with modern hooks
- **Vite** for fast development and building
- **Tailwind CSS** for styling
- **Lucide React** for icons
- **Responsive design** for all devices

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

Run the setup script which will handle everything for you:

```bash
chmod +x setup.sh
./setup.sh
```

The script will:
- Check for required dependencies (Python, Node.js, npm)
- Install Python and Node.js dependencies
- Prompt for your Claude API key
- Create environment files
- Set up the database
- Start both backend and frontend servers

### Option 2: Manual Setup

If you prefer to set up manually, follow these steps:

#### Prerequisites
- **Python 3.8+**
- **Node.js 16+**
- **npm or yarn**
- **Claude API Key** (from Anthropic)

#### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create environment file:**
   ```bash
   cp .env.example .env
   ```

5. **Add your Claude API key to `.env`:**
   ```
   ANTHROPIC_API_KEY=your_claude_api_key_here
   ```

6. **Initialize database:**
   ```bash
   python app.py
   ```

#### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```
ANTHROPIC_API_KEY=your_claude_api_key_here
FLASK_ENV=development
FLASK_DEBUG=True
```

#### Frontend (.env)
```
VITE_API_URL=http://localhost:5000
```

### Claude API Key

To get a Claude API key:
1. Visit [Anthropic's website](https://www.anthropic.com/)
2. Sign up for an account
3. Navigate to the API section
4. Generate a new API key
5. Add it to your backend `.env` file

## 🎯 Usage

### For Companies

1. **Login** with a company account (demo: `demo@test.com` / password: `123`)
2. **Create Tasks** by defining:
   - Task title and description
   - Evaluation criteria
   - Submission deadline
3. **Review Submissions** as they come in
4. **View AI Evaluations** with detailed feedback and rankings

### For Applicants

1. **Login** with an applicant account (demo accounts available)
2. **Browse Available Tasks** and select ones to complete
3. **Submit Video Demonstrations** showing your solution in action
4. **View Feedback** and build your portfolio of completed challenges

### Demo Accounts

The platform includes several demo accounts for testing:

- **Company Account**: `demo@test.com` (password: `123`)
- **Applicant Accounts**:
  - `custom@test.com` (password: `123`)
  - `gpt@test.com` (password: `123`)
  - `gemini@test.com` (password: `123`)
  - `deepseek@test.com` (password: `123`)

## 🧠 AI Evaluation System

### Advanced Features

SkillsFoundry's AI evaluation system is designed to be fair and comprehensive:

#### Screenshot Quality Handling
- **Forgiving Analysis**: Understands that video frames may show loading states or transitional moments
- **Technical Focus**: Prioritizes evidence of technical implementation over visual presentation
- **Benefit of Doubt**: Gives submissions credit for functionality that may not be clearly visible

#### Feature Detection
The AI specifically looks for and rewards:
- **Download/Export Functionality**: File downloads, PDF generation, save features
- **Media Integration**: Image galleries, video players, custom uploads
- **Pagination/Navigation**: Complex routing, page controls, infinite scroll
- **State Management**: Loading states, form validation, dynamic updates
- **Interactive Demos**: Live previews, dynamic demonstrations
- **Advanced UI Components**: Modals, dropdowns, accordions, carousels

#### Technical Hierarchy
Submissions are evaluated with this priority:
1. **Technical Architecture** - Framework usage, complexity, modern practices
2. **Functional Completeness** - Meeting task requirements
3. **Implementation Quality** - Code structure, best practices
4. **User Experience** - Design and usability
5. **Interactive Features** - Dynamic behavior and user interaction

### Ranking System

- **Tournament-Style Comparisons**: Every submission is compared against every other submission
- **Win-Rate Based**: Rankings determined by head-to-head comparison results
- **Consistent Results**: Eliminates order-dependent ranking issues
- **Percentile Scores**: Clear percentile rankings from 0-100%

## 📁 Project Structure

```
skillsfoundry/
├── backend/
│   ├── app.py                 # Flask application entry point
│   ├── database.py            # Database models and setup
│   ├── requirements.txt       # Python dependencies
│   ├── services/
│   │   ├── evaluation_service.py      # Tournament-style ranking
│   │   ├── llm_service.py            # Claude AI integration
│   │   ├── frame_extraction_service.py # Video frame processing
│   │   └── criteria_processing_service.py
│   ├── models/               # Data models
│   ├── uploads/             # Video file storage
│   └── extracted_frames/    # Processed video frames
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── auth/        # Authentication components
│   │   │   ├── company/     # Company dashboard components
│   │   │   ├── applicant/   # Applicant dashboard components
│   │   │   ├── common/      # Shared components
│   │   │   └── ui/          # UI components
│   │   ├── contexts/        # React contexts
│   │   ├── services/        # API services
│   │   └── App.jsx         # Main application component
│   ├── package.json
│   └── vite.config.js
├── setup.sh                # Automated setup script
└── README.md               # This file
```

## 🔍 Testing

### Test the Evaluation System

A test script is included to verify the AI evaluation improvements:

```bash
python test_improved_evaluation.py
```

This tests:
- Interactivity detection algorithms
- Frame extraction improvements
- Evaluation prompt enhancements

## 🚨 Troubleshooting

### Common Issues

1. **"ANTHROPIC_API_KEY environment variable is required"**
   - Make sure you've added your Claude API key to the backend `.env` file

2. **Port already in use**
   - Backend runs on port 5000, frontend on port 5173
   - Kill existing processes: `lsof -ti:5000 | xargs kill -9`

3. **Video upload issues**
   - Ensure the `backend/uploads/` directory exists and is writable
   - Check file size limits in your system

4. **Database issues**
   - Delete `backend/database.db` and restart the backend to recreate
