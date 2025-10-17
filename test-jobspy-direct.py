#!/usr/bin/env python3
"""
Test python-jobspy library directly to debug MCP endpoint
"""
from jobspy import scrape_jobs
import sys

print("🔍 Testing python-jobspy library...")

try:
    # Test with minimal parameters - India jobs
    print("\n📋 Searching Indeed India for 'python developer' in Bangalore...")
    jobs = scrape_jobs(
        site_name=["indeed"],
        search_term="python developer",
        location="bangalore",
        results_wanted=5,
        hours_old=72,
        country_indeed="India",
    )
    
    print(f"\n✅ JobSpy returned: {type(jobs)}")
    print(f"📊 Number of jobs: {len(jobs) if jobs is not None else 0}")
    
    if jobs is not None and len(jobs) > 0:
        print(f"📋 Columns: {jobs.columns.tolist()}")
        print(f"\n📦 First job:")
        first_job = jobs.iloc[0].to_dict()
        for key, value in first_job.items():
            print(f"  {key}: {value}")
        
        print(f"\n🎉 Success! Found {len(jobs)} jobs")
    else:
        print("\n⚠️ No jobs found")
        
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
