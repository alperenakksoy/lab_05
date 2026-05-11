import requests
import time
import statistics
import json


TARGET_URL = "http://localhost:8000/api/v1/vehicles"
HEADERS = {
    "X-API-Key": "fleet-secret-key",
    "Accept": "application/json",
}


def print_stats(label, latencies, success_count, error_count, rate_limit_hits=0):
    total = success_count + error_count
    success_rate = (success_count / total * 100) if total > 0 else 0

    print(f"\n{'─'*50}")
    print(f"  RESULTS: {label}")
    print(f"{'─'*50}")
    print(f"  Total Requests : {total}")
    print(f"  Successful     : {success_count}")
    print(f"  Failed         : {error_count}")
    print(f"  Rate Limited   : {rate_limit_hits}")
    print(f"  Success Rate   : {success_rate:.1f}%")

    if latencies:
        latencies_sorted = sorted(latencies)
        mean   = statistics.mean(latencies_sorted)
        median = statistics.median(latencies_sorted)
        p95 = latencies_sorted[max(0, int(len(latencies_sorted) * 0.95) - 1)]
        p99 = latencies_sorted[max(0, int(len(latencies_sorted) * 0.99) - 1)]

        print(f"  Mean Latency   : {mean*1000:.2f} ms")
        print(f"  Median Latency : {median*1000:.2f} ms")
        print(f"  p95 Latency    : {p95*1000:.2f} ms")
        print(f"  p99 Latency    : {p99*1000:.2f} ms")
    else:
        print("  No successful requests to calculate latency.")

    print(f"{'─'*50}\n")

    result = {
        "scenario": label,
        "total": total,
        "success": success_count,
        "errors": error_count,
        "rate_limited": rate_limit_hits,
        "success_rate_pct": round(success_rate, 1),
    }
    if latencies:
        result.update({
            "mean_ms":   round(statistics.mean(latencies) * 1000, 2),
            "median_ms": round(statistics.median(latencies) * 1000, 2),
            "p95_ms":    round(p95 * 1000, 2),
            "p99_ms":    round(p99 * 1000, 2),
        })
    filename = f"result_{label.lower().replace(' ', '_')}.json"
    with open(filename, "w") as f:
        json.dump(result, f, indent=2)
    print(f"  Saved -> {filename}")


# ─────────────────────────────────────────────
# SCENARIO 1 — Normal Operation (100 requests)
# ─────────────────────────────────────────────
def scenario_1_normal():
    """
    Send 100 requests and measure latency statistics.
    """
    print("\n[SCENARIO 1] Normal Operation — 100 Requests")
    latencies = []
    success = 0
    errors = 0

    for _ in range(100):
        start = time.time()
        try:
            res = requests.get(TARGET_URL, headers=HEADERS, timeout=5.0)
            latency = time.time() - start
            if res.status_code == 200:
                success += 1
                latencies.append(latency)
            else:
                errors += 1
        except requests.exceptions.RequestException:
            errors += 1
        time.sleep(0.05)

    print_stats("Normal Operation", latencies, success, errors)


# ─────────────────────────────────────────────
# SCENARIO 2 — Database Down (30 second polling)
# ─────────────────────────────────────────────
def scenario_2_db_down():
    """
    While this script is running, stop the DB in another terminal:
        docker ps                          # find the db container name
        docker stop <db_container_name>
    Keep sending requests for 30 seconds.
    Expected: 500 or 503 errors once the DB goes down.
    """
    print("\n[SCENARIO 2] Database Down Test — 30 seconds polling")
    print("ACTION: Open another terminal and run:")
    print("        docker ps   # find the db container name")
    print("        docker stop <db_container_name>")
    print("Waiting 5 seconds before starting...\n")
    time.sleep(5)

    end_time = time.time() + 30
    latencies = []
    success = 0
    errors = 0

    while time.time() < end_time:
        start = time.time()
        try:
            res = requests.get(TARGET_URL, headers=HEADERS, timeout=3.0)
            latency = time.time() - start
            status = res.status_code
            if status == 200:
                success += 1
                latencies.append(latency)
                print(f"  200 OK     ({latency*1000:.0f}ms)", end="\r")
            else:
                errors += 1
                print(f"  {status} ERROR  ({latency*1000:.0f}ms)   ", end="\r")
        except requests.exceptions.RequestException as e:
            errors += 1
            print(f"  CONN ERROR — {type(e).__name__}     ", end="\r")
        time.sleep(0.5)

    print()
    print_stats("DB Down", latencies, success, errors)
    print("Remember to restart the DB: docker start <db_container_name>")


