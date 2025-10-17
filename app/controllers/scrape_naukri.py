import requests
from datetime import datetime
from typing import List, Dict, Any
from app.helpers.response import ResponseHelper


def _infer_remote(text: str) -> bool:
    t = (text or '').lower()
    return ('remote' in t) or ('work from home' in t) or ('wfh' in t)


def _iso_date_from_epoch(ms: int) -> str:
    try:
        return datetime.fromtimestamp(ms / 1000).strftime('%Y-%m-%d')
    except Exception:
        return ''


def _extract_location(placeholders: List[Dict[str, Any]]) -> str:
    try:
        for p in placeholders or []:
            if p.get('type') == 'location':
                return p.get('label') or ''
    except Exception:
        pass
    return ''


def scrape_naukri(keyword: str = 'developer', location: str = '', limit: int = 20) -> Any:
    base_url = 'https://www.naukri.com/jobapi/v3/search'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/html, */*',
        'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8',
        'Referer': 'https://www.naukri.com/',
    }

    jobs: List[Dict[str, Any]] = []
    page = 1
    per_page = 20

    try:
        while len(jobs) < limit:
            params = {
                'noOfResults': per_page,
                'urlType': 'search_by_keyword',
                'searchType': 'adv',
                'keyword': keyword,
                'pageNo': page,
                'seoKey': f"{(keyword or '').lower().replace(' ', '-')}-jobs",
                'src': 'jobsearchDesk',
                'latLong': '',
                'location': location,
            }

            resp = requests.get(base_url, headers=headers, params=params, timeout=20)
            if resp.status_code != 200:
                break
            data = resp.json()
            job_details = data.get('jobDetails') or []
            if not job_details:
                break

            for jd in job_details:
                title = jd.get('title') or 'N/A'
                company = jd.get('companyName') or 'N/A'
                loc = _extract_location(jd.get('placeholders') or []) or location
                created = jd.get('createdDate')
                posted_on = _iso_date_from_epoch(created) if created else ''
                desc = (jd.get('jobDescription') or '')
                jd_url = jd.get('jdURL') or ''
                link = f"https://www.naukri.com{jd_url}" if jd_url.startswith('/') else jd_url
                is_remote = _infer_remote(f"{title} {company} {loc} {desc}")

                if title == 'N/A' or company == 'N/A':
                    continue

                jobs.append({
                    'title': title,
                    'company': company,
                    'location': loc,
                    'description': desc[:500],
                    'link': link or 'N/A',
                    'posted_on': posted_on or 'Recently',
                    'isRemote': is_remote,
                    'source': 'Naukri'
                })

                if len(jobs) >= limit:
                    break

            page += 1

        return ResponseHelper.success_response('Success scraping Naukri jobs', {
            'jobs': jobs,
            'pagination': {
                'current_page': page,
                'last_page': page,
                'next_page': None
            }
        })
    except Exception as e:
        return ResponseHelper.failure_response(f'Error scraping Naukri: {str(e)}', status_code=500)
