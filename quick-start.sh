#!/bin/bash

# FPL Assistant Quick Start Script

echo "🚀 FPL Assistant - Quick Start"
echo "================================"
echo ""

# Check Python and Node
echo "📋 Checking dependencies..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 14+"
    exit 1
fi

echo "✅ Python: $(python3 --version)"
echo "✅ Node: $(node --version)"
echo ""

# Setup Backend
echo "📦 Setting up Backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "   Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "   Installing Python dependencies..."
pip install -q -r requirements.txt

if [ ! -f ".env" ]; then
    echo "   Creating .env file..."
    cp .env.example .env
fi

echo "✅ Backend ready!"
echo ""

# Setup Frontend
cd ../frontend

echo "📦 Setting up Frontend..."
if [ ! -d "node_modules" ]; then
    echo "   Installing npm dependencies..."
    npm install --silent --no-progress
fi

echo "✅ Frontend ready!"
echo ""

# Summary
cd ..
echo "🎉 Setup complete!"
echo ""
echo "📚 To get started:"
echo ""
echo "   Terminal 1 - Backend:"
echo "     cd backend"
echo "     source venv/bin/activate"
echo "     python run.py"
echo ""
echo "   Terminal 2 - Frontend:"
echo "     cd frontend"
echo "     npm start"
echo ""
echo "Then open: http://localhost:3000"
echo ""
echo "📖 For more info, see SETUP_AND_USAGE.md"
echo ""
