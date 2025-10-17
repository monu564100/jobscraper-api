"""
Aggregate Jobs Controller
Returns top 20 filtered jobs from all sources
"""

from flask import jsonify, request
import asyncio
from app.services.job_aggregator import aggregate_jobs


def get_aggregate_jobs():
    """
    Fetch, analyze, and return top 20 jobs from all sources
    Query params:
    - keyword: Job title/keyword
    - location: Job location
    - jobTitle: User's preferred job title (for scoring)
    """
    try:
        # Get query parameters
        keyword = request.args.get('keyword', 'developer')
        location = request.args.get('location', '')
        job_title = request.args.get('jobTitle', keyword)
        work_mode = request.args.get('workMode', '')  # remote | hybrid | onsite | any
        max_days_old = request.args.get('maxDaysOld', '14')
        
        # User preferences for scoring
        user_preferences = {
            'jobTitle': job_title,
            'location': location,
            'workMode': work_mode,
            'maxDaysOld': max_days_old
        }
        
        print(f"🎯 Aggregating jobs for: {keyword} in {location}")
        
        # Run async aggregation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            aggregate_jobs(keyword, location, user_preferences)
        )
        loop.close()
        
        if result['status'] == 'success':
            return jsonify(result), 200
        else:
            return jsonify(result), 503
            
    except Exception as e:
        print(f"❌ Aggregation error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'status': 'failed',
            'message': f'Job aggregation error: {str(e)}',
            'data': {'jobs': []},
            'progress': 100
        }), 500
