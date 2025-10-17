# MCP Server Implementation - Complete Fix

## Problem
MCP endpoint was returning `{"data": {"jobs": []}}` with empty results despite success status.

## Root Cause Analysis

### Original Issue
1. **Docker Dependency**: Initial implementation used `subprocess` to run Docker commands
2. **Windows Error**: `[WinError 2] The system cannot find the file specified` - Docker executable not found
3. **Empty Results**: After fixing Docker, still got empty jobs array

### Investigation Steps
1. Examined `jobspy-mcp-server` reference implementation:
   - Node.js version uses `sudo docker run jobspy --site_name "..." --format json`
   - Executes via `execSync`, parses JSON output
   - Converts to camelCase and normalizes dates

2. Tested `python-jobspy` library directly:
   ```python
   from jobspy import scrape_jobs
   jobs = scrape_jobs(
       site_name=["indeed"],
       search_term="python developer",
       location="bangalore",
       results_wanted=5,
       hours_old=72,
       country_indeed="India",
   )
   # Returns pandas DataFrame with 5 jobs ✅
   ```

3. Found the solution:
   - Library works correctly when called directly
   - Returns pandas DataFrame with columns: `title`, `company`, `location`, `job_url`, `date_posted`, `site`, `is_remote`, etc.
   - Needed proper parameter mapping and debug logging

## Solution Implementation

### 1. Enhanced Service with Debug Logging (`app/mcp/service.py`)

```python
def run_jobspy(params: SearchJobsParams, timeout: int = 60) -> List[Dict[str, Any]]:
    """
    Run JobSpy directly using python-jobspy library
    No Docker required - pure Python implementation
    """
    try:
        from jobspy import scrape_jobs
    except ImportError:
        raise ImportError("python-jobspy not installed. Run: pip install python-jobspy")
    
    print(f"🔍 MCP JobSpy starting with params: {params.model_dump()}")
    
    # Parse site names - must be list
    site_names = [s.strip() for s in (params.site_names or 'indeed,linkedin').split(',')]
    print(f"📋 Searching sites: {site_names}")
    
    # Build kwargs - only include non-None values
    kwargs = {
        'site_name': site_names,
        'search_term': params.search_term or 'software engineer',
        'results_wanted': params.results_wanted or 20,
        'hours_old': params.hours_old or 96,
        'country_indeed': params.country_indeed or 'USA',
    }
    
    # Add optional parameters
    if params.location:
        kwargs['location'] = params.location
    # ... other optional params
    
    print(f"📞 Calling scrape_jobs with: {kwargs}")
    
    # Call JobSpy scraper
    jobs_df = scrape_jobs(**kwargs)
    
    print(f"✅ JobSpy returned: {type(jobs_df)}, len={len(jobs_df)}")
    
    if jobs_df is None or len(jobs_df) == 0:
        print("⚠️ No jobs found by JobSpy")
        return []
    
    jobs_list = jobs_df.to_dict('records')
    print(f"📦 Converted to {len(jobs_list)} job records")
    
    normalized = [normalize_job(j) for j in jobs_list]
    print(f"🎉 Returning {len(normalized)} normalized jobs")
    return normalized
```

### 2. Normalization Function

```python
def normalize_job(job: Dict[str, Any]) -> Dict[str, Any]:
    """
    JobSpy returns: id, site, job_url, job_url_direct, title, company, 
    location, date_posted, job_type, is_remote, description, etc.
    """
    title = job.get('title') or job.get('job_title') or 'N/A'
    company = job.get('company') or job.get('company_name') or 'N/A'
    location = job.get('location') or job.get('job_location') or ''
    desc = job.get('description') or ''
    link = job.get('url') or job.get('job_url') or ''
    posted = job.get('date_posted') or job.get('datePosted') or ''
    source = job.get('site') or job.get('via') or 'JobSpy'
    is_remote = job.get('is_remote') or ('remote' in f"{location} {desc}".lower())
    
    return {
        'title': title,
        'company': company,
        'location': location,
        'description': desc,
        'link': link,
        'posted_on': convert_date_to_string(posted),
        'isRemote': bool(is_remote),
        'source': source,
        'via': source,
    }
```

## Testing

### Direct Library Test
```bash
python test-jobspy-direct.py
```
**Result**: ✅ Returns 5 jobs from Indeed India

### Service Test
```bash
python test-mcp-service.py
```
**Result**: ✅ Both single and multi-site searches work

### HTTP Endpoint Test
```bash
# Start server: python main.py
python test-mcp-http.py
```
**Result**: ✅ Both GET `/api/mcp/search` and POST `/api/mcp/request` work

## Debug Output Example

