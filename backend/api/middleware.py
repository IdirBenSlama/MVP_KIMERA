from fastapi import Request
import json

with open("backend/core/cim_profiles.json") as f:
    CIM_PROFILES = json.load(f)

async def icw_middleware(request: Request, call_next):
    profile_name = request.headers.get("X-Kimera-Profile", "default")
    profile = CIM_PROFILES.get(profile_name, {})
    request.state.kimera_profile = profile
    response = await call_next(request)
    return response
