import requests
import time
from statistics import mean

API_BASE = "http://localhost:8001"  # Adjust port if needed
ENDPOINTS = ["/system/status", "/system/stability"]
ITERATIONS = 100

results = {ep: [] for ep in ENDPOINTS}
errors = {ep: 0 for ep in ENDPOINTS}

print(f"Starting stress test on endpoints: {ENDPOINTS}")

for i in range(ITERATIONS):
    for ep in ENDPOINTS:
        url = API_BASE + ep
        start = time.time()
        try:
            resp = requests.get(url, timeout=5)
            elapsed = time.time() - start
            results[ep].append(elapsed)
            if resp.status_code != 200:
                errors[ep] += 1
                print(f"[ERROR] {url} returned status {resp.status_code}")
        except Exception as e:
            errors[ep] += 1
            print(f"[EXCEPTION] {url}: {e}")

print("\n--- Stress Test Summary ---")
for ep in ENDPOINTS:
    times = results[ep]
    print(f"Endpoint: {ep}")
    print(f"  Requests: {len(times)}")
    print(f"  Errors: {errors[ep]}")
    if times:
        print(f"  Avg Response Time: {mean(times):.4f}s")
        print(f"  Min Response Time: {min(times):.4f}s")
        print(f"  Max Response Time: {max(times):.4f}s")
    print()

