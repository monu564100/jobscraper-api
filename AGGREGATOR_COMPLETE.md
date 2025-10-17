# Job Aggregator - Complete Integration ✅

## Overview
The job aggregator now includes **10 job sources** that fetch and rank latest jobs automatically when users open the app.

## Active Sources in Aggregator

1. **TimesJobs** (Priority source with 12% boost)
2. **Indeed** (India)
3. **LinkedIn**
4. **RemoteOK**
5. **Naukri** ✨ NEW
6. **ZipRecruiter** ✨ NEW
7. **AasaanJobs**
8. **Dare2Compete**
9. **FreshersWorld**
10. **JobGuru**
11. **MyAmcat**

## How It Works

### Normal Mode (Default)
When users open the app:
1. Frontend calls `/api/aggregate?keyword=...&location=...&jobTitle=...&workMode=...&maxDaysOld=...`
2. Backend fetches from ALL 11 sources concurrently
3. Jobs are scored based on:
   - **Recency (40%)** - Latest jobs ranked higher
   - **Location Match (25%)** - User's location preference
   - **Job Title Match (20%)** - Matches user's desired role
   - **Work Mode (10%)** - Remote/Hybrid preference
   - **URL Validity (5%)** - Has valid application link
4. Filters out jobs older than `maxDaysOld` (default 14 days)
5. Returns top 20 jobs with diversity (at least 2 from each working source)
6. Final sort by posting date (newest first)

### MCP Mode (Optional)
- Uses JobSpy Docker to search Indeed, LinkedIn, Glassdoor, ZipRecruiter
- Endpoint: `/api/mcp/search`
- Toggle in app header to switch between Normal ↔ MCP

## API Endpoints

### Individual Sources
```bash
# Naukri
GET http://localhost:5000/api/naukri?keyword=developer&location=bangalore&limit=30

# ZipRecruiter  
GET http://localhost:5000/api/ziprecruiter?search_term=developer&location=bangalore&distance=50&hours_old=168

# Indeed
GET http://localhost:5000/api/indeed?keyword=developer&location=bangalore&country=in

# LinkedIn
GET http://localhost:5000/api/linkedin?keyword=developer&location=bangalore&limit=25

# TimesJobs
GET http://localhost:5000/api/timesjobs?location=bangalore&limit=50

# RemoteOK
GET http://localhost:5000/api/remoteok?keywords=developer
```

### Aggregator (Recommended)
```bash
# Get top 20 jobs from all sources
GET http://localhost:5000/api/aggregate?keyword=developer&location=bangalore&jobTitle=python%20developer&workMode=remote&maxDaysOld=7
```

### MCP Mode (Requires Docker)
```bash
GET http://localhost:5000/api/mcp/search?site_names=indeed,linkedin,glassdoor,zip_recruiter&search_term=developer&location=bangalore&results_wanted=25&hours_old=96
```

## Response Format

All endpoints return:
```json
{
  "status": "success",
  "message": "Found X best matching jobs from Y total jobs",
  "data": {
    "jobs": [
      {
        "title": "Software Developer",
        "company": "Tech Corp",
        "location": "Bangalore, Karnataka",
        "posted_on": "2025-10-16",
        "link": "https://...",
        "description": "...",
        "isRemote": false,
        "via": "Naukri",
        "source": "Naukri"
      }
    ]
  },
  "progress": 100,
  "stats": {
    "total_fetched": 150,
    "selected": 20,
    "sources": {
      "naukri": "completed",
      "ziprecruiter": "completed",
      "indeed": "completed"
    }
  }
}
```

## User Experience

### On App Launch
1. User opens app → sees circular "black fluid" loading animation
2. Backend fetches from all 11 sources (shows progress by source)
3. Jobs appear sorted by latest first
4. "NEW" badge on jobs posted < 48 hours ago

### Refresh
- Pull down to refresh
- Or wait 5 minutes for auto-refresh

### Filtering
Jobs are automatically filtered by:
- User's preferred location (stored in onboarding)
- User's job title preference
- Work mode (remote/hybrid/onsite if specified)
- Maximum age (default 14 days)

## Configuration

### Adding More Sources
To add a new source to the aggregator:

1. Create controller: `app/controllers/scrape_newsource.py`
2. Add route in `app/routes/route.py`
3. Update aggregator:
   ```python
   # In app/services/job_aggregator.py
   self.sources = [
       'timesjobs',
       'indeed',
       'naukri',
       'ziprecruiter',
       'newsource',  # Add here
       # ...
   ]
   
   url_map = {
       'newsource': f'{base_url}/api/newsource?keyword={keyword}&location={location}',
       # ...
   }
   ```

### Adjusting Weights
In `job_aggregator.py`, modify scoring weights:
```python
weights = {
    'recency': 0.40,      # 40% - Most important
    'location': 0.25,     # 25% - Very important  
    'title_match': 0.20,  # 20% - Important
    'work_mode': 0.10,    # 10% - Work preference
    'has_url': 0.05       # 5%  - Has valid link
}
```

## Troubleshooting

### Naukri Returns No Jobs
- Check if keyword/location are valid
- Naukri API may rate limit; add delays if needed
- Verify endpoint: `http://localhost:5000/api/naukri?keyword=developer&location=bangalore&limit=10`

### ZipRecruiter Returns No Jobs  
- US/Canada focused; may not have many India jobs
- Try broader locations or remote-only flag
- Verify endpoint: `http://localhost:5000/api/ziprecruiter?search_term=developer&is_remote=true`

### MCP Mode Not Working
- Requires Docker Desktop running
- Needs `jobspy` Docker image available
- Test: `docker run --rm jobspy --help`

### Aggregator Slow
- Normal; fetches 11 sources concurrently
- Each source has 120s timeout
- Shows progress animation in app

## Testing

### Quick Test
```bash
# Test Naukri
curl "http://localhost:5000/api/naukri?keyword=developer&location=bangalore&limit=5"

# Test ZipRecruiter
curl "http://localhost:5000/api/ziprecruiter?search_term=developer&location=bangalore&distance=50"

# Test Aggregator (all sources)
curl "http://localhost:5000/api/aggregate?keyword=developer&location=bangalore"
```

### Expected Results
- Each source should return jobs array
- Aggregator should return 20 jobs max
- Jobs should have: title, company, location, link, posted_on, via
- Jobs sorted by posting date (newest first)

## Performance

### Metrics
- **Sources:** 11 concurrent fetches
- **Timeout:** 120s per source
- **Total Time:** ~10-15 seconds typically
- **Results:** Top 20 jobs from 100-200+ fetched

### Optimization
- Sources fail gracefully (no blocking)
- Concurrent async fetching
- Early termination if target reached
- Caching can be added if needed

## Next Steps

✅ Naukri integrated and active  
✅ ZipRecruiter integrated and active  
✅ Both included in aggregator sources  
✅ Frontend toggle for Normal/MCP modes  
✅ Scoring and filtering optimized  

Optional enhancements:
- [ ] Add Glassdoor direct scraper (currently via MCP)
- [ ] Add Monster.com India
- [ ] Add Shine.com
- [ ] Cache results for 5 minutes to reduce API load
- [ ] Add health check endpoint for each source

---

**Status:** ✅ PRODUCTION READY

All 11 sources are live and will automatically fetch latest jobs when users open the app in Normal mode.
