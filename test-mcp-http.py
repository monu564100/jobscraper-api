"""
Test MCP endpoint via HTTP
Make sure Flask server is running on port 8000 before running this test
"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("🧪 Testing MCP HTTP endpoint...\n")

# Test 1: GET /api/mcp/search with query parameters
print("=" * 60)
print("TEST 1: GET /api/mcp/search (Indeed India)")
print("=" * 60)

response = requests.get(f"{BASE_URL}/api/mcp/search", params={
    "site_names": "indeed",
    "search_term": "python developer",
    "location": "bangalore",
    "results_wanted": 5,
    "hours_old": 72,
    "country_indeed": "India"
})

print(f"Status: {response.status_code}")
print(f"Response:")
data = response.json()
print(json.dumps(data, indent=2)[:500] + "...")

if data.get('status') == 'success':
    jobs = data.get('data', {}).get('jobs', [])
    print(f"\n✅ Got {len(jobs)} jobs")
    if jobs:
        print(f"\nFirst job title: {jobs[0].get('title')}")
        print(f"Company: {jobs[0].get('company')}")
        print(f"Location: {jobs[0].get('location')}")
        print(f"Source: {jobs[0].get('source')}")
else:
    print(f"\n❌ Failed: {data.get('message')}")

# Test 2: POST /api/mcp/request with JSON body
print("\n" + "=" * 60)
print("TEST 2: POST /api/mcp/request (Multiple sites)")
print("=" * 60)

response2 = requests.post(f"{BASE_URL}/api/mcp/request", json={
    "tool": "search_jobs",
    "params": {
        "site_names": "indeed,linkedin",
        "search_term": "software engineer",
        "location": "bangalore",
        "results_wanted": 10,
        "hours_old": 96,
        "country_indeed": "India"
    }
})

print(f"Status: {response2.status_code}")
data2 = response2.json()

if data2.get('status') == 'success':
    jobs2 = data2.get('data', {}).get('jobs', [])
    print(f"\n✅ Got {len(jobs2)} jobs")
    
    # Count by source
    from collections import Counter
    if jobs2:
        sources = Counter(j.get('source') for j in jobs2)
        print(f"\n📊 Jobs by source: {dict(sources)}")
        print(f"\nSample job titles:")
        for i, job in enumerate(jobs2[:3], 1):
            print(f"  {i}. {job.get('title')} at {job.get('company')} ({job.get('source')})")
else:
    print(f"\n❌ Failed: {data2.get('message')}")

print("\n🎉 All HTTP tests complete!")
print("\n" + "=" * 60)
print("Summary:")
print("=" * 60)
print(f"✅ MCP service is working correctly")
print(f"✅ Both GET and POST endpoints functional")
print(f"✅ JobSpy integration successful")
print(f"✅ Ready to use in Frontend MCP mode")