# ─────────────────────────────────────────────
# SCENARIO 3 — Container Restart (Recovery Time)
# ─────────────────────────────────────────────
def scenario_3_recovery():
    """
    While this script is running, restart the API container in another terminal:
        docker restart <api_container_name>
    Measures how long until the API returns 200 again (Recovery Time).
    """
    print("\n[SCENARIO 3] Container Restart — Recovery Time")
    print("ACTION: Open another terminal and run:")
    print("        docker restart <api_container_name>")
    print("Polling for 45 seconds...\n")

    end_time = time.time() + 45
    down_start = None
    recovery_time = None
    success = 0
    errors = 0
    latencies = []

    while time.time() < end_time:
        start = time.time()
        try:
            res = requests.get(TARGET_URL, headers=HEADERS, timeout=2.0)
            latency = time.time() - start

            if res.status_code == 200:
                latencies.append(latency)
                success += 1

                # First 200 after a downtime period means recovery is complete
                if down_start is not None and recovery_time is None:
                    recovery_time = time.time() - down_start
                    print(f"\n  RECOVERED! Recovery Time: {recovery_time:.2f} seconds")

                print(f"  200 OK     ({latency*1000:.0f}ms)", end="\r")
            else:
                errors += 1
                if down_start is None:
                    down_start = time.time()
                print(f"  {res.status_code} ERROR              ", end="\r")

        except requests.exceptions.RequestException:
            errors += 1
            if down_start is None:
                down_start = time.time()
            print(f"  CONNECTION LOST                   ", end="\r")

        time.sleep(0.5)

    print()
    if recovery_time:
        print(f"\n  Recovery Time: {recovery_time:.2f} seconds")
    else:
        print("\n  No downtime detected (did you restart the container?)")

    print_stats("Container Restart", latencies, success, errors)


# ─────────────────────────────────────────────
# SCENARIO 4 — Network Latency (tc)
# ─────────────────────────────────────────────
def scenario_4_latency():
    """
    Apply artificial 100ms latency BEFORE running this function, then start the test.

    Linux:
        sudo tc qdisc add dev lo root netem delay 100ms
    Remove after test:
        sudo tc qdisc del dev lo root

    Mac (Network Link Conditioner):
        System Settings -> Network -> ... -> Link Conditioner
        Or: brew install iproute2mac  (limited support)
        Easiest on Mac: use the Network Link Conditioner app from Additional Tools for Xcode.
    """
    print("\n[SCENARIO 4] Network Latency Test")
    print("BEFORE running this test, apply artificial latency:")
    print("")
    print("  Linux : sudo tc qdisc add dev lo root netem delay 100ms")
    print("  Mac   : Use Network Link Conditioner (System Settings)")
    print("")
    input("Press Enter when latency is applied and you are ready...")

    print("\nRunning 50 requests with artificial latency...\n")
    latencies = []
    success = 0
    errors = 0

    for i in range(50):
        start = time.time()
        try:
            res = requests.get(TARGET_URL, headers=HEADERS, timeout=10.0)
            latency = time.time() - start
            if res.status_code == 200:
                success += 1
                latencies.append(latency)
                print(f"  [{i+1:02d}/50] 200 OK  {latency*1000:.0f}ms", end="\r")
            else:
                errors += 1
        except requests.exceptions.RequestException:
            errors += 1
        time.sleep(0.1)

    print()
    print_stats("Network Latency 100ms", latencies, success, errors)
    print("Remove latency when done:")
    print("  Linux: sudo tc qdisc del dev lo root")
    print("  Mac  : Disable Network Link Conditioner")


# ─────────────────────────────────────────────
# SCENARIO 5 — Rate Limit (200 requests / 60s)
# ─────────────────────────────────────────────
def scenario_5_rate_limit():
    """
    Send 200 requests as fast as possible — no sleep.
    Rate limit is 100/minute so 429 responses are expected after the first ~100.
    Expected: first ~100 succeed with 200, the rest return 429.
    """
    print("\n[SCENARIO 5] Rate Limit Test — 200 Requests (no sleep)")
    latencies = []
    success = 0
    errors = 0
    rate_limited = 0

    start_all = time.time()

    for i in range(200):
        start = time.time()
        try:
            res = requests.get(TARGET_URL, headers=HEADERS, timeout=5.0)
            latency = time.time() - start

            if res.status_code == 200:
                success += 1
                latencies.append(latency)
            elif res.status_code == 429:
                rate_limited += 1
                errors += 1
                print(f"  [{i+1:03d}] 429 Rate Limited!     ", end="\r")
            else:
                errors += 1
        except requests.exceptions.RequestException:
            errors += 1

    total_time = time.time() - start_all
    print(f"\n  Completed 200 requests in {total_time:.2f} seconds")
    print_stats("Rate Limiting", latencies, success, errors, rate_limited)

if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  RESILIENCE TEST SUITE — Week 5")
    print("=" * 50)
    print("  1: Normal Operation      (100 requests)")
    print("  2: Database Down         (30s polling — stop DB first)")
    print("  3: Container Restart     (45s polling — restart API first)")
    print("  4: Network Latency       (50 requests — apply tc first)")
    print("  5: Rate Limit Test       (200 requests, no sleep)")
    print("  6: Run ALL scenarios")
    print("=" * 50)

    choice = input("Your choice (1-6): ").strip()

    if choice == "1":
        scenario_1_normal()
    elif choice == "2":
        scenario_2_db_down()
    elif choice == "3":
        scenario_3_recovery()
    elif choice == "4":
        scenario_4_latency()
    elif choice == "5":
        scenario_5_rate_limit()
    elif choice == "6":
        scenario_1_normal()
        scenario_5_rate_limit()
        scenario_3_recovery()

        print("\nScenarios 2 (DB Down) and 4 (Latency) require manual steps.")
        print("Run them separately: python test_resilience.py -> choose 2 or 4")
    else:
        print("Invalid choice.")