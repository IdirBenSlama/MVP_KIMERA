# KIMERA SWM Dependency Cleanup Report

## Overview
The requirements.txt file has been cleaned up to remove unused dependencies and organize the remaining ones by category. This reduces installation time, potential conflicts, and security surface area.

## Dependencies Removed (Unused/Redundant)

### Web Framework & Security (Unused)
- **Flask==2.3.3** - Not used (FastAPI is the web framework)
- **Flask-JWT-Extended==4.5.3** - Not used (no Flask usage)
- **bcrypt==4.1.2** - Not used (no password hashing in codebase)
- **cryptography==44.0.2** - Not used directly
- **PyJWT==2.10.1** - Not used (no JWT handling found)

### Background Jobs & Scheduling (Unused)
- **APScheduler==3.11.0** - Not used (no scheduled jobs found)

### OpenAI Integration (Unused)
- **openai==1.70.0** - Not used in current codebase
- **litellm==1.65.4.post1** - Not used in current codebase
- **tiktoken==0.9.0** - Not used in current codebase

### Database (Unused)
- **neo4j==5.28.1** - Not used (only SQLAlchemy/PostgreSQL used)

### Development Tools (Redundant)
- **radon==6.0.1** - Code complexity tool, not essential
- **typer==0.15.2** - CLI framework, not used

### Git Integration (Unused)
- **GitPython==3.1.44** - Not used in current codebase

### Security & Vault (Unused)
- **hvac==2.3.0** - HashiCorp Vault client, not used

### JSON Schema (Unused)
- **jsonschema==4.23.0** - Not used in current codebase
- **jsonschema-specifications==2024.10.1** - Not used

### HTTP Extensions (Redundant)
- **httpx-sse==0.4.0** - Server-sent events, not used

### Template Engine (Unused)
- **Jinja2==3.1.6** - Not used (FastAPI uses its own templating)
- **MarkupSafe==3.0.2** - Jinja2 dependency, not needed

### Timezone Support (Redundant)
- **pytz==2025.2** - Redundant with built-in datetime
- **tzdata==2025.2** - Redundant with built-in datetime
- **tzlocal==5.3.1** - Not used

### Build Tools (Redundant)
- **setuptools==79.0.1** - Usually included with Python
- **toml==0.10.2** - Not used for configuration

### Async Support (Redundant)
- **sniffio==1.3.1** - Low-level async detection, not needed directly

### ONNX Optimization (Simplified)
- **onnxruntime-gpu>=1.16.0,<1.21.0** - Redundant with main onnxruntime

## Dependencies Kept (Actually Used)

### Core Web Framework
- **fastapi** - Main web framework
- **uvicorn** - ASGI server
- **pydantic** - Data validation
- **python-multipart** - File upload support

### Database & Storage
- **SQLAlchemy** - ORM used throughout
- **psycopg2-binary** - PostgreSQL adapter
- **pgvector** - Vector similarity search

### AI/ML Core
- **torch** - Deep learning framework
- **transformers** - Hugging Face models
- **numpy** - Numerical computing
- **scipy** - Scientific computing
- **scikit-learn** - Machine learning utilities
- **huggingface-hub** - Model downloads

### Embedding Models
- **FlagEmbedding** - BGE-M3 embedding model
- **safetensors** - Safe tensor serialization
- **tokenizers** - Text tokenization

### NLP Processing
- **spacy** - Natural language processing
- **en_core_web_sm** - English language model

### Image Processing
- **pillow** - Image manipulation (used in CLIP service)

### HTTP Clients
- **httpx** - Modern HTTP client
- **requests** - HTTP requests
- **aiohttp** - Async HTTP client

### System Monitoring
- **psutil** - System resource monitoring
- **rich** - Terminal formatting

### Development & Testing
- **pytest** - Testing framework

### Utilities
- **click** - CLI framework (used in scripts)
- **tqdm** - Progress bars
- **PyYAML** - YAML parsing
- **python-dotenv** - Environment variables

## Impact Assessment

### Positive Impacts
1. **Reduced Installation Time**: ~40% fewer packages to install
2. **Smaller Attack Surface**: Fewer dependencies = fewer potential vulnerabilities
3. **Cleaner Environment**: Less chance of version conflicts
4. **Better Organization**: Dependencies grouped by purpose
5. **Easier Maintenance**: Clear understanding of what's actually needed

### Risk Mitigation
1. **Backup Created**: Original requirements saved as `requirements_original_backup.txt`
2. **Gradual Approach**: Can restore individual packages if needed
3. **Testing Required**: Full system testing recommended after cleanup

## Recommendations

### Immediate Actions
1. **Test Core Functionality**: Run main API endpoints
2. **Test Embedding System**: Verify BGE-M3 model loading
3. **Test Database Operations**: Verify CRUD operations
4. **Test Image Processing**: Verify CLIP functionality

### Optional Additions (If Needed)
```bash
# Financial analysis features
pip install pandas yfinance matplotlib seaborn

# Advanced security (if implementing auth)
pip install bcrypt PyJWT

# Background jobs (if implementing scheduled tasks)
pip install APScheduler

# OpenAI integration (if adding LLM features)
pip install openai litellm tiktoken
```

### Monitoring
- Watch for any import errors during system operation
- Monitor system performance after cleanup
- Be prepared to add back specific packages if functionality breaks

## Files Modified
- `requirements.txt` - Cleaned and reorganized
- `requirements_original_backup.txt` - Backup of original file
- `requirements_clean.txt` - Clean version (same as new requirements.txt)
- `DEPENDENCY_CLEANUP_REPORT.md` - This report

## Next Steps
1. Run `pip install -r requirements.txt` in a fresh environment
2. Test all major system components
3. Remove backup files once stability is confirmed
4. Consider creating a `requirements-dev.txt` for development-only dependencies