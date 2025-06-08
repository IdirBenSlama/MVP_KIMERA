from pydantic import BaseModel
from typing import List, Dict, Optional

class LinguisticGeoid(BaseModel):
    primary_statement: str
    confidence_score: float
    source_geoid_id: str
    supporting_scars: List[Dict] = []
    potential_ambiguities: List[str] = []
    explanation_lineage: str
