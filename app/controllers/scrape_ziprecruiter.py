import requests
from datetime import datetime
from typing import List, Dict, Any
from app.helpers.response import ResponseHelper


def _map_country(code: str) -> str:
    if code == 'US':
        return 'USA'
    if code == 'CA':
        return 'Canada'
    return code or ''


def scrape_ziprecruiter(search_term: str = '', location: str = '', distance: int = 50, job_type: str = '', is_remote: bool = False, hours_old: int = 96, page: int = 1) -> Any:
    base_url = 'https://api.ziprecruiter.com/jobs-app/jobs'
    params: Dict[str, Any] = {}

    if search_term:
        params['search'] = search_term
    if location:
        params['location'] = location
    if distance:
        params['radius'] = str(distance)
    if job_type:
        params['employment_types'] = job_type
    if is_remote:
        params['remote_jobs_only'] = 'true'
    if hours_old:
        if hours_old <= 24:
            params['days'] = '1'
        elif hours_old <= 168:
            params['days'] = '7'
        elif hours_old <= 720:
            params['days'] = '30'

    params['page'] = str(page)

    try:
        resp = requests.get(base_url, params=params, timeout=20)
        if resp.status_code != 200:
            return ResponseHelper.failure_response(f'ZipRecruiter HTTP {resp.status_code}', status_code=resp.status_code)
        data = resp.json() or {}
        job_posts = data.get('jobs') or []
        jobs: List[Dict[str, Any]] = []

        for job in job_posts:
            title = job.get('name') or 'N/A'
            company = (job.get('hiring_company') or {}).get('name') or 'N/A'
            city = job.get('job_city') or ''
            state = job.get('job_state') or ''
            country = _map_country(job.get('job_country') or '')
            loc_parts = [p for p in [city, state, country] if p]
            loc = ', '.join(loc_parts)

            listing_key = job.get('listing_key') or ''
            job_url = f"https://www.ziprecruiter.com/jobs//j?lvk={listing_key}" if listing_key else ''
            desc = job.get('job_description') or ''
            posted = job.get('posted_time')
            posted_on = ''
            try:
                if posted:
                    posted_on = datetime.fromtimestamp(int(posted)).strftime('%Y-%m-%d')
            except Exception:
                posted_on = ''

            if title == 'N/A' or company == 'N/A':
                continue

            jobs.append({
                'title': title,
                'company': company,
                'location': loc,
                'description': desc[:500],
                'link': job_url or 'N/A',
                'posted_on': posted_on or 'Recently',
                'source': 'ZipRecruiter'
            })

        return ResponseHelper.success_response('Success scraping ZipRecruiter jobs', {
            'jobs': jobs,
            'pagination': {
                'current_page': page,
                'last_page': page,
                'next_page': None
            }
        })
    except Exception as e:
        return ResponseHelper.failure_response(f'Error scraping ZipRecruiter: {str(e)}', status_code=500)
