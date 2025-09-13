"""Setup script for the Script Analyzer."""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages."""
    try:
        print("📦 Installing required packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        return False

def check_pdf_file():
    """Check if script.pdf exists."""
    if os.path.exists("script.pdf"):
        file_size = os.path.getsize("script.pdf")
        print(f"✅ Found script.pdf ({file_size:,} bytes)")
        return True
    else:
        print("⚠️  script.pdf not found in current directory")
        print("   Please place your PDF script file as 'script.pdf' in this directory")
        return False

def run_app():
    """Run the Streamlit app."""
    try:
        print("\n🚀 Starting the Script Analyzer application...")
        print("   The app will open in your default web browser")
        print("   Press Ctrl+C to stop the application\n")
        subprocess.run([sys.executable, "-m", "streamlit", "run", "script_analyzer.py"])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error running app: {e}")

def main():
    """Main setup function."""
    print("=" * 50)
    print("📋 Script Analyzer Setup")
    print("=" * 50)
    
    # Check for PDF file
    pdf_exists = check_pdf_file()
    
    # Install requirements
    if install_requirements():
        print("\n🎯 Setup completed successfully!")
        
        if pdf_exists:
            print("\n🚀 Ready to run! Starting the application...")
            run_app()
        else:
            print("\n📝 Please add your script.pdf file and run:")
            print("   streamlit run script_analyzer.py")
    else:
        print("\n❌ Setup failed. Please install requirements manually:")
        print("   pip install -r requirements.txt")

if __name__ == "__main__":
    main()
