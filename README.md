# Digital Logic Design Platform

A comprehensive web-based platform for digital logic design, analysis, and simulation with integrated backend and frontend.

## 🚀 Quick Start

### Option 1: Windows Users
Double-click `start_backend.bat` to automatically start the server.

### Option 2: Python Script
```bash
python start_server.py
```

### Option 3: Manual Start
```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 🌐 Access Points

- **Frontend Application**: http://localhost:8000/improved.html
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🔧 Features

### ✅ Implemented Features

1. **Truth Table Generator**
   - Generate truth tables for Boolean expressions
   - Support for multiple input formats (A & B | C, A.B + C, A AND B OR C)
   - Export to workspace

2. **K-Map Generator & Simplifier**
   - Visual K-Map generation with automatic cache-busting
   - Boolean expression simplification
   - Support for up to 3 variables
   - Real-time image refresh (fixes previous caching issues)

3. **Circuit Designer**
   - Logic circuit analysis from Boolean expressions
   - Gate count estimation
   - Circuit structure visualization

4. **Boolean Expression Simplifier**
   - Multiple simplification methods (Algebraic SOP, POS, Manual)
   - Complexity reduction analysis
   - Best result selection

5. **Sequence Detector**
   - Mealy and Moore machine analysis
   - State diagram generation
   - Truth table generation for sequences
   - Flip-flop analysis integration
   - Cache-busted image serving

6. **Flip-Flop Analysis**
   - Support for D, JK, T, and SR flip-flops
   - Truth table conversion
   - Circuit optimization

7. **Interactive Whiteboard**
   - Drawing tools with logic gate templates
   - Save/load functionality
   - Export capabilities

8. **Personal Workspace**
   - Project management system
   - Save and organize work
   - Export/import projects

## 🏗️ Architecture

### Backend (FastAPI)
- **main.py**: Main server with all API endpoints
- **logic.py**: Boolean logic operations and K-map generation
- **sequence.py**: Sequence detector analysis (unchanged logic)
- **flipflop.py**: Flip-flop conversion utilities

### Frontend (HTML/JavaScript)
- **improved.html**: Single-page application with all features
- Responsive design with Material Design components
- Real-time API integration with proper error handling

### Key Integration Fixes Applied

1. **K-Map Image Refreshing**
   - Added timestamp-based cache-busting
   - Multiple image serving endpoints
   - Automatic image refresh on generation

2. **Backend-Frontend Connection**
   - Added missing `/simplify` endpoint
   - Fixed CORS configuration
   - Proper static file serving for all outputs

3. **Sequence Detector Integration**
   - Cache-busting for all generated images
   - Proper file serving for state diagrams and truth tables
   - Maintained sequence.py logic without changes

## 📁 File Structure

```
DIGITAL/
├── main.py                 # FastAPI backend server
├── logic.py               # Boolean logic operations
├── sequence.py            # Sequence detector (unchanged)
├── flipflop.py           # Flip-flop utilities
├── improved.html         # Frontend application
├── requirements.txt      # Python dependencies
├── start_server.py       # Python startup script
├── start_backend.bat     # Windows batch startup
├── test_backend.py       # Backend testing script
└── outputs/              # Generated files (images, diagrams)
    ├── kmap.png
    ├── state_diagram.png
    ├── truth_table.png
    └── ...
```

## 🔌 API Endpoints

### Core Endpoints
- `POST /truth-table` - Generate truth tables
- `POST /kmap` - Generate K-maps with cache-busting
- `POST /circuit` - Analyze logic circuits
- `POST /simplify` - Simplify Boolean expressions
- `POST /sequence-detector` - Analyze sequence detectors
- `POST /compare-sequences` - Compare sequence detectors
- `POST /flipflops` - Flip-flop analysis

### File Serving
- `GET /kmap.png` - Current K-map image
- `GET /kmap_{timestamp}.png` - Timestamped K-map images
- `GET /outputs/{filename}` - All generated output files
- `GET /health` - Server health check

## 🛠️ Technical Details

### Cache-Busting Implementation
- Timestamp-based unique filenames for images
- Query parameter cache-busting (`?t=timestamp`)
- Automatic image refresh in frontend
- Fallback mechanisms for missing files

### CORS Configuration
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Static File Serving
- Frontend served from root (`/`)
- Output files served from `/outputs/`
- Automatic directory creation

## 🧪 Testing

### Backend Testing
```bash
python test_backend.py
```

### Manual Testing
1. Start the server
2. Open http://localhost:8000/improved.html
3. Test each feature:
   - Generate truth tables
   - Create K-maps (verify images refresh)
   - Analyze sequences
   - Use the whiteboard
   - Save to workspace

## 🔍 Troubleshooting

### Common Issues

1. **K-Map images not refreshing**
   - ✅ Fixed with timestamp-based cache-busting
   - Images now refresh automatically

2. **Backend connection errors**
   - Ensure server is running on port 8000
   - Check firewall settings
   - Verify all dependencies are installed

3. **Missing images in sequence detector**
   - ✅ Fixed with proper file serving and cache-busting
   - All generated images now serve correctly

4. **CORS errors**
   - ✅ Fixed with proper CORS middleware configuration

### Debug Mode
Start server with debug logging:
```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
```

## 📦 Dependencies

### Python Backend
- fastapi==0.104.1
- uvicorn[standard]==0.24.0
- python-multipart==0.0.6
- sympy==1.12
- matplotlib==3.8.2
- graphviz==0.20.1
- requests==2.31.0
- numpy==1.24.3

### Frontend
- Tailwind CSS (CDN)
- Material Icons (CDN)
- Vanilla JavaScript (no additional dependencies)

## 🎯 Key Improvements Made

1. **✅ Fixed K-Map Refreshing**: Images now update properly with cache-busting
2. **✅ Added Missing Endpoints**: `/simplify` endpoint implemented
3. **✅ Enhanced File Serving**: Comprehensive output file serving
4. **✅ Improved Error Handling**: Better error messages and fallbacks
5. **✅ Sequence Integration**: Proper integration with sequence.py without logic changes
6. **✅ Startup Scripts**: Easy server startup for all users
7. **✅ Documentation**: Comprehensive setup and usage guide

## 🚀 Production Deployment

For production deployment:

1. Set `LOGICLAB_CORS_ORIGINS` to the exact frontend origins that should call the API.
2. Set `OPENROUTER_API_KEY` in the server environment if AI Verilog generation is enabled.
3. Use a production ASGI server such as Uvicorn/Gunicorn behind HTTPS.
4. Set up structured logging, monitoring, and error reporting.
5. Move generated files from local `outputs/` storage to durable object storage if users need persistent history.
6. Vendor or bundle frontend assets instead of relying on public CDNs when deploying offline or in restricted networks.

## 📝 License

This project is for educational and research purposes.
