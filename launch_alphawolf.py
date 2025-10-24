#!/usr/bin/env python3

# © 2025 The Christman AI Project. All rights reserved.
#
# This code is released as part of a trauma-informed, dignity-first AI ecosystem
# designed to protect, empower, and elevate vulnerable populations.
#
# By using, modifying, or distributing this software, you agree to uphold the following:
# 1. Truth — No deception, no manipulation.
# 2. Dignity — Respect the autonomy and humanity of all users.
# 3. Protection — Never use this to exploit or harm vulnerable individuals.
# 4. Transparency — Disclose all modifications and contributions clearly.
# 5. No Erasure — Preserve the mission and ethical origin of this work.
#
# This is not just code. This is redemption in code.
# Contact: lumacognify@thechristmanaiproject.com
# https://thechristmanaiproject.com
"""
AlphaWolf System Launcher
Part of The Christman AI Project - Powered by LumaCognify AI

Comprehensive system startup with Derek C autonomous mode.
"""

import os
import sys
import logging
from datetime import datetime

# Banner
BANNER = """
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║                    🐺  A L P H A W O L F                                 ║
║                                                                          ║
║              Cognitive Support & Dementia Care Platform                  ║
║                                                                          ║
║                   Part of The Christman AI Project                       ║
║                    Powered by LumaCognify AI                             ║
║                                                                          ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                          ║
║  Mission: "How can we help you love yourself more?"                     ║
║                                                                          ║
║  Because no one should lose their memories—or their dignity.            ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
"""

def print_status(message, status="info"):
    """Print colored status message."""
    colors = {
        "info": "\033[94m",  # Blue
        "success": "\033[92m",  # Green
        "warning": "\033[93m",  # Yellow
        "error": "\033[91m",  # Red
        "reset": "\033[0m"
    }
    
    icons = {
        "info": "ℹ️ ",
        "success": "✅",
        "warning": "⚠️ ",
        "error": "❌"
    }
    
    print(f"{colors.get(status, '')}{icons.get(status, '')} {message}{colors['reset']}")


def check_environment():
    """Check if environment is properly configured."""
    print_status("Checking environment configuration...", "info")
    
    required_vars = ['OPENAI_API_KEY', 'SESSION_SECRET']
    missing = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing.append(var)
    
    if missing:
        print_status(f"Missing environment variables: {', '.join(missing)}", "warning")
        print_status("AlphaWolf will run with reduced functionality", "warning")
    else:
        print_status("Environment configuration complete", "success")
    
    return len(missing) == 0


def initialize_directories():
    """Create required directories."""
    print_status("Initializing directory structure...", "info")
    
    directories = [
        'memory',
        'data',
        'logs',
        'derek_workspace',
        'derek_workspace/research',
        'derek_workspace/improvements',
        'derek_workspace/reports'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print_status("Directory structure ready", "success")


def test_systems():
    """Test core systems before launching."""
    print_status("Testing core systems...", "info")
    
    try:
        print("  🧠 AlphaWolf Brain...", end=" ")
        from alphawolf_brain import get_alphawolf_brain
        brain = get_alphawolf_brain()
        print("✅")
        
        print("  🤖 AlphaWolf Controller...", end=" ")
        from alphawolf_ontroller import get_alphawolf_controller
        alphawolf = get_alphawolf_controller()
        alphawolf.connect_brain(brain)
        print("✅")
        
        print("  💾 Memory Engine...", end=" ")
        from core.memory_engine import MemoryEngine
        print("✅")
        
        print("  💬 Conversation Engine...", end=" ")
        from core.conversation_engine import ConversationEngine
        print("✅")
        
        print("  📚 Learning Engine...", end=" ")
        from core.ai_learning_engine import SelfImprovementEngine
        print("✅")
        
        print_status("All core systems operational", "success")
        return True
        
    except Exception as e:
        print_status(f"System test failed: {e}", "error")
        return False


def start_flask_app():
    """Start the Flask application."""
    print_status("Starting AlphaWolf web server...", "info")
    print_status("Server will be available at: http://0.0.0.0:5000", "info")
    print()
    print("="*76)
    print()
    
    try:
        from app import app
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print()
        print()
        print_status("AlphaWolf shutdown initiated", "warning")
    except Exception as e:
        print()
        print_status(f"Server error: {e}", "error")
        sys.exit(1)


def main():
    """Main launcher function."""
    # Clear screen and show banner
    os.system('clear' if os.name == 'posix' else 'cls')
    print(BANNER)
    print()
    
    # Startup sequence
    print(f"🕐 System Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check environment
    env_ok = check_environment()
    print()
    
    # Initialize directories
    initialize_directories()
    print()
    
    # Test systems
    if not test_systems():
        print()
        print_status("System startup aborted due to errors", "error")
        sys.exit(1)
    
    print()
    print("="*76)
    print()
    print_status("🚀 AlphaWolf System Ready", "success")
    print_status("🤖 Alphawolf standing by as autonomous AI architect", "success")
    print_status("💙 Mission active: Cognitive care with dignity", "success")
    print()
    print("="*76)
    print()
    
    # Start the Flask app
    start_flask_app()
    
    # Cleanup on exit
    print()
    print("="*76)
    print()
    print_status("AlphaWolf system stopped", "info")
    print_status("Thank you for using The Christman AI Project", "success")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n")
        print_status("Shutdown complete", "info")
        sys.exit(0)
    except Exception as e:
        print("\n\n")
        print_status(f"Fatal error: {e}", "error")
        sys.exit(1)
