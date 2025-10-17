#!/usr/bin/env python3
"""
Test MCP service directly without Flask
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.mcp.service import run_jobspy
from app.mcp.schemas import SearchJobsParams

print("🧪 Testing MCP service directly...\n")

# Test 1: Basic search
print("=" * 60)
print("TEST 1: Basic Indeed search for Python developer in Bangalore")
print("=" * 60)

params = SearchJobsParams(
    site_names="indeed",
    search_term="python developer",
    location="bangalore",
    results_wanted=5,
    hours_old=72,
    country_indeed="India"
)

try:
    jobs = run_jobspy(params)
    print(f"\n✅ Got {len(jobs)} jobs")
    if jobs:
        print(f"\n📦 First job:")
        first = jobs[0]
        for key, value in first.items():
            if key == 'description':
                print(f"  {key}: {value[:100]}..." if len(value) > 100 else f"  {key}: {value}")
            else:
                print(f"  {key}: {value}")
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()

# Test 2: Multiple sites
print("\n" + "=" * 60)
print("TEST 2: Multiple sites (indeed,linkedin)")
print("=" * 60)

params2 = SearchJobsParams(
    site_names="indeed,linkedin",
    search_term="software engineer",
    location="bangalore",
    results_wanted=10,
    hours_old=96,
    country_indeed="India"
)

try:
    jobs2 = run_jobspy(params2)
    print(f"\n✅ Got {len(jobs2)} jobs")
    
    # Count by source
    from collections import Counter
    sources = Counter(j['source'] for j in jobs2)
    print(f"\n📊 Jobs by source: {dict(sources)}")
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n🎉 All tests complete!")
