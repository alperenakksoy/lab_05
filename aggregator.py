import requests
import json
import time


PEERS = {
    "My_API": "http://localhost:8000/api/v1/vehicles",
    "Peer_1": "http://192.168.1.50:8000/api/v1/vehicles",
    "Peer_2": "http://192.168.1.51:8000/api/v1/vehicles",
}

HEADERS = {
    "X-API-Key": "fleet-secret-key",
    "Accept": "application/json",
}

def fetch_from_peer(name, url):

    print(f"[{name}] Connecting: {url}")
    try:
        response = requests.get(url, headers=HEADERS, timeout=3.0)

        if response.status_code == 200:
            data = response.json()
            print(f"[{name}] OK — {len(data)} vehicles fetched.")
            for item in data:
                item["_source"] = name
            return data
        else:
            print(f"[{name}] ERROR — HTTP {response.status_code}")
            return []

    except requests.exceptions.RequestException as e:
        print(f"[{name}] UNREACHABLE — {type(e).__name__}")
        return []

def aggregate_data():
    merged_fleet = []
    source_summary = {}

    start_time = time.time()

    for peer_name, peer_url in PEERS.items():
        vehicles = fetch_from_peer(peer_name, peer_url)
        merged_fleet.extend(vehicles)
        source_summary[peer_name] = {
            "url": peer_url,
            "vehicle_count": len(vehicles),
            "status": "ok" if vehicles else "failed",
        }

    duration = time.time() - start_time

    print("\n" + "=" * 50)
    print(f"  AGGREGATION COMPLETE in {duration:.2f}s")
    print("=" * 50)
    for name, info in source_summary.items():
        icon = "OK  " if info["status"] == "ok" else "FAIL"
        print(f"  [{icon}] {name:12} -> {info['vehicle_count']} vehicles")
    print(f"\n  Total vehicles: {len(merged_fleet)}")
    print("=" * 50)

    print("\nMerged Fleet:")
    print(json.dumps(merged_fleet, indent=2, default=str))


    result = {
        "aggregated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "duration_seconds": round(duration, 3),
        "sources": source_summary,
        "total_vehicles": len(merged_fleet),
        "merged_fleet": merged_fleet,
    }
    with open("aggregated_result.json", "w") as f:
        json.dump(result, f, indent=2, default=str)
    print("\nSaved -> aggregated_result.json")

if __name__ == "__main__":
    aggregate_data()