# SPMS Backend - Smart Participants Management System

A comprehensive humanitarian social protection management API built with FastAPI.

## Features
- 🔐 JWT Authentication & Authorization
- 👥 Household & Participant Management
- 📊 Programme & Project Management
- 📅 Activity & Attendance Tracking
- 📋 Survey & M&E Tools
- 🔍 Case Management
- 📈 Comprehensive Reporting

## Deployment

### Render (Production)
This application is configured for deployment on Render.com using the included `render.yaml`.

1. Push code to GitHub
2. Connect repository to Render
3. Render will auto-detect and deploy using `render.yaml`

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run server
python -m uvicorn backend.main:app --reload --port 8000
```

### Environment Variables
See `.env.example` for required environment variables.

## API Documentation
- Health Check: `/health`
- API Root: `/`
- Authentication: `/api/v1/auth/`

## Support
**Engineer Simon Akalees Odiman**
- Email: oakalees@yahoo.com
- Phone: +256 773 965 088 / +256 755 002 896
- Location: Kampala, Uganda

## License
Proprietary - All rights reserved