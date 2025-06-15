# Kimera SWM System Update Fixes

## Issues Resolved

### 1. Dependency Resolution Error
**Problem**: `error: resolution-too-deep` - Dependency resolution exceeded maximum depth
**Solution**: 
- Created `requirements-minimal.txt` with looser version constraints
- Implemented multi-strategy dependency installation:
  1. Try main requirements.txt
  2. Fallback to minimal requirements
  3. Install core packages individually if needed
- Added version ranges instead of exact pins for AI/ML dependencies

### 2. Missing `get_system_metrics` Function
**Problem**: `cannot import name 'get_system_metrics' from 'backend.monitoring.telemetry'`
**Solution**: 
- Added `get_system_metrics()` function to `backend/monitoring/telemetry.py`
- Function returns system metrics dictionary with active geoids, cycle count, vault pressure, and timestamp
- Includes proper error handling and fallback values

### 3. Database SQL Query Error
**Problem**: `Textual SQL expression 'SELECT 1' should be explicitly declared as text('SELECT 1')`
**Solution**: 
- Updated database connection test in `update_system.py`
- Added proper SQLAlchemy `text()` wrapper around raw SQL queries
- Imported `text` from `sqlalchemy` module

### 4. Unicode Encoding Issues
**Problem**: `'charmap' codec can't encode character '\\u2705' in position 2: character maps to <undefined>`
**Solution**: 
- Replaced all emoji characters with ASCII alternatives:
  - 🔄 → [PROCESSING]
  - ✅ → [SUCCESS] 
  - ❌ → [FAILED]
  - ⚠️ → [WARNING]
  - 🚀 → [STARTING]
  - 🎉 → [COMPLETE]
  - 📊 → [REPORT]
  - ⏱️ → [DURATION]
- Implemented `SafeStreamHandler` class for better Unicode handling in logging
- Added proper encoding fallbacks for Windows console

## Current System Status

After applying these fixes, the system update now shows:

✅ **Working Components**:
- Embedding Model Update: Successfully loads BGE-M3 model
- Database Optimization: Completes successfully
- Vault System Optimization: Rebalances vaults properly
- Monitoring System Update: Collects 4 metrics successfully
- System Tests: Database and embedding tests pass
- System Cleanup: Removes temporary files

⚠️ **Partial Issues**:
- Dependency Installation: May fail due to system build tools, but fallback strategies ensure core functionality
- API Health Check: Skipped when API server not running (expected behavior)

## Recommendations

1. **For Production**: Consider using Docker containers to avoid dependency resolution issues
2. **For Development**: Install Microsoft Visual C++ Build Tools if dependency compilation fails
3. **For Monitoring**: Start the API server before running system tests for complete health checks

## Files Modified

1. `update_system.py` - Main update script with emoji fixes and improved dependency handling
2. `backend/monitoring/telemetry.py` - Added missing `get_system_metrics` function
3. `requirements.txt` - Updated with version ranges for better compatibility
4. `requirements-minimal.txt` - Created minimal dependency set for fallback

## Test Results

The system update now completes successfully with 6/7 steps passing:
- Update Dependencies: ⚠️ (Partial - core packages installed)
- Update Embedding Model: ✅
- Optimize Database: ✅
- Optimize Vault System: ✅
- Update Monitoring System: ✅
- Run System Tests: ✅
- Cleanup System: ✅

Total duration: ~2-3 minutes depending on system performance.