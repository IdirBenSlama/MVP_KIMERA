#!/usr/bin/env python3
"""
Database optimization script for Kimera SWM
Implements performance improvements and data cleanup
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import json
import math
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://kimera:kimera_secure_pass_2025@localhost:5432/kimera_swm")

def create_db_engine():
    """Create database engine"""
    return create_engine(DATABASE_URL)

def convert_json_to_jsonb(engine):
    """Convert JSON columns to JSONB for better performance"""
    print("\n🔄 Converting JSON columns to JSONB...")
    
    conversions = [
        # Geoids table
        ("geoids", "symbolic_state"),
        ("geoids", "metadata_json"),
        ("geoids", "semantic_state_json"),
        # SCARs table
        ("scars", "geoids"),
        # Insights table
        ("insights", "echoform_repr"),
        ("insights", "application_domains"),
        # Multimodal groundings
        ("multimodal_groundings", "visual_features"),
        ("multimodal_groundings", "auditory_features"),
        ("multimodal_groundings", "tactile_features"),
        ("multimodal_groundings", "temporal_context"),
        ("multimodal_groundings", "causal_predecessors"),
        ("multimodal_groundings", "causal_successors"),
        ("multimodal_groundings", "causal_mechanisms"),
        ("multimodal_groundings", "physical_properties"),
        ("multimodal_groundings", "spatial_relationships"),
    ]
    
    with engine.connect() as conn:
        for table, column in conversions:
            try:
                # Check if table and column exist
                check_query = text("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = :table AND column_name = :column
                """)
                result = conn.execute(check_query, {"table": table, "column": column}).fetchone()
                
                if result and result[1] == 'json':
                    print(f"   Converting {table}.{column} from JSON to JSONB...")
                    alter_query = text(f"ALTER TABLE {table} ALTER COLUMN {column} TYPE JSONB USING {column}::JSONB")
                    conn.execute(alter_query)
                    conn.commit()
                    print(f"   ✅ Converted {table}.{column}")
                elif result and result[1] == 'jsonb':
                    print(f"   ℹ️  {table}.{column} is already JSONB")
                else:
                    print(f"   ⚠️  {table}.{column} not found or not JSON type")
            except Exception as e:
                print(f"   ❌ Error converting {table}.{column}: {e}")
                conn.rollback()

def clean_infinity_values(engine):
    """Clean up Infinity values in JSON data"""
    print("\n🧹 Cleaning Infinity values in JSON data...")
    
    with engine.connect() as conn:
        # Find and fix Infinity values in multimodal_groundings
        try:
            # Get all records with physical_properties
            query = text("""
                SELECT grounding_id, physical_properties 
                FROM multimodal_groundings 
                WHERE physical_properties IS NOT NULL
            """)
            results = conn.execute(query).fetchall()
            
            fixed_count = 0
            for grounding_id, props in results:
                if props and 'Infinity' in str(props):
                    # Parse and fix the JSON
                    props_str = str(props).replace('Infinity', '9999999999')
                    try:
                        fixed_props = json.loads(props_str) if isinstance(props_str, str) else props
                        
                        # Update the record
                        update_query = text("""
                            UPDATE multimodal_groundings 
                            SET physical_properties = :props 
                            WHERE grounding_id = :id
                        """)
                        conn.execute(update_query, {
                            "props": json.dumps(fixed_props),
                            "id": grounding_id
                        })
                        fixed_count += 1
                    except json.JSONDecodeError:
                        print(f"   ⚠️  Could not fix JSON for {grounding_id}")
            
            conn.commit()
            print(f"   ✅ Fixed {fixed_count} records with Infinity values")
            
        except Exception as e:
            print(f"   ❌ Error cleaning Infinity values: {e}")
            conn.rollback()

