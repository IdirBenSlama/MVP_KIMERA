"""Placeholder for ICW implementation."""

from fastapi import Request

async def example_middleware(request: Request, call_next):
    response = await call_next(request)
    return response
