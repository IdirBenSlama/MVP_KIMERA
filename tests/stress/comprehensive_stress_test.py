import asyncio
import httpx
import time
import random
import logging

# --- Configuration ---
API_BASE_URL = "http://127.0.0.1:8000"
NUM_GEOIDS_TO_CREATE = 2000
CONCURRENT_REQUESTS = 100
CONTRADICTION_CYCLES = 50

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def create_geoid(client: httpx.AsyncClient) -> str:
    """Creates a single geoid with random semantic features."""
    payload = {
        "semantic_features": {
            f"feature_{i}": random.uniform(-1.0, 1.0) for i in range(10)
        }
    }
    try:
        response = await client.post(f"{API_BASE_URL}/geoids", json=payload, timeout=30)
        response.raise_for_status()
        return response.json().get("geoid_id")
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        logging.error(f"Error creating geoid: {e}")
        return None

async def run_geoid_injection(client: httpx.AsyncClient):
    """Runs the high-volume geoid injection phase."""
    logging.info(f"--- Phase 1: Injecting {NUM_GEOIDS_TO_CREATE} geoids with {CONCURRENT_REQUESTS} concurrent requests ---")
    start_time = time.time()
    
    tasks = [create_geoid(client) for _ in range(NUM_GEOIDS_TO_CREATE)]
    results = await asyncio.gather(*tasks)
    
    end_time = time.time()
    duration = end_time - start_time
    
    successful_creations = [res for res in results if res]
    failure_rate = (1 - len(successful_creations) / NUM_GEOIDS_TO_CREATE) * 100
    
    logging.info(f"Injection Complete. Duration: {duration:.2f}s")
    logging.info(f"Geoids created per second: {NUM_GEOIDS_TO_CREATE / duration:.2f}")
    logging.info(f"Failure Rate: {failure_rate:.2f}%")
    
    return successful_creations

async def run_contradiction_load(client: httpx.AsyncClient, geoid_ids: list):
    """Runs the contradiction processing load phase."""
    logging.info(f"--- Phase 2: Running {CONTRADICTION_CYCLES} contradiction cycles on {len(geoid_ids)} geoids ---")
    
    payload = {"geoid_ids": geoid_ids}
    cycle_times = []
    
    for i in range(CONTRADICTION_CYCLES):
        start_time = time.time()
        try:
            response = await client.post(f"{API_BASE_URL}/process/contradictions", json=payload, timeout=120)
            response.raise_for_status()
            end_time = time.time()
            duration = end_time - start_time
            cycle_times.append(duration)
            logging.info(f"Cycle {i+1}/{CONTRADICTION_CYCLES} complete in {duration:.2f}s. Detections: {response.json().get('contradictions_detected')}")
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            logging.error(f"Error in contradiction cycle {i+1}: {e}")

    if cycle_times:
        logging.info(f"Contradiction Load Complete. Average cycle time: {sum(cycle_times) / len(cycle_times):.2f}s")
    else:
        logging.warning("No contradiction cycles were completed successfully.")

async def get_system_status(client: httpx.AsyncClient):
    """Retrieves and logs the final system status."""
    logging.info("--- Phase 3: Retrieving final system status ---")
    try:
        response = await client.get(f"{API_BASE_URL}/system/status")
        response.raise_for_status()
        status = response.json()
        logging.info(f"Final Status: {status}")
    except httpx.RequestError as e:
        logging.error(f"Could not retrieve system status: {e}")

async def main():
    """Main function to run the comprehensive stress test."""
    logging.info("🚀 Starting Comprehensive Kimera Stress Test 🚀")
    async with httpx.AsyncClient() as client:
        # Phase 1
        geoid_ids = await run_geoid_injection(client)
        
        if not geoid_ids:
            logging.error("No geoids were created. Aborting stress test.")
            return
            
        # Give the server a moment to settle
        await asyncio.sleep(2)
        
        # Phase 2
        await run_contradiction_load(client, geoid_ids)
        
        # Phase 3
        await get_system_status(client)
        
    logging.info("✅ Comprehensive Stress Test Finished ✅")

if __name__ == "__main__":
    asyncio.run(main()) 