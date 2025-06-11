from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.vault.database import ScarDB, Base
import json

# Create engine and session
engine = create_engine('sqlite:///stress_test.db')
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

# Get all scars
scars = session.query(ScarDB).all()

print(f"\nTotal number of scars: {len(scars)}")

# Analyze scar patterns
reason_counts = {}
resolved_by_counts = {}
entropy_ranges = []
semantic_polarities = []

for scar in scars:
    # Count reasons
    reason_counts[scar.reason] = reason_counts.get(scar.reason, 0) + 1
    
    # Count resolvers
    resolved_by_counts[scar.resolved_by] = resolved_by_counts.get(scar.resolved_by, 0) + 1
    
    # Track entropy changes
    entropy_ranges.append(scar.delta_entropy)
    
    # Track semantic polarities
    semantic_polarities.append(scar.semantic_polarity)

print("\nMost common reasons for scars:")
for reason, count in sorted(reason_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
    print(f"- {reason}: {count} scars")

print("\nResolvers of contradictions:")
for resolver, count in sorted(resolved_by_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"- {resolver}: {count} scars")

print(f"\nEntropy Analysis:")
print(f"- Average entropy change: {sum(entropy_ranges)/len(entropy_ranges):.3f}")
print(f"- Max entropy change: {max(entropy_ranges):.3f}")
print(f"- Min entropy change: {min(entropy_ranges):.3f}")

print(f"\nSemantic Polarity Analysis:")
print(f"- Average polarity: {sum(semantic_polarities)/len(semantic_polarities):.3f}")
print(f"- Max polarity: {max(semantic_polarities):.3f}")
print(f"- Min polarity: {min(semantic_polarities):.3f}")

# Print some example scars
print("\nExample scars:")
for scar in scars[:3]:
    print(f"\nScar ID: {scar.scar_id}")
    print(f"Reason: {scar.reason}")
    print(f"Resolved by: {scar.resolved_by}")
    print(f"Entropy change: {scar.delta_entropy:.3f}")
    print(f"Semantic polarity: {scar.semantic_polarity:.3f}")
    print(f"Geoids involved: {scar.geoids}") 