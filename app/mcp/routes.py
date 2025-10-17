from flask import request
from app.helpers.response import ResponseHelper
from . import mcp_bp
from .schemas import SearchJobsParams
from .service import run_jobspy


@mcp_bp.route('/search', methods=['GET'])
def mcp_search():
    try:
        params = SearchJobsParams(
            site_names=request.args.get('site_names') or 'indeed,linkedin',
            search_term=request.args.get('search_term') or request.args.get('keyword') or 'software engineer',
            location=request.args.get('location') or '',
            distance=(int(request.args.get('distance')) if request.args.get('distance') else None),
            job_type=request.args.get('job_type'),
            google_search_term=request.args.get('google_search_term'),
            results_wanted=(int(request.args.get('results_wanted')) if request.args.get('results_wanted') else 20),
            easy_apply=(request.args.get('easy_apply') == 'true' if request.args.get('easy_apply') else None),
            description_format=request.args.get('description_format'),
            offset=(int(request.args.get('offset')) if request.args.get('offset') else None),
            hours_old=(int(request.args.get('hours_old')) if request.args.get('hours_old') else 96),
            verbose=(int(request.args.get('verbose')) if request.args.get('verbose') else None),
            country_indeed=request.args.get('country_indeed'),
            is_remote=(request.args.get('is_remote') == 'true' if request.args.get('is_remote') else None),
            linkedin_fetch_description=(request.args.get('linkedin_fetch_description') == 'true' if request.args.get('linkedin_fetch_description') else None),
            linkedin_company_ids=request.args.get('linkedin_company_ids'),
            enforce_annual_salary=(request.args.get('enforce_annual_salary') == 'true' if request.args.get('enforce_annual_salary') else None),
            proxies=request.args.get('proxies'),
            ca_cert=request.args.get('ca_cert'),
        )
        jobs = run_jobspy(params)
        print(f"🎯 MCP endpoint returning {len(jobs)} jobs")
        print(f"📋 First job sample: {jobs[0] if jobs else 'No jobs'}")
        return ResponseHelper.success_response('Success fetching MCP jobs', { 'jobs': jobs })
    except Exception as e:
        print(f"❌ MCP endpoint error: {str(e)}")
        import traceback
        traceback.print_exc()
        return ResponseHelper.failure_response(f'MCP error: {str(e)}', status_code=500)


@mcp_bp.route('/request', methods=['POST'])
def mcp_request():
    try:
        payload = request.get_json(force=True, silent=True) or {}
        tool = payload.get('tool') or payload.get('method')
        if tool != 'search_jobs':
            return ResponseHelper.failure_response('Unsupported tool. Only search_jobs is implemented.', status_code=400)
        params_dict = payload.get('params') or {}
        params = SearchJobsParams(**params_dict)
        jobs = run_jobspy(params)
        return ResponseHelper.success_response('Success fetching MCP jobs', { 'jobs': jobs })
    except Exception as e:
        return ResponseHelper.failure_response(f'MCP error: {str(e)}', status_code=500)
