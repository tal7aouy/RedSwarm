#!/bin/bash

echo "🔴 RedSwarm Setup Script"
echo "========================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your API keys!"
    echo ""
fi

# Backend setup
echo "Setting up backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Creating necessary directories..."
mkdir -p logs data

cd ..

# Frontend setup
echo ""
echo "Setting up frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "Installing Node dependencies..."
    npm install
fi

cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your ANTHROPIC_API_KEY (or OPENAI_API_KEY)"
echo "2. Start the backend:"
echo "   cd backend && source venv/bin/activate && uvicorn main:app --reload --port 8000"
echo "3. Start the frontend (new terminal):"
echo "   cd frontend && npm run dev -- --port 3000"
echo "4. Visit http://localhost:3000"
echo ""
echo "Happy hacking! 🔴"