def create_optimized_indexes(engine):
    """Create optimized indexes for better performance"""
    print("\n📊 Creating optimized indexes...")
    
    indexes = [
        # JSONB GIN indexes for efficient queries
        "CREATE INDEX IF NOT EXISTS idx_geoids_symbolic_gin ON geoids USING gin (symbolic_state) WHERE symbolic_state IS NOT NULL",
        "CREATE INDEX IF NOT EXISTS idx_geoids_metadata_gin ON geoids USING gin (metadata_json) WHERE metadata_json IS NOT NULL",
        "CREATE INDEX IF NOT EXISTS idx_scars_geoids_gin ON scars USING gin (geoids) WHERE geoids IS NOT NULL",
        "CREATE INDEX IF NOT EXISTS idx_insights_domains_gin ON insights USING gin (application_domains) WHERE application_domains IS NOT NULL",
        
        # Timestamp indexes for time-based queries
        "CREATE INDEX IF NOT EXISTS idx_scars_timestamp ON scars (timestamp DESC)",
        "CREATE INDEX IF NOT EXISTS idx_scars_last_accessed ON scars (last_accessed DESC)",
        "CREATE INDEX IF NOT EXISTS idx_insights_created ON insights (created_at DESC)",
        
        # Composite indexes for common queries
        "CREATE INDEX IF NOT EXISTS idx_scars_vault_timestamp ON scars (vault_id, timestamp DESC)",
        "CREATE INDEX IF NOT EXISTS idx_scars_weight_entropy ON scars (weight DESC, delta_entropy DESC)",
        
        # Vector similarity indexes (for pgvector)
        "CREATE INDEX IF NOT EXISTS idx_geoids_semantic_vector ON geoids USING ivfflat (semantic_vector vector_cosine_ops) WITH (lists = 100)",
        "CREATE INDEX IF NOT EXISTS idx_scars_vector ON scars USING ivfflat (scar_vector vector_cosine_ops) WITH (lists = 100)",
        
        # Text search indexes
        "CREATE INDEX IF NOT EXISTS idx_scars_reason ON scars USING gin (to_tsvector('english', reason)) WHERE reason IS NOT NULL",
        
        # Foreign key indexes
        "CREATE INDEX IF NOT EXISTS idx_multimodal_concept ON multimodal_groundings (concept_id)",
        "CREATE INDEX IF NOT EXISTS idx_causal_cause ON causal_relationships (cause_concept_id)",
        "CREATE INDEX IF NOT EXISTS idx_causal_effect ON causal_relationships (effect_concept_id)",
    ]
    
    with engine.connect() as conn:
        for index_sql in indexes:
            try:
                conn.execute(text(index_sql))
                index_name = index_sql.split("INDEX IF NOT EXISTS ")[1].split(" ON")[0]
                print(f"   ✅ Created index: {index_name}")
            except Exception as e:
                print(f"   ❌ Error creating index: {e}")
        conn.commit()

def analyze_and_vacuum(engine):
    """Run ANALYZE and VACUUM for query optimization"""
    print("\n🔧 Running ANALYZE and VACUUM...")
    
    tables = ["geoids", "scars", "insights", "multimodal_groundings", 
              "causal_relationships", "enhanced_scars"]
    
    with engine.connect() as conn:
        # Need to set isolation level for VACUUM
        conn.execute(text("COMMIT"))
        for table in tables:
            try:
                conn.execute(text(f"VACUUM ANALYZE {table}"))
                print(f"   ✅ Analyzed and vacuumed: {table}")
            except Exception as e:
                print(f"   ❌ Error with {table}: {e}")

def create_materialized_views(engine):
    """Create materialized views for complex queries"""
    print("\n📈 Creating materialized views...")
    
    views = [
        # SCAR resolution patterns
        """
        CREATE MATERIALIZED VIEW IF NOT EXISTS mv_scar_patterns AS
        SELECT 
            s.vault_id,
            COUNT(*) as scar_count,
            AVG(s.delta_entropy) as avg_entropy_reduction,
            AVG(s.semantic_polarity) as avg_polarity,
            AVG(s.mutation_frequency) as avg_mutation_freq,
            MAX(s.timestamp) as last_scar_time
        FROM scars s
        GROUP BY s.vault_id
        """,
        
        # Geoid complexity metrics
        """
        CREATE MATERIALIZED VIEW IF NOT EXISTS mv_geoid_complexity AS
        SELECT 
            g.geoid_id,
            jsonb_array_length(g.symbolic_state->'symbols') as symbol_count,
            jsonb_array_length(g.metadata_json->'tags') as tag_count,
            COUNT(DISTINCT s.scar_id) as related_scars
        FROM geoids g
        LEFT JOIN scars s ON s.geoids ? g.geoid_id
        GROUP BY g.geoid_id, g.symbolic_state, g.metadata_json
        """
    ]
    
    with engine.connect() as conn:
        for view_sql in views:
            try:
                conn.execute(text(view_sql))
                view_name = view_sql.split("VIEW IF NOT EXISTS ")[1].split(" AS")[0]
                print(f"   ✅ Created materialized view: {view_name}")
            except Exception as e:
                print(f"   ❌ Error creating view: {e}")
        conn.commit()

