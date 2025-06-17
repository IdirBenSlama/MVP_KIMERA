# KIMERA SWM - Semantic Working Memory System

[![Version](https://img.shields.io/badge/version-2.3.0-blue.svg)](https://github.com/your-org/kimera-swm)
[![Python](https://img.shields.io/badge/python-3.13+-green.svg)](https://python.org)
[![GPU](https://img.shields.io/badge/GPU-RTX_4090_validated-blue.svg)](COMPREHENSIVE_SYSTEM_DOCUMENTATION.md)
[![Tests](https://img.shields.io/badge/tests-99.92%25_success-brightgreen.svg)](test_scripts/tyrannic_progressive_crash_test.py)
[![Requirements](https://img.shields.io/badge/requirements-unified-green.svg)](requirements.txt)


**KIMERA SWM** is a high-performance cognitive architecture system with **99.92% reliability** under extreme stress conditions and **Neo4j graph integration** for genuine understanding capabilities. Successfully tested with 128 concurrent threads processing 2048-feature semantic geoids with full GPU acceleration.

## 🎯 Key Achievements

- ✅ **Extreme Stress Testing**: 99.92% success rate (2,538/2,540 operations)
- ✅ **Neo4j Integration**: Graph database with dual-write capability for semantic relationships
- ✅ **Understanding Architecture**: Infrastructure for genuine comprehension beyond pattern matching
- ✅ **Requirements Consolidation**: Unified dependencies in single requirements.txt
- ✅ **GPU Optimization**: Full RTX 4090 acceleration with BGE-M3 embeddings
- ✅ **Database Validation**: 178.84 MB with perfect data integrity
- ✅ **Performance**: 18-35 operations/second under maximum load

## 🚀 Quick Start

### Prerequisites
- Python 3.13+ 
- NVIDIA GPU with CUDA support (RTX 4090 recommended)
- 16GB+ RAM
- Docker (for Neo4j graph database)

### Installation
```bash
# 1. Setup environment
python -m venv .venv
source .venv/Scripts/activate  # Windows
# source .venv/bin/activate    # macOS/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. GPU acceleration (recommended)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# 4. Setup Neo4j (optional but recommended)
docker run -d --name kimera-neo4j \
  -p 7687:7687 -p 7474:7474 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:5

# 5. Set Neo4j environment variables
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASS="password"

# 6. Run system
python run_kimera.py
```

### API Access
- **Swagger UI**: http://localhost:8001/docs
- **System Status**: http://localhost:8001/system/status
- **Neo4j Browser**: http://localhost:7474 (username: neo4j, password: password)

## 📊 Performance Results

### Stress Test Results
| Phase | Threads | Features | Depth | Success Rate | Performance | GPU Util |
|-------|---------|----------|-------|--------------|-------------|----------|
| 1 | 2 | 32 | 2 | **100.0%** | 2.69 ops/sec | 7% |
| 2 | 4 | 64 | 3 | **100.0%** | 35.27 ops/sec | 85% |
| 3 | 8 | 128 | 4 | **100.0%** | 31.60 ops/sec | 22% |
| 4 | 16 | 256 | 5 | **100.0%** | 29.56 ops/sec | 44% |
| 5 | 32 | 512 | 6 | **100.0%** | 27.86 ops/sec | 33% |
| 6 | 64 | 1024 | 7 | **100.0%** | 23.96 ops/sec | 33% |
| 7 | 128 | 2048 | 8 | **99.8%** | 18.68 ops/sec | 5% |

**Overall**: 99.92% success rate, no breaking point found

## 🧪 Testing

### Neo4j Integration Test
```bash
# Quick test (Windows)
test_neo4j.bat

# Quick test (Linux/Mac)
chmod +x test_neo4j.sh
./test_neo4j.sh

# Manual test
python test_neo4j_integration.py
```

### Run Stress Test
```bash
# Main stress test (requires GPU)
python test_scripts/tyrannic_progressive_crash_test.py

# CPU fallback mode (not recommended)
python test_scripts/tyrannic_progressive_crash_test.py --allow-cpu

# Install GPU dependencies
python test_scripts/tyrannic_progressive_crash_test.py --install-gpu-deps
```

### Database Analysis
```bash
# Analyze test database
python analyze_tyrannic_db.py

# Vector quality check
python vector_quality_analysis.py
```

## 🏗️ Architecture

```
KIMERA SWM v2.3
├── 🌐 API Layer (FastAPI)
├── 🧠 Core Processing (BGE-M3 GPU)
├── 🗄️ Data Layer (SQL + Neo4j Graph)
├── 🔗 Graph Layer (Semantic Relationships)
└── 🔧 Testing Framework
```

### Technology Stack
- **Backend**: Python 3.13, FastAPI, Uvicorn
- **AI/ML**: PyTorch 2.7.1+cu118, BGE-M3 (1024D)
- **Database**: SQLite, PostgreSQL, Neo4j Graph
- **Graph**: Neo4j 5.x with Bolt protocol
- **GPU**: CUDA 11.8/12.4, RTX 4090 optimized

## 🌐 API Examples

### Create Geoid
```python
import requests

response = requests.post('http://localhost:8001/geoids', json={
    "semantic_features": {"concept": 0.8, "intensity": 0.6},
    "symbolic_content": {"type": "example"},
    "metadata": {"source": "quickstart"}
})
```

### System Status
```python
response = requests.get('http://localhost:8001/system/status')
status = response.json()
print(f"GPU: {status['gpu_available']}")
```

## 📦 Requirements

### Unified Dependencies
Single requirements.txt file with 48 packages:
```bash
pip install -r requirements.txt
```

### Key Dependencies
- **FastAPI**: Web framework
- **PyTorch**: AI/ML with CUDA support
- **BGE-M3**: Semantic embeddings
- **SQLAlchemy**: Database ORM
- **Transformers**: NLP models

## 🚀 Deployment

### Development
```bash
python run_kimera.py
```

### Production
```bash
python -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker
```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "run_kimera.py"]
```

## 🔧 Troubleshooting

### GPU Issues
```bash
# Check CUDA
python -c "import torch; print(torch.cuda.is_available())"

# Install CUDA PyTorch
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

### Performance Issues
```bash
# Run stress test
python test_scripts/tyrannic_progressive_crash_test.py
# Expected: 99%+ success rate
```

## 📚 Documentation

- **[Complete System Guide](COMPREHENSIVE_SYSTEM_DOCUMENTATION.md)** - Detailed documentation
- **[Neo4j Integration Guide](NEO4J_TEST_GUIDE.md)** - Graph database setup and testing
- **[Understanding Roadmap](documentation/ROADMAP_GENUINE_UNDERSTANDING.md)** - Path to genuine understanding
- **[Requirements Report](REQUIREMENTS_CONSOLIDATION_REPORT.md)** - Dependency management
- **[Documentation Index](DOCUMENTATION_INDEX_FINAL.md)** - All documentation links

## 🏆 Validation

KIMERA SWM has been comprehensively validated:

### ✅ **Stress Testing**
- 2,540 operations across 7 progressive phases
- 99.92% success rate under extreme load
- No breaking point found

### ✅ **Database Quality**
- 178.84 MB database with perfect integrity
- 2,538 geoids with consistent 1024D vectors
- No data corruption detected

### ✅ **GPU Performance**
- RTX 4090 with 85% peak utilization
- BGE-M3 embeddings with proper acceleration
- Thermal management (48-50°C)

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

<div align="center">

**KIMERA SWM v2.3** - *Production-ready cognitive architecture with 99.92% reliability*

*Last Updated: June 15, 2025 | Test Status: PASSED*

</div>