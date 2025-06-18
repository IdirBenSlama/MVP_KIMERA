# Additional methods to add to UnderstandingVaultManager

def get_all_geoids(self) -> List[GeoidState]:
    """Get all geoids from the database."""
    from .database import GeoidDB
    
    with SessionLocal() as db:
        geoid_rows = db.query(GeoidDB).all()
        geoids = []
        for row in geoid_rows:
            try:
                geoid = GeoidState(
                    geoid_id=row.geoid_id,
                    semantic_state=row.semantic_state_json or {},
                    symbolic_state=row.symbolic_state or {},
                    embedding_vector=row.semantic_vector if row.semantic_vector is not None else [],
                    metadata=row.metadata_json or {}
                )
                geoids.append(geoid)
            except Exception:
                continue
        return geoids

def get_total_scar_count(self, vault_id: str) -> int:
    """Get total count of SCARs in a vault."""
    from .database import ScarDB
    
    with SessionLocal() as db:
        return db.query(ScarDB).filter(ScarDB.vault_id == vault_id).count()

def insert_scar(self, scar: ScarRecord, vector: List[float]) -> ScarRecord:
    """Insert a SCAR into the database."""
    from .database import ScarDB
    
    with SessionLocal() as db:
        # Determine vault based on simple hash
        vault_id = "vault_a" if hash(scar.scar_id) % 2 == 0 else "vault_b"
        
        scar_db = ScarDB(
            scar_id=scar.scar_id,
            geoids=scar.geoids,
            reason=scar.reason,
            timestamp=datetime.fromisoformat(scar.timestamp),
            resolved_by=scar.resolved_by,
            pre_entropy=scar.pre_entropy,
            post_entropy=scar.post_entropy,
            delta_entropy=scar.delta_entropy,
            cls_angle=scar.cls_angle,
            semantic_polarity=scar.semantic_polarity,
            mutation_frequency=scar.mutation_frequency,
            weight=scar.weight,
            vault_id=vault_id,
            scar_vector=vector
        )
        
        db.add(scar_db)
        db.commit()
        db.refresh(scar_db)
        
        # Also create enhanced SCAR
        self.create_understanding_scar(
            scar,
            understanding_depth=0.5,
            causal_understanding={},
            compositional_analysis={},
            contextual_factors={},
            introspective_accuracy=0.5
        )
        
        return scar

def get_scars_from_vault(self, vault_id: str, limit: int = 10) -> List[ScarRecord]:
    """Get SCARs from a specific vault."""
    from .database import ScarDB
    
    with SessionLocal() as db:
        scar_rows = db.query(ScarDB).filter(
            ScarDB.vault_id == vault_id
        ).order_by(ScarDB.timestamp.desc()).limit(limit).all()
        
        scars = []
        for row in scar_rows:
            scar = ScarRecord(
                scar_id=row.scar_id,
                geoids=row.geoids,
                reason=row.reason,
                timestamp=row.timestamp.isoformat(),
                resolved_by=row.resolved_by,
                pre_entropy=row.pre_entropy,
                post_entropy=row.post_entropy,
                delta_entropy=row.delta_entropy,
                cls_angle=row.cls_angle,
                semantic_polarity=row.semantic_polarity,
                mutation_frequency=row.mutation_frequency,
                weight=row.weight
            )
            scars.append(scar)
        
        return scars

def rebalance_vaults(self, by_weight: bool = False) -> int:
    """Rebalance SCARs between vaults."""
    from .database import ScarDB
    
    with SessionLocal() as db:
        vault_a_count = db.query(ScarDB).filter(ScarDB.vault_id == "vault_a").count()
        vault_b_count = db.query(ScarDB).filter(ScarDB.vault_id == "vault_b").count()
        
        moved = 0
        if abs(vault_a_count - vault_b_count) > 10:  # Threshold for rebalancing
            # Move SCARs from larger vault to smaller
            source_vault = "vault_a" if vault_a_count > vault_b_count else "vault_b"
            target_vault = "vault_b" if vault_a_count > vault_b_count else "vault_a"
            
            to_move = abs(vault_a_count - vault_b_count) // 2
            
            scars_to_move = db.query(ScarDB).filter(
                ScarDB.vault_id == source_vault
            ).limit(to_move).all()
            
            for scar in scars_to_move:
                scar.vault_id = target_vault
                moved += 1
            
            db.commit()
        
        return moved