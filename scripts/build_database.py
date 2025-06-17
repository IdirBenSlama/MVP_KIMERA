#!/usr/bin/env python3
"""
KIMERA SWM Database Builder

This script builds and initializes the complete KIMERA SWM database system,
including both the relational database (SQLite/PostgreSQL) and the graph
database (Neo4j).

The system uses a hybrid architecture:
- SQLite/PostgreSQL: Primary storage for structured data
- Neo4j: Graph storage for semantic relationships and causal chains

Usage:
    python build_database.py [--neo4j] [--enhanced] [--reset]

Options:
    --neo4j     Initialize Neo4j graph database
    --enhanced  Create enhanced understanding tables
    --reset     Drop and recreate all tables
    --help      Show this help message
"""

import os
import sys
import argparse
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if all required dependencies are available."""
    print("🔍 Checking dependencies...")
    
    missing_deps = []
    
    # Check SQLAlchemy
    try:
        import sqlalchemy
        print(f"   ✅ SQLAlchemy {sqlalchemy.__version__}")
    except ImportError:
        missing_deps.append("sqlalchemy")
    
    # Check Neo4j driver
    try:
        import neo4j
        print(f"   ✅ Neo4j driver {neo4j.__version__}")
    except ImportError:
        missing_deps.append("neo4j")
    
    # Check backend modules
    try:
        from backend.vault.database import Base, engine, SessionLocal
        print("   ✅ Backend database modules")
    except ImportError as e:
        print(f"   ❌ Backend modules: {e}")
        missing_deps.append("backend-modules")
    
    if missing_deps:
        print(f"\n❌ Missing dependencies: {', '.join(missing_deps)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    print("   ✅ All dependencies available")
    return True

def check_neo4j_connection() -> bool:
    """Check if Neo4j is available and accessible."""
    print("\n🔌 Checking Neo4j connection...")
    
    try:
        from backend.graph.session import driver_liveness_check, get_driver
        
        # Check environment variables
        neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        neo4j_user = os.getenv("NEO4J_USER", "neo4j")
        neo4j_pass = os.getenv("NEO4J_PASS")
        
        if not neo4j_pass:
            print("   ⚠️  NEO4J_PASS environment variable not set")
            print("   Set with: export NEO4J_PASS='your_password'")
            return False
        
        print(f"   Neo4j URI: {neo4j_uri}")
        print(f"   Neo4j User: {neo4j_user}")
        print("   Neo4j Password: [CONFIGURED]")
        
        # Test connection
        if driver_liveness_check():
            print("   ✅ Neo4j connection successful")
            return True
        else:
            print("   ❌ Neo4j not responding")
            print("   Start with: docker run -p 7687:7687 -p 7474:7474 -e NEO4J_AUTH=neo4j/password neo4j:5")
            return False
            
    except Exception as e:
        print(f"   ❌ Neo4j connection error: {e}")
        return False

def initialize_relational_database(reset: bool = False, enhanced: bool = False):
    """Initialize the relational database (SQLite/PostgreSQL)."""
    print("\n🗄️  Initializing relational database...")
    
    try:
        from backend.vault.database import Base, engine, SessionLocal
        
        if enhanced:
            # Import enhanced schema to register tables
            from backend.vault.enhanced_database_schema import Base as EnhancedBase
            print("   📊 Enhanced understanding schema loaded")
        
        # Drop tables if reset requested
        if reset:
            print("   🗑️  Dropping existing tables...")
            Base.metadata.drop_all(bind=engine)
            if enhanced:
                EnhancedBase.metadata.drop_all(bind=engine)
        
        # Create all tables
        print("   🏗️  Creating database tables...")
        Base.metadata.create_all(bind=engine)
        
        if enhanced:
            EnhancedBase.metadata.create_all(bind=engine)
            print("   ✅ Enhanced understanding tables created")
        
        # Verify tables were created
        with SessionLocal() as db:
            # Check core tables
            core_tables = ['scars', 'geoids', 'insights']
            for table in core_tables:
                try:
                    result = db.execute(f"SELECT COUNT(*) FROM {table}")
                    count = result.scalar()
                    print(f"   ✅ Table '{table}': {count} records")
                except Exception as e:
                    print(f"   ❌ Table '{table}': {e}")
        
        print("   ✅ Relational database initialized successfully")
        return True
        
    except Exception as e:
        print(f"   ❌ Error initializing relational database: {e}")
        return False

def create_database_indexes():
    """Create optimized database indexes for performance."""
    print("\n📊 Creating database indexes...")
    
    try:
        from backend.vault.database import engine
        
        indexes = [
            # Core SCAR indexes
            "CREATE INDEX IF NOT EXISTS idx_scars_vault_id ON scars(vault_id);",
            "CREATE INDEX IF NOT EXISTS idx_scars_timestamp ON scars(timestamp DESC);",
            "CREATE INDEX IF NOT EXISTS idx_scars_weight ON scars(weight);",
            "CREATE INDEX IF NOT EXISTS idx_scars_geoids ON scars(geoids);",
            "CREATE INDEX IF NOT EXISTS idx_scars_reason ON scars(reason);",
            "CREATE INDEX IF NOT EXISTS idx_scars_vault_timestamp ON scars(vault_id, timestamp DESC);",
            
            # Core Geoid indexes
            "CREATE INDEX IF NOT EXISTS idx_geoids_id ON geoids(geoid_id);",
            "CREATE INDEX IF NOT EXISTS idx_geoids_created ON geoids(rowid);",
            
            # Insight indexes
            "CREATE INDEX IF NOT EXISTS idx_insights_type ON insights(insight_type);",
            "CREATE INDEX IF NOT EXISTS idx_insights_source ON insights(source_resonance_id);",
            "CREATE INDEX IF NOT EXISTS idx_insights_status ON insights(status);",
            "CREATE INDEX IF NOT EXISTS idx_insights_created ON insights(created_at DESC);",
            
            # Composite indexes for common queries
            "CREATE INDEX IF NOT EXISTS idx_scars_vault_weight ON scars(vault_id, weight);",
            "CREATE INDEX IF NOT EXISTS idx_scars_vault_reason ON scars(vault_id, reason);",
        ]
        
        with engine.connect() as conn:
            for index_sql in indexes:
                try:
                    conn.execute(index_sql)
                    index_name = index_sql.split('idx_')[1].split(' ')[0] if 'idx_' in index_sql else 'unknown'
                    print(f"   ✅ Index: {index_name}")
                except Exception as e:
                    print(f"   ⚠️  Index creation warning: {e}")
            
            conn.commit()
        
        print("   ✅ Database indexes created successfully")
        return True
        
    except Exception as e:
        print(f"   ❌ Error creating indexes: {e}")
        return False

def initialize_neo4j_database(reset: bool = False):
    """Initialize the Neo4j graph database."""
    print("\n🕸️  Initializing Neo4j graph database...")
    
    try:
        from backend.graph.session import get_session
        
        with get_session() as session:
            # Clear existing data if reset requested
            if reset:
                print("   🗑️  Clearing existing graph data...")
                session.run("MATCH (n) DETACH DELETE n")
            
            # Create constraints for data integrity
            constraints = [
                "CREATE CONSTRAINT geoid_id_unique IF NOT EXISTS FOR (g:Geoid) REQUIRE g.geoid_id IS UNIQUE",
                "CREATE CONSTRAINT scar_id_unique IF NOT EXISTS FOR (s:Scar) REQUIRE s.scar_id IS UNIQUE",
            ]
            
            print("   🔒 Creating constraints...")
            for constraint in constraints:
                try:
                    session.run(constraint)
                    constraint_name = constraint.split('_unique')[0].split(' ')[-1]
                    print(f"   ✅ Constraint: {constraint_name}_unique")
                except Exception as e:
                    if "already exists" not in str(e).lower():
                        print(f"   ⚠️  Constraint warning: {e}")
            
            # Create indexes for performance
            indexes = [
                "CREATE INDEX geoid_timestamp IF NOT EXISTS FOR (g:Geoid) ON (g.created_at)",
                "CREATE INDEX scar_timestamp IF NOT EXISTS FOR (s:Scar) ON (s.timestamp)",
                "CREATE INDEX scar_vault IF NOT EXISTS FOR (s:Scar) ON (s.vault_id)",
                "CREATE INDEX scar_reason IF NOT EXISTS FOR (s:Scar) ON (s.reason)",
            ]
            
            print("   📊 Creating graph indexes...")
            for index in indexes:
                try:
                    session.run(index)
                    index_name = index.split(' ')[2]
                    print(f"   ✅ Index: {index_name}")
                except Exception as e:
                    if "already exists" not in str(e).lower():
                        print(f"   ⚠️  Index warning: {e}")
            
            # Verify Neo4j setup
            result = session.run("RETURN 'Neo4j initialized' AS message")
            message = result.single()["message"]
            print(f"   ✅ {message}")
        
        print("   ✅ Neo4j graph database initialized successfully")
        return True
        
    except Exception as e:
        print(f"   ❌ Error initializing Neo4j database: {e}")
        return False

def create_sample_data():
    """Create sample data to verify the database setup."""
    print("\n🧪 Creating sample data...")
    
    try:
        from backend.vault.vault_manager import VaultManager
        from backend.core.geoid import GeoidState
        import uuid
        
        vault_manager = VaultManager()
        
        # Create sample geoids
        sample_geoids = []
        for i in range(3):
            geoid = GeoidState(
                geoid_id=f"SAMPLE_GEOID_{uuid.uuid4().hex[:8]}",
                semantic_state={
                    "concept": f"sample_concept_{i}",
                    "semantic_weight": 0.5 + (i * 0.1),
                    "created_by": "database_builder"
                },
                symbolic_state={
                    "type": "sample",
                    "index": i,
                    "category": "test_data"
                },
                embedding_vector=[float(j + i) for j in range(384)],  # Sample 384-dim vector
                metadata={
                    "created_at": datetime.now().isoformat(),
                    "source": "database_builder",
                    "purpose": "verification"
                }
            )
            sample_geoids.append(geoid)
        
        # Insert sample data
        for i, geoid in enumerate(sample_geoids):
            try:
                # This will trigger dual-write to both SQL and Neo4j
                scar_db = vault_manager.insert_scar(geoid, geoid.embedding_vector)
                print(f"   ✅ Sample {i+1}: SCAR {scar_db.scar_id[:12]}...")
            except Exception as e:
                print(f"   ⚠️  Sample {i+1} warning: {e}")
        
        # Verify data was created
        total_scars_a = vault_manager.get_total_scar_count("vault_a")
        total_scars_b = vault_manager.get_total_scar_count("vault_b")
        
        print(f"   📊 Vault A: {total_scars_a} SCARs")
        print(f"   📊 Vault B: {total_scars_b} SCARs")
        print(f"   📊 Total: {total_scars_a + total_scars_b} SCARs created")
        
        print("   ✅ Sample data created successfully")
        return True
        
    except Exception as e:
        print(f"   ❌ Error creating sample data: {e}")
        return False

def verify_database_setup():
    """Verify that both databases are working correctly."""
    print("\n✅ Verifying database setup...")
    
    success = True
    
    # Test relational database
    try:
        from backend.vault.database import SessionLocal, ScarDB, GeoidDB
        
        with SessionLocal() as db:
            scar_count = db.query(ScarDB).count()
            geoid_count = db.query(GeoidDB).count()
            
            print(f"   📊 SQL Database: {scar_count} SCARs, {geoid_count} Geoids")
            
    except Exception as e:
        print(f"   ❌ SQL Database error: {e}")
        success = False
    
    # Test Neo4j database
    try:
        from backend.graph.session import get_session
        
        with get_session() as session:
            # Count nodes
            result = session.run("""
                MATCH (n) 
                RETURN labels(n)[0] as type, count(n) as count
                ORDER BY type
            """)
            
            neo4j_counts = {record["type"]: record["count"] for record in result}
            
            if neo4j_counts:
                for node_type, count in neo4j_counts.items():
                    print(f"   🕸️  Neo4j: {count} {node_type} nodes")
            else:
                print("   🕸️  Neo4j: No data (expected for fresh install)")
                
    except Exception as e:
        print(f"   ❌ Neo4j Database error: {e}")
        success = False
    
    return success

def show_database_info():
    """Show information about the database setup."""
    print("\n📋 Database Information:")
    print("=" * 50)
    
    # Database URLs
    database_url = os.getenv("DATABASE_URL", "sqlite:///./kimera_swm.db")
    neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    
    print(f"📊 Relational DB: {database_url}")
    print(f"🕸️  Graph DB: {neo4j_uri}")
    
    # File info for SQLite
    if database_url.startswith("sqlite"):
        db_file = database_url.replace("sqlite:///", "").replace("./", "")
        if os.path.exists(db_file):
            size = os.path.getsize(db_file)
            print(f"💾 Database file: {db_file} ({size:,} bytes)")
        else:
            print(f"💾 Database file: {db_file} (will be created)")
    
    print("\n🔧 Next Steps:")
    print("1. Start KIMERA: python run_kimera.py")
    print("2. Test API: curl http://localhost:8000/health")
    print("3. View Neo4j: http://localhost:7474 (if Neo4j enabled)")
    print("4. Run tests: python -m pytest tests/")

def main():
    """Main database builder function."""
    parser = argparse.ArgumentParser(
        description="Build and initialize KIMERA SWM databases",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python build_database.py                    # Basic setup (SQL only)
  python build_database.py --neo4j            # Include Neo4j setup
  python build_database.py --enhanced         # Include enhanced tables
  python build_database.py --neo4j --enhanced # Full setup
  python build_database.py --reset            # Reset and rebuild
        """
    )
    
    parser.add_argument("--neo4j", action="store_true", 
                       help="Initialize Neo4j graph database")
    parser.add_argument("--enhanced", action="store_true",
                       help="Create enhanced understanding tables")
    parser.add_argument("--reset", action="store_true",
                       help="Drop and recreate all tables")
    parser.add_argument("--sample-data", action="store_true",
                       help="Create sample data for testing")
    
    args = parser.parse_args()
    
    print("🚀 KIMERA SWM Database Builder")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Check Neo4j if requested
    neo4j_available = True
    if args.neo4j:
        neo4j_available = check_neo4j_connection()
        if not neo4j_available:
            print("\n⚠️  Neo4j not available. Continuing with SQL-only setup.")
    
    # Initialize relational database
    if not initialize_relational_database(reset=args.reset, enhanced=args.enhanced):
        print("\n❌ Failed to initialize relational database")
        return 1
    
    # Create database indexes
    if not create_database_indexes():
        print("\n⚠️  Warning: Some indexes may not have been created")
    
    # Initialize Neo4j if available and requested
    if args.neo4j and neo4j_available:
        if not initialize_neo4j_database(reset=args.reset):
            print("\n⚠️  Warning: Neo4j initialization failed")
    
    # Create sample data if requested
    if args.sample_data:
        if not create_sample_data():
            print("\n⚠️  Warning: Sample data creation failed")
    
    # Verify setup
    if not verify_database_setup():
        print("\n⚠️  Warning: Database verification had issues")
    
    # Show final information
    show_database_info()
    
    print("\n🎉 Database build completed!")
    
    if args.neo4j and not neo4j_available:
        print("\n💡 To enable Neo4j later:")
        print("1. Start Neo4j: docker run -p 7687:7687 -p 7474:7474 -e NEO4J_AUTH=neo4j/password neo4j:5")
        print("2. Set environment: export NEO4J_PASS='password'")
        print("3. Re-run: python build_database.py --neo4j")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())