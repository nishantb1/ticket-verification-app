#!/usr/bin/env python3
"""
Local development runner with R2 environment variables
This script loads environment variables from .env file and runs the Flask app
"""

import os
import sys
from dotenv import load_dotenv

def main():
    """Load environment variables and run the Flask app"""
    
    # Load environment variables from .env file
    env_file = '.env'
    if os.path.exists(env_file):
        print(f"📁 Loading environment variables from {env_file}")
        load_dotenv(env_file)
        print("✅ Environment variables loaded")
    else:
        print(f"⚠️  No {env_file} file found. R2 will not be available.")
        print(f"   Create {env_file} from .env.example to enable R2 storage")
    
    # Check R2 configuration
    r2_vars = ['R2_ACCOUNT_ID', 'R2_BUCKET_NAME', 'R2_ACCESS_KEY_ID', 'R2_SECRET_ACCESS_KEY', 'R2_ENDPOINT']
    r2_configured = all(os.environ.get(var) for var in r2_vars)
    
    if r2_configured:
        print("🌩️  Cloudflare R2 configuration detected")
        print(f"   Account ID: {os.environ.get('R2_ACCOUNT_ID')}")
        print(f"   Bucket: {os.environ.get('R2_BUCKET_NAME')}")
        print(f"   Endpoint: {os.environ.get('R2_ENDPOINT')}")
    else:
        print("📁 R2 not configured - will use local storage")
        missing = [var for var in r2_vars if not os.environ.get(var)]
        if missing:
            print(f"   Missing variables: {', '.join(missing)}")
    
    print("\n🚀 Starting Flask development server...")
    print("   URL: http://localhost:5000")
    print("   Admin: http://localhost:5000/admin/login")
    print("   Press Ctrl+C to stop\n")
    
    # Set development environment
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = '1'
    
    # Import and run the Flask app
    try:
        from app import app
        app.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()