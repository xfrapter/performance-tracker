import subprocess
import sys
import os
from pathlib import Path

def create_venv():
    """Create virtual environment if it doesn't exist."""
    if not os.path.exists('venv'):
        print("Creating virtual environment...")
        subprocess.run([sys.executable, '-m', 'venv', 'venv'])
    else:
        print("Virtual environment already exists.")

def install_requirements():
    """Install required packages."""
    requirements = [
        'kivy==2.2.1',
        'kivymd==1.1.1',
        'pillow==10.2.0',
        'matplotlib==3.8.2',
        'pandas==2.2.0',
        'buildozer==1.5.0'
    ]
    
    # Determine the pip command based on the OS
    if sys.platform == 'win32':
        pip_cmd = os.path.join('venv', 'Scripts', 'pip')
    else:
        pip_cmd = os.path.join('venv', 'bin', 'pip')
    
    print("Installing requirements...")
    for req in requirements:
        print(f"Installing {req}...")
        subprocess.run([pip_cmd, 'install', req])

def create_directories():
    """Create necessary directories."""
    directories = [
        'docs',
        'data',
        'backups',
        'tests'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"Created directory: {directory}")

def main():
    print("Setting up Performance Tracker App...")
    
    # Create virtual environment
    create_venv()
    
    # Install requirements
    install_requirements()
    
    # Create directories
    create_directories()
    
    print("\nSetup completed successfully!")
    print("\nTo activate the virtual environment:")
    if sys.platform == 'win32':
        print("    .\\venv\\Scripts\\activate")
    else:
        print("    source venv/bin/activate")
    
    print("\nTo run the app:")
    print("    python main.py")

if __name__ == '__main__':
    main() 