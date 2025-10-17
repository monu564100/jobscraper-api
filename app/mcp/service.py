import json
import math
from typing import Dict, Any, List
from datetime import datetime

from .schemas import SearchJobsParams


def is_nan_value(value: Any) -> bool:
    """Return True if value is a NaN-like value."""
    try:
        # NaN is the only value that is not equal to itself
        return value != value  # type: ignore[comparison-overlap]
    except Exception:
        return False


def pick(*values: Any, default: Any = '') -> Any:
    """Return the first value that is not None/NaN/empty-string; otherwise default."""
    for v in values:
        if v is None:
            continue
        if is_nan_value(v):
            continue
        if isinstance(v, str):
            # Filter out 'nan' strings and blanks
            if v.strip() == '' or v.strip().lower() == 'nan':
                continue
            return v
        return v
    return default


def convert_date_to_string(date_value: Any) -> str:
    """Convert various date types to safe string for JSON; handle NaN/None."""
    if date_value is None or is_nan_value(date_value):
        return ''
    if isinstance(date_value, datetime):
        return date_value.isoformat()
    try:
        return str(date_value)
    except Exception:
        return ''


def normalize_job(job: Dict[str, Any]) -> Dict[str, Any]:
    # Safely pick values and coerce to strings where appropriate
    title = str(pick(job.get('title'), job.get('job_title'), default='N/A'))
    company = str(pick(job.get('company'), job.get('company_name'), default='N/A'))
    location = str(pick(job.get('location'), job.get('job_location'), default=''))
    desc = str(pick(job.get('description'), default=''))
    link = str(pick(job.get('url'), job.get('job_url'), default=''))
    posted_raw = pick(job.get('date_posted'), job.get('datePosted'), default='')
    source = str(pick(job.get('site'), job.get('via'), default='JobSpy'))

    # Determine remote flag safely
    is_remote_raw = job.get('is_remote')
    if isinstance(is_remote_raw, bool):
        is_remote = is_remote_raw
    else:
        is_remote = 'remote' in f"{location} {desc}".lower()

    return {
        'title': title,
        'company': company,
        'location': location,
        'description': desc,
        'link': link,
        'posted_on': convert_date_to_string(posted_raw),
        'isRemote': bool(is_remote),
        'source': source,
        'via': source,
    }


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
    
        # Parse site_names from comma-separated string
    site_list = []
    if params.site_names:
        site_list = [s.strip() for s in params.site_names.split(',')]
    
    # Validate site names
    valid_sites = ['linkedin', 'indeed', 'zip_recruiter', 'glassdoor', 'google', 'bayt', 'naukri', 'bdjobs']
    invalid_sites = [s for s in site_list if s and s not in valid_sites]
    if invalid_sites:
        print(f"⚠️ Invalid site names detected: {invalid_sites}")
        print(f"✅ Valid sites are: {valid_sites}")
        # Remove invalid sites
        site_list = [s for s in site_list if s in valid_sites]
    
    print(f"📋 Parsed sites: {site_list}")
    
    # Parse proxies if provided
    proxies = None
    if params.proxies:
        proxies = [p.strip() for p in params.proxies.split(',')]
    
    # Parse LinkedIn company IDs if provided
    linkedin_company_ids = None
    if params.linkedin_company_ids:
        try:
            linkedin_company_ids = [int(id.strip()) for id in params.linkedin_company_ids.split(',')]
        except ValueError:
            linkedin_company_ids = None
    
    # Prepare kwargs - only include non-None values
    kwargs = {
        'site_name': site_list,
        'search_term': params.search_term or 'software engineer',
        'results_wanted': params.results_wanted or 20,
        'hours_old': params.hours_old or 96,
        'country_indeed': params.country_indeed or 'USA',
    }
    
    # Add optional parameters only if provided
    if params.location:
        kwargs['location'] = params.location
    if params.distance:
        kwargs['distance'] = params.distance
    if params.job_type:
        kwargs['job_type'] = params.job_type
    if params.is_remote:
        kwargs['is_remote'] = True
    if params.easy_apply:
        kwargs['easy_apply'] = True
    if params.offset:
        kwargs['offset'] = params.offset
    if params.description_format:
        kwargs['description_format'] = params.description_format
    if params.linkedin_fetch_description:
        kwargs['linkedin_fetch_description'] = True
    if linkedin_company_ids:
        kwargs['linkedin_company_ids'] = linkedin_company_ids
    if params.enforce_annual_salary:
        kwargs['enforce_annual_salary'] = True
    if proxies:
        kwargs['proxies'] = proxies
    if params.ca_cert:
        kwargs['ca_cert'] = params.ca_cert
    if params.verbose is not None:
        kwargs['verbose'] = params.verbose
    
    print(f"📞 Calling scrape_jobs with: {kwargs}")
    
    try:
        # Call JobSpy scraper
        jobs_df = scrape_jobs(**kwargs)
        
        print(f"✅ JobSpy returned: {type(jobs_df)}, len={len(jobs_df) if jobs_df is not None else 0}")
        
        # Handle None or empty DataFrame
        if jobs_df is None or len(jobs_df) == 0:
            print("⚠️ No jobs found by JobSpy")
            return []
        
        # Convert DataFrame to list of dicts
        jobs_list = jobs_df.to_dict('records')
        print(f"📦 Converted to {len(jobs_list)} job records")
        
        # Normalize each job
        normalized = [normalize_job(j) for j in jobs_list]
        print(f"🎉 Returning {len(normalized)} normalized jobs")
        return normalized
        
    except Exception as e:
        print(f"❌ JobSpy error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