def setup_vector_similarity_functions(engine):
    """Create helper functions for vector similarity search"""
    print("\n🔍 Setting up vector similarity functions...")
    
    functions = [
        # Find similar SCARs
        """
        CREATE OR REPLACE FUNCTION find_similar_scars(
            query_vector vector(1024),
            limit_count int DEFAULT 10
        )
        RETURNS TABLE(
            scar_id varchar,
            similarity float,
            reason varchar,
            delta_entropy float
        ) AS $$
        BEGIN
            RETURN QUERY
            SELECT 
                s.scar_id,
                1 - (s.scar_vector <=> query_vector) as similarity,
                s.reason,
                s.delta_entropy
            FROM scars s
            WHERE s.scar_vector IS NOT NULL
            ORDER BY s.scar_vector <=> query_vector
            LIMIT limit_count;
        END;
        $$ LANGUAGE plpgsql;
        """,
        
        # Find semantically related geoids
        """
        CREATE OR REPLACE FUNCTION find_related_geoids(
            query_geoid_id varchar,
            limit_count int DEFAULT 5
        )
        RETURNS TABLE(
            geoid_id varchar,
            similarity float
        ) AS $$
        DECLARE
            query_vector vector(1024);
        BEGIN
            SELECT semantic_vector INTO query_vector
            FROM geoids
            WHERE geoid_id = query_geoid_id;
            
            RETURN QUERY
            SELECT 
                g.geoid_id,
                1 - (g.semantic_vector <=> query_vector) as similarity
            FROM geoids g
            WHERE g.geoid_id != query_geoid_id
                AND g.semantic_vector IS NOT NULL
            ORDER BY g.semantic_vector <=> query_vector
            LIMIT limit_count;
        END;
        $$ LANGUAGE plpgsql;
        """
    ]
    
    with engine.connect() as conn:
        for func_sql in functions:
            try:
                conn.execute(text(func_sql))
                func_name = func_sql.split("FUNCTION ")[1].split("(")[0]
                print(f"   ✅ Created function: {func_name}")
            except Exception as e:
                print(f"   ❌ Error creating function: {e}")
        conn.commit()

def create_neo4j_sync_triggers(engine):
    """Create triggers to sync with Neo4j"""
    print("\n🔄 Setting up Neo4j sync triggers...")
    
    # Create a notification table for Neo4j sync
    with engine.connect() as conn:
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS neo4j_sync_queue (
                    id SERIAL PRIMARY KEY,
                    operation VARCHAR(10),
                    table_name VARCHAR(50),
                    record_id VARCHAR(255),
                    data JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed BOOLEAN DEFAULT FALSE
                )
            """))
            
            # Create trigger function
            conn.execute(text("""
                CREATE OR REPLACE FUNCTION notify_neo4j_sync()
                RETURNS TRIGGER AS $$
                BEGIN
                    INSERT INTO neo4j_sync_queue (operation, table_name, record_id, data)
                    VALUES (
                        TG_OP,
                        TG_TABLE_NAME,
                        CASE 
                            WHEN TG_TABLE_NAME = 'geoids' THEN NEW.geoid_id
                            WHEN TG_TABLE_NAME = 'scars' THEN NEW.scar_id
                            ELSE NULL
                        END,
                        row_to_json(NEW)::jsonb
                    );
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;
            """))
            
            # Create triggers for main tables
            tables = ['geoids', 'scars']
            for table in tables:
                conn.execute(text(f"""
                    CREATE TRIGGER {table}_neo4j_sync
                    AFTER INSERT OR UPDATE ON {table}
                    FOR EACH ROW
                    EXECUTE FUNCTION notify_neo4j_sync()
                """))
            
            conn.commit()
            print("   ✅ Created Neo4j sync triggers")
        except Exception as e:
            print(f"   ❌ Error creating triggers: {e}")
            conn.rollback()

def main():
    """Run all optimization tasks"""
    print("🚀 Kimera SWM Database Optimization")
    print("=" * 50)
    
    engine = create_db_engine()
    
    # Run optimizations
    convert_json_to_jsonb(engine)
    clean_infinity_values(engine)
    create_optimized_indexes(engine)
    create_materialized_views(engine)
    setup_vector_similarity_functions(engine)
    create_neo4j_sync_triggers(engine)
    analyze_and_vacuum(engine)
    
    print("\n✅ Database optimization complete!")
    print("\n📝 Next steps:")
    print("1. Restart Kimera to use optimized database")
    print("2. Monitor query performance")
    print("3. Refresh materialized views periodically")

if __name__ == "__main__":
    main()