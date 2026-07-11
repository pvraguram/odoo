# LogicLab Backend-Frontend Integration Guide

## Overview
This document describes the complete integration between the FastAPI backend and the HTML frontend for the LogicLab digital logic design platform.

## Architecture

### Backend (FastAPI)
- **File**: `main.py`
- **Port**: 8000
- **URL**: `http://localhost:8000`
- **Features**:
  - Truth table generation
  - K-map visualization and simplification
  - Circuit diagram generation
  - Boolean expression simplification
  - Sequence detector analysis
  - Flip-flop conversion and analysis

### Frontend (HTML/JavaScript)
- **File**: `improved.html`
- **Access URL**: `http://localhost:8000/improved.html`
- **API Base URL**: `http://localhost:8000`
- **Features**:
  - Interactive web interface
  - Real-time API communication
  - Result visualization
  - Workspace management
  - Drawing whiteboard

## Quick Start

### 1. Start the Application
```bash
# Run the startup script
start_backend.bat
```

This will:
- Start the FastAPI server on port 8000
- Automatically open the browser to the frontend
- Display connection status

### 2. Test the Connection
- Click the "Test Backend Connection" button in the UI
- Or run the connection test script:
```bash
python test_connection.py
```

## API Endpoints

### Core Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check and available endpoints |
| `/truth-table` | POST | Generate truth table from boolean expression |
| `/kmap` | POST | Generate K-map and simplified expression |
| `/circuit` | POST | Generate circuit diagram text |
| `/simplify` | POST | Simplify boolean expressions |
| `/sequence-detector` | POST | Analyze sequence detectors |
| `/flipflops` | POST | Flip-flop analysis |

### Static File Serving
- Frontend files served from root (`/`)
- Output images served from `/outputs/`
- K-map images with cache-busting: `/kmap.png?t=timestamp`

## Integration Features

### 1. CORS Configuration
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Set `LOGICLAB_CORS_ORIGINS` for deployment, for example:
```bash
LOGICLAB_CORS_ORIGINS=https://your-domain.example
```

### 2. Static File Mounting
```python
app.mount("/", StaticFiles(directory=".", html=True), name="frontend")
```

### 3. Cache-Busting for Images
- K-map images include timestamps to prevent caching issues
- Automatic image refresh when generating new K-maps

### 4. Error Handling
- Comprehensive error messages
- Network error detection
- User-friendly error display

## Frontend API Integration

### API Configuration
```javascript
const API_BASE_URL = window.location.origin;
```

### API Call Function
```javascript
async function callAPI(endpoint, formData) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        body: formData
    });
    return await response.json();
}
```

### Connection Status
- Real-time backend status indicator
- Automatic connection testing
- Visual feedback for connection state

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure backend is running on port 8000
   - Check if another service is using port 8000
   - Verify API_BASE_URL in frontend matches backend URL

2. **CORS Errors**
   - Backend includes CORS middleware
   - Should not occur with current configuration

3. **Image Loading Issues**
   - K-map images use cache-busting timestamps
   - Check `/outputs/` directory permissions

4. **Sequence Detector Issues**
   - Ensure `sequence.py` is in the same directory
   - Check that all dependencies are installed

### Testing Tools

1. **Connection Test Script**
   ```bash
   python test_connection.py
   ```

2. **Manual API Testing**
   ```bash
   curl -X GET http://localhost:8000/health
   curl -X POST http://localhost:8000/truth-table -d "expr=A & B"
   ```

3. **Browser Developer Tools**
   - Check Network tab for API calls
   - Monitor Console for JavaScript errors

## File Structure
```
DIGITAL/
├── main.py                 # FastAPI backend
├── improved.html          # Frontend interface
├── start_backend.bat      # Startup script
├── test_connection.py     # Connection test script
├── logic.py              # Logic operations
├── sequence.py           # Sequence detector logic
├── flipflop.py           # Flip-flop analysis
├── outputs/              # Generated images
└── README_INTEGRATION.md # This file
```

## Dependencies

### Backend Requirements
```
fastapi
uvicorn
sympy
matplotlib
numpy
pillow
```

### Frontend Requirements
- Modern web browser with JavaScript enabled
- No additional dependencies (uses CDN resources)

## Development Notes

### Adding New Endpoints
1. Add endpoint function in `main.py`
2. Add corresponding frontend JavaScript function
3. Update API documentation
4. Test with `test_connection.py`

### Modifying Frontend
1. Update `improved.html`
2. Ensure API_BASE_URL is correct
3. Test all functionality
4. Verify mobile responsiveness

### Deployment Considerations
- Update API_BASE_URL for production
- Configure proper CORS origins
- Set up reverse proxy if needed
- Enable HTTPS in production

## Support
For issues or questions:
1. Check this integration guide
2. Run connection test script
3. Check browser developer console
4. Verify all files are present and accessible

---
*Last updated: 2025-01-05*
