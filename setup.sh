#!/bin/bash

# Simple SkillsFoundry Setup Script

echo "SkillsFoundry Setup"
echo "==================="

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "ERROR: Please run this script from the SkillsFoundry root directory"
    exit 1
fi

# Get Claude API key
echo
echo "You need a Claude API key from https://www.anthropic.com/"
echo -n "Enter your Claude API key: "
read -s CLAUDE_API_KEY
echo

if [ -z "$CLAUDE_API_KEY" ]; then
    echo "ERROR: Claude API key is required"
    exit 1
fi

# Setup backend
echo "Setting up backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create backend .env
cat > .env << EOF
ANTHROPIC_API_KEY=$CLAUDE_API_KEY
FLASK_ENV=development
FLASK_DEBUG=True
EOF

mkdir -p uploads extracted_frames
cd ..

# Setup frontend
echo "Setting up frontend..."
cd frontend
npm install

# Create frontend .env
cat > .env << EOF
VITE_API_URL=http://localhost:5000
EOF
cd ..

echo "Setup complete!"
echo
echo "To start SkillsFoundry:"
echo "  ./run.sh"
echo
echo "Demo accounts:"
echo "  Company: demo@test.com (password: 123)"
echo "  Applicants: custom@test.com, gpt@test.com, etc. (password: 123)"
