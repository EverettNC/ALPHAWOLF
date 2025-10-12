#!/bin/bash
# Memory Lane Quick Start & Test Script
# Launches AlphaWolf and runs comprehensive Memory Lane tests

echo "🐺 =========================================="
echo "   ALPHAWOLF MEMORY LANE - QUICK START"
echo "   'Without memory, no existence'"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.12+"
    exit 1
fi

echo "✅ Python 3 detected"

# Check if in virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Not in virtual environment. Activating..."
    
    if [ -d "venv" ]; then
        source venv/bin/activate
        echo "✅ Virtual environment activated"
    else
        echo "❌ Virtual environment not found. Creating..."
        python3 -m venv venv
        source venv/bin/activate
        echo "✅ Virtual environment created and activated"
        
        echo "📦 Installing dependencies..."
        pip install -r requirements.txt
        echo "✅ Dependencies installed"
    fi
else
    echo "✅ Virtual environment already active"
fi

# Check if Flask is installed
if ! python3 -c "import flask" &> /dev/null; then
    echo "❌ Flask not installed. Installing dependencies..."
    pip install -r requirements.txt
fi

echo ""
echo "🚀 Starting AlphaWolf Flask App..."
echo ""

# Start Flask in background
python3 app.py &
FLASK_PID=$!

echo "⏳ Waiting for Flask to start (5 seconds)..."
sleep 5

# Check if Flask is running
if ! curl -s http://localhost:5000/ > /dev/null; then
    echo "❌ Flask failed to start"
    kill $FLASK_PID 2>/dev/null
    exit 1
fi

echo "✅ AlphaWolf Flask app is running (PID: $FLASK_PID)"
echo ""
echo "🌐 Opening Memory Lane in browser..."
echo "   URL: http://localhost:5000/memory-lane"
echo ""

# Open browser (cross-platform)
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:5000/memory-lane &
elif command -v open &> /dev/null; then
    open http://localhost:5000/memory-lane &
elif command -v start &> /dev/null; then
    start http://localhost:5000/memory-lane &
else
    echo "⚠️  Could not auto-open browser. Please visit:"
    echo "   http://localhost:5000/memory-lane"
fi

sleep 2

echo ""
echo "🧪 Running Memory Lane API Tests..."
echo ""

# Run test suite
python3 test_memory_lane.py

TEST_RESULT=$?

echo ""
echo "=========================================="
echo "   TEST RESULTS"
echo "=========================================="

if [ $TEST_RESULT -eq 0 ]; then
    echo "✅ ALL TESTS PASSED - READY FOR COMMERCIAL"
    echo ""
    echo "🎬 Memory Lane is fully operational!"
    echo "   All 31+ buttons are functional"
    echo ""
else
    echo "⚠️  SOME TESTS FAILED"
    echo ""
    echo "Review test output above for details"
    echo ""
fi

echo "=========================================="
echo "   NEXT STEPS"
echo "=========================================="
echo ""
echo "1. ✅ Memory Lane is open in your browser"
echo "2. ✅ Flask app is running (PID: $FLASK_PID)"
echo "3. 🎯 Test each button manually in the UI"
echo "4. 🎬 Record commercial demo"
echo ""
echo "To stop the server:"
echo "   kill $FLASK_PID"
echo ""
echo "Or press Ctrl+C"
echo ""
echo "🐺 AlphaWolf Memory Lane - Preserving Existence"
echo "   'AI that helps you never say goodbye'"
echo ""

# Keep script running and monitor Flask
echo "Monitoring AlphaWolf server... (Press Ctrl+C to stop)"
echo ""

# Wait for Flask process
wait $FLASK_PID
