"""
JobSpy Proxy Controller
Runs the jobspy docker image to fetch jobs and normalizes output
"""

import json
import subprocess
from flask import request
from app.helpers.response import ResponseHelper


def _build_args(params: dict) -> list:
    args = []
    mapping = {
        'site_names': '--site_name',
        'search_term': '--search_term',
        'location': '--location',
        'distance': '--distance',
        'job_type': '--job_type',
        'google_search_term': '--google_search_term',
        'results_wanted': '--results_wanted',
        'easy_apply': '--easy_apply',
        'description_format': '--description_format',
        'offset': '--offset',
        'hours_old': '--hours_old',
        'verbose': '--verbose',
        'country_indeed': '--country_indeed',
        'is_remote': '--is_remote',
        'linkedin_fetch_description': '--linkedin_fetch_description',
        'linkedin_company_ids': '--linkedin_company_ids',
        'enforce_annual_salary': '--enforce_annual_salary',
        'proxies': '--proxies',
        'ca_cert': '--ca_cert'
    }
    for key, flag in mapping.items():
        if key in params and params[key] not in (None, '', 0, False):
            if isinstance(params[key], bool):
                if params[key]:
                    args.append(flag)
            else:
                args.extend([flag, str(params[key])])
    args.extend(['--format', 'json'])
    return args


def jobspy_search():
    try:
        # Read query params
        params = {
            'site_names': request.args.get('site_names', 'indeed,linkedin'),
            'search_term': request.args.get('search_term') or request.args.get('keyword', 'developer'),
            'location': request.args.get('location', ''),
            'results_wanted': request.args.get('results_wanted', '20'),
            'hours_old': request.args.get('hours_old', '96')
        }

        args = _build_args(params)
        cmd = ['docker', 'run', '--rm', 'jobspy'] + args

        # Execute with timeout
        raw = subprocess.check_output(cmd, timeout=60)
        data = json.loads(raw.decode('utf-8', errors='ignore'))

        # Normalize fields similar to other scrapers
        jobs = []
        for j in data:
            title = j.get('title') or j.get('job_title') or 'N/A'
            company = j.get('company') or j.get('company_name') or 'N/A'
            location = j.get('location') or j.get('job_location') or ''
            desc = j.get('description') or ''
            link = j.get('url') or j.get('job_url') or ''
            posted = j.get('date_posted') or j.get('datePosted') or ''
            is_remote = j.get('is_remote') or ('remote' in f"{location} {desc}".lower())
            jobs.append({
                'title': title,
                'company': company,
                'location': location,
                'description': desc,
                'link': link,
                'posted_on': posted,
                'isRemote': bool(is_remote),
                'source': j.get('site') or j.get('via') or 'JobSpy'
            })

        return ResponseHelper.success_response('Success fetching from JobSpy', {
            'jobs': jobs
        })
    except subprocess.TimeoutExpired:
        return ResponseHelper.failure_response('JobSpy request timed out', status_code=504)
    except Exception as e:
        return ResponseHelper.failure_response(f'JobSpy error: {str(e)}', status_code=500)
