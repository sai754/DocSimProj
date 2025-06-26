# #!/usr/bin/env python3
# """
# Script to run the Streamlit Recruitment Matching System
# """

# import subprocess
# import sys
# import os

# def main():
#     try:
#         # Change to the script directory
#         script_dir = os.path.dirname(os.path.abspath(__file__))
#         os.chdir(script_dir)
        
#         # Run streamlit
#         print("🚀 Starting Recruitment Matching System...")
#         print("📱 The app will open in your browser automatically")
#         print("🔗 If it doesn't open, go to: http://localhost:8501")
#         print("⏹️  Press Ctrl+C to stop the server")
#         print("-" * 50)
        
#         subprocess.run([
#             sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
#             "--server.headless", "true",
#             "--server.port", "8000",
#             "--browser.gatherUsageStats", "false"
#         ])
        
#     except KeyboardInterrupt:
#         print("\n👋 Shutting down the server...")
#     except Exception as e:
#         print(f"❌ Error starting the application: {e}")
#         print("💡 Make sure you have installed the requirements:")
#         print("   pip install -r requirements.txt")

# if __name__ == "__main__":
#     main()