```
🔍 MCP JobSpy starting with params: {'site_names': 'indeed', 'search_term': 'python developer', ...}
📋 Searching sites: ['indeed']
📞 Calling scrape_jobs with: {'site_name': ['indeed'], 'search_term': 'python developer', ...}
✅ JobSpy returned: <class 'pandas.core.frame.DataFrame'>, len=5
📦 Converted to 5 job records
🎉 Returning 5 normalized jobs
```

## API Usage

### GET Request
```bash
curl "http://localhost:8000/api/mcp/search?site_names=indeed&search_term=python%20developer&location=bangalore&results_wanted=5&hours_old=72&country_indeed=India"
```

### POST Request
```bash
curl -X POST http://localhost:8000/api/mcp/request \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "search_jobs",
    "params": {
      "site_names": "indeed,linkedin",
      "search_term": "software engineer",
      "location": "bangalore",
      "results_wanted": 10,
      "hours_old": 96,
      "country_indeed": "India"
    }
  }'
```

## Frontend Integration

### MCP Mode Toggle
```typescript
// Frontend/app/(tabs)/index.tsx
const mode = useStoredState('sc_mode', 'normal'); // 'normal' | 'mcp'

const loadWithAggregator = async (type: string, useMode?: string) => {
  const currentMode = useMode || mode;
  
  if (currentMode === 'mcp') {
    // MCP Mode - use JobSpy
    const url = `${API_BASE_URL}/api/mcp/search?${params}`;
    // site_names, search_term, location, results_wanted, hours_old
  } else {
    // Normal Mode - use aggregator
    const url = `${API_BASE_URL}/api/aggregate?${params}`;
    // keyword, location, jobTitle, workMode, maxDaysOld
  }
};
```

## Supported Job Sites (via JobSpy)

- ✅ **Indeed** (India, USA, UK, Canada, etc.)
- ✅ **LinkedIn** (Global)
- ✅ **Glassdoor** (USA, UK, etc.)
- ✅ **ZipRecruiter** (USA)
- ✅ **Google Jobs** (Global)
- ✅ **Naukri** (India)
- ✅ **Bayt** (Middle East)

## Parameters Reference

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `site_names` | string | `"indeed,linkedin"` | Comma-separated list of sites |
| `search_term` | string | `"software engineer"` | Job search query |
| `location` | string | `""` | Location to search in |
| `distance` | int | `50` | Distance in miles/km |
| `results_wanted` | int | `20` | Number of results per site |
| `hours_old` | int | `96` | Max age of jobs in hours |
| `country_indeed` | string | `"USA"` | Country for Indeed (`"India"`, `"USA"`, etc.) |
| `is_remote` | boolean | `false` | Remote jobs only |
| `job_type` | string | `null` | `"fulltime"`, `"parttime"`, `"contract"`, etc. |

## Status

- ✅ MCP service implemented with python-jobspy
- ✅ Debug logging added for troubleshooting
- ✅ No Docker dependency required
- ✅ Both GET and POST endpoints working
- ✅ Proper DataFrame to dict conversion
- ✅ Job normalization matching app schema
- ✅ Frontend toggle between Normal/MCP modes
- ✅ Tested with Indeed, LinkedIn (multi-site)

## Next Steps

1. **Performance Optimization**
   - Add caching for repeated searches
   - Implement rate limiting
   - Consider async/concurrent site scraping

2. **Enhanced Features**
   - Add salary filtering
   - Implement job type filtering
   - Add company blacklist/whitelist
   - Enable saved searches

3. **Monitoring**
   - Add request logging
   - Track success/failure rates per site
   - Monitor response times
   - Alert on scraping failures

## Troubleshooting

### Empty Results
- ✅ **Fixed**: Added debug logging to trace execution
- ✅ **Fixed**: Proper parameter mapping to JobSpy library
- ✅ **Fixed**: DataFrame to dict conversion

### Slow Response
- JobSpy scrapes live sites, takes 5-30 seconds per site
- Use `hours_old` to limit freshness requirement
- Reduce `results_wanted` for faster responses

### Site-Specific Issues
- **Indeed**: Requires `country_indeed` parameter
- **LinkedIn**: May need `linkedin_fetch_description=True` for full descriptions
- **ZipRecruiter**: USA only by default

## Files Modified

- ✅ `app/mcp/service.py` - Added debug logging and proper error handling
- ✅ `app/mcp/schemas.py` - Pydantic models for parameters
- ✅ `app/mcp/routes.py` - Flask routes (GET/POST)
- ✅ `app/mcp/__init__.py` - Blueprint registration
- ✅ `app/__init__.py` - MCP blueprint mounted at `/api/mcp`
- ✅ `requirements.txt` - Added `python-jobspy>=1.1.80`
- ✅ `test-jobspy-direct.py` - Direct library test
- ✅ `test-mcp-service.py` - Service layer test
- ✅ `test-mcp-http.py` - HTTP endpoint test

---

**Last Updated**: 2025-01-19  
**Status**: ✅ **WORKING - All tests passing**
