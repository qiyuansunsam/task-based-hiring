#!/bin/bash

# SkillsFoundry Run Script

echo "Starting SkillsFoundry..."

# Function to cleanup background processes
cleanup() {
    echo
    echo "Shutting down servers..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start backend
echo "Starting backend server..."
cd backend
source venv/bin/activate
python app.py &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "Starting frontend server..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo
echo "SkillsFoundry is running!"
echo "   Frontend: http://localhost:5173"
echo "   Backend:  http://localhost:5000"
echo
echo "Demo accounts:"
echo "   Company: demo@test.com (password: 123)"
echo "   Applicants: custom@test.com, gpt@test.com, etc. (password: 123)"
echo
echo "Press Ctrl+C to stop both servers"

# Wait for both processes
wait
