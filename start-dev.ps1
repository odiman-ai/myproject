# start-dev.ps1
# PowerShell script to set up and run SPMS backend

# 1. Activate virtual environment
Write-Host "Activating virtual environment..."
.\venv\Scripts\Activate.ps1

# 2. Set environment variables (adjust as needed)
$env:SECRET_KEY = "change-this-in-production"
$env:ACCESS_TOKEN_EXPIRE_MINUTES = "30"
$env:SPMS_ENV = "development"
$env:DATABASE_URL = "sqlite:///./spms_dev.db"

# 3. Start Uvicorn from project root
Write-Host "Starting SPMS backend..."
python -m uvicorn backend.main:app --reload
