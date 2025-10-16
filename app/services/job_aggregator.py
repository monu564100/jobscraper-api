"""
Job Aggregator Service
Fetches jobs from all sources, analyzes, filters, and returns best 20 jobs
"""

import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import re
from difflib import SequenceMatcher

class JobAggregator:
    """
    Aggregates jobs from multiple sources and returns top 20 filtered results
    """
    
    def __init__(self):
        self.sources = [
            'timesjobs',
            'linkedin',
            'remoteok',
            'aasaanjobs',
            'dare2compete',
            'freshersworld',
            'jobguru',
            'myamcat'
        ]
        self.all_jobs = []
        self.progress = {}
        
    def parse_date_to_timestamp(self, date_string: str) -> int:
        """
        Parse various date formats to timestamp
        Returns timestamp in milliseconds (0 if invalid)
        """
        if not date_string or date_string == 'N/A' or date_string.strip() == '':
            return 0
        
        now = datetime.now()
        date_lower = date_string.lower().strip()
        
        # Handle "Just now", "Recently", "Today"
        if date_lower in ['just now', 'recently', 'today']:
            return int(now.timestamp() * 1000)
        
        # Handle "Yesterday"
        if date_lower == 'yesterday':
            return int((now - timedelta(days=1)).timestamp() * 1000)
        
        # Handle relative time: "X time ago"
        relative_match = re.search(r'(\d+)\s*(second|minute|hour|day|week|month|year)s?\s*(ago)?', date_lower)
        if relative_match:
            value = int(relative_match.group(1))
            unit = relative_match.group(2)
            
            delta_map = {
                'second': timedelta(seconds=value),
                'minute': timedelta(minutes=value),
                'hour': timedelta(hours=value),
                'day': timedelta(days=value),
                'week': timedelta(weeks=value),
                'month': timedelta(days=value * 30),
                'year': timedelta(days=value * 365)
            }
            
            if unit in delta_map:
                target_time = now - delta_map[unit]
                return int(target_time.timestamp() * 1000)
        
        # Handle "30+ days ago"
        days_match = re.search(r'(\d+)\+?\s*days?\+?\s*(ago)?', date_lower)
        if days_match:
            days = int(days_match.group(1))
            target_time = now - timedelta(days=days)
            return int(target_time.timestamp() * 1000)
        
        # Handle "last X"
        last_match = re.search(r'last\s+(second|minute|hour|day|week|month|year)', date_lower)
        if last_match:
            unit = last_match.group(1)
            delta_map = {
                'second': timedelta(seconds=1),
                'minute': timedelta(minutes=1),
                'hour': timedelta(hours=1),
                'day': timedelta(days=1),
                'week': timedelta(weeks=1),
                'month': timedelta(days=30),
                'year': timedelta(days=365)
            }
            if unit in delta_map:
                target_time = now - delta_map[unit]
                return int(target_time.timestamp() * 1000)
        
        # Try parsing ISO date
        try:
            parsed = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            return int(parsed.timestamp() * 1000)
        except:
            pass
        
        # Try standard date parsing
        try:
            parsed = datetime.strptime(date_string, '%Y-%m-%d')
            return int(parsed.timestamp() * 1000)
        except:
            pass
        
        return 0
    
    def calculate_location_match_score(self, job_location: str, user_location: str) -> float:
        """
        Calculate how well job location matches user location
        Returns score 0.0 to 1.0
        """
        if not job_location or not user_location:
            return 0.5  # Neutral score if location unknown
        
        job_loc = job_location.lower().strip()
        user_loc = user_location.lower().strip()
        
        # Exact match
        if job_loc == user_loc:
            return 1.0
        
        # Contains user location
        if user_loc in job_loc or job_loc in user_loc:
            return 0.9
        
        # Remote jobs are always good
        if 'remote' in job_loc or 'work from home' in job_loc or 'wfh' in job_loc:
            return 0.95
        
        # Similar using sequence matcher
        similarity = SequenceMatcher(None, job_loc, user_loc).ratio()
        if similarity > 0.7:
            return 0.8
        
        # Check for city variations
        location_mappings = {
            'bangalore': ['bengaluru', 'banglore', 'blr'],
            'mumbai': ['bombay'],
            'delhi': ['new delhi', 'ncr'],
            'chennai': ['madras'],
            'kolkata': ['calcutta'],
            'gurugram': ['gurgaon']
        }
        
        for main_city, variations in location_mappings.items():
            if user_loc in [main_city] + variations:
                if job_loc in [main_city] + variations:
                    return 0.95
        
        return 0.3  # Low score for different locations
    
    def calculate_job_title_match_score(self, job_title: str, user_job_title: str) -> float:
        """
        Calculate how well job title matches user preference
        Returns score 0.0 to 1.0
        """
        if not job_title or not user_job_title:
            return 0.5
        
        job_t = job_title.lower().strip()
        user_t = user_job_title.lower().strip()
        
        # Exact match
        if job_t == user_t:
            return 1.0
        
        # Contains user title
        if user_t in job_t or job_t in user_t:
            return 0.9
        
        # Word overlap
        job_words = set(job_t.split())
        user_words = set(user_t.split())
        common_words = job_words.intersection(user_words)
        
        if len(user_words) > 0:
            overlap_ratio = len(common_words) / len(user_words)
            if overlap_ratio > 0.5:
                return 0.7 + (overlap_ratio * 0.2)
        
        # Similarity
        similarity = SequenceMatcher(None, job_t, user_t).ratio()
        return similarity * 0.8
    
    def calculate_job_score(self, job: Dict[str, Any], user_preferences: Dict[str, str]) -> float:
        """
        Calculate overall job score based on multiple factors
        Higher score = better match
        """
        score = 0.0
        weights = {
            'recency': 0.35,      # 35% - Most important
            'location': 0.30,     # 30% - Very important
            'title_match': 0.25,  # 25% - Important
            'has_url': 0.10       # 10% - Nice to have
        }
        
        # Recency score
        timestamp = self.parse_date_to_timestamp(job.get('posted_on', ''))
        if timestamp > 0:
            now_ms = int(datetime.now().timestamp() * 1000)
            age_hours = (now_ms - timestamp) / (1000 * 60 * 60)
            
            if age_hours < 24:
                recency_score = 1.0
            elif age_hours < 48:
                recency_score = 0.9
            elif age_hours < 72:
                recency_score = 0.8
            elif age_hours < 168:  # 1 week
                recency_score = 0.6
            elif age_hours < 720:  # 30 days
                recency_score = 0.4
            else:
                recency_score = 0.2
        else:
            recency_score = 0.1  # Very low for jobs without date
        
        score += recency_score * weights['recency']
        
        # Location match score
        location_score = self.calculate_location_match_score(
            job.get('location', ''),
            user_preferences.get('location', '')
        )
        score += location_score * weights['location']
        
        # Title match score
        title_score = self.calculate_job_title_match_score(
            job.get('title', ''),
            user_preferences.get('jobTitle', '')
        )
        score += title_score * weights['title_match']
        
        # URL validity score
        job_url = job.get('link', '') or job.get('url', '')
        url_score = 1.0 if (job_url and job_url.startswith('http')) else 0.3
        score += url_score * weights['has_url']

        # Source bonus: prioritize TimesJobs slightly
        via = (job.get('via') or '').lower()
        source_bonus = 1.0
        if 'timesjobs' in via:
            source_bonus = 1.12  # ~12% boost

        score *= source_bonus
        # Clamp score to max 1.0 for consistency
        return min(score, 1.0)
    
    async def fetch_from_source(self, session: aiohttp.ClientSession, source: str, 
                                keyword: str, location: str) -> List[Dict[str, Any]]:
        """
        Fetch jobs from a single source
        """
        base_url = 'http://localhost:5000'  # Adjust if needed
        
        url_map = {
            'internshala': f'{base_url}/api/internshala?keyword={keyword}&location={location}&page=1',
            'linkedin': f'{base_url}/api/linkedin?keyword={keyword}&location={location}&limit=25',
            'remoteok': f'{base_url}/api/remoteok?keywords={keyword}',
            'aasaanjobs': f'{base_url}/api/aasaanjobs?keyword={keyword}',
            'dare2compete': f'{base_url}/api/dare2compete',
            'freshersworld': f'{base_url}/api/freshersworld?keyword={keyword}&location={location}',
            'jobguru': f'{base_url}/api/jobguru?keyword={keyword}',
            'timesjobs': f'{base_url}/api/timesjobs?keyword={keyword}&location={location}',
            'myamcat': f'{base_url}/api/myamcat?keyword={keyword}&location={location}'
        }
        
        if source not in url_map:
            return []
        
        try:
            self.progress[source] = 'fetching'
            
            async with session.get(url_map[source], timeout=aiohttp.ClientTimeout(total=120)) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Extract jobs from response
                    jobs = []
                    if isinstance(data, dict):
                        if 'data' in data:
                            if isinstance(data['data'], dict) and 'jobs' in data['data']:
                                jobs = data['data']['jobs']
                            elif isinstance(data['data'], list):
                                jobs = data['data']
                        elif 'jobs' in data:
                            jobs = data['jobs']
                    elif isinstance(data, list):
                        jobs = data
                    
                    # Add source to each job
                    for job in jobs:
                        job['via'] = source.title()
                    
                    self.progress[source] = 'completed'
                    print(f"✅ {source}: {len(jobs)} jobs")
                    return jobs
                else:
                    self.progress[source] = 'failed'
                    print(f"❌ {source}: HTTP {response.status}")
                    return []
        except asyncio.TimeoutError:
            self.progress[source] = 'timeout'
            print(f"⏱️ {source}: Timeout")
            return []
        except Exception as e:
            self.progress[source] = 'error'
            print(f"❌ {source}: {str(e)}")
            return []
    
    async def fetch_all_jobs(self, keyword: str, location: str) -> List[Dict[str, Any]]:
        """
        Fetch jobs from all sources concurrently
        """
        print(f"🔍 Fetching jobs for: {keyword} in {location}")
        
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.fetch_from_source(session, source, keyword, location)
                for source in self.sources
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            all_jobs = []
            for result in results:
                if isinstance(result, list):
                    all_jobs.extend(result)
            
            print(f"📦 Total jobs fetched: {len(all_jobs)}")
            return all_jobs
    
    def filter_and_select_top_jobs(self, jobs: List[Dict[str, Any]], 
                                   user_preferences: Dict[str, str], 
                                   target_count: int = 20) -> List[Dict[str, Any]]:
        """
        Filter and select top N jobs based on scoring
        """
        print(f"🔬 Analyzing {len(jobs)} jobs...")
        
        # Filter out invalid jobs
        valid_jobs = []
        for job in jobs:
            # Must have title and company
            if not job.get('title') or not job.get('company'):
                continue
            if job.get('title') == 'N/A' or job.get('company') == 'N/A':
                continue
            
            valid_jobs.append(job)
        
        print(f"✅ Valid jobs: {len(valid_jobs)}")
        
        # Calculate score for each job
        for job in valid_jobs:
            job['_score'] = self.calculate_job_score(job, user_preferences)
        
        # Sort by score (highest first)
        sorted_jobs = sorted(valid_jobs, key=lambda x: x['_score'], reverse=True)
        
        # Select top jobs with diversity
        selected_jobs: List[Dict[str, Any]] = []
        source_counts: Dict[str, int] = {}
        min_per_source = 2  # Default diversity minimum per source

        # Special priority: pick extra from TimesJobs first (if available)
        boosted_source_names = {'TimesJobs', 'Timesjobs'}
        max_timesjobs = 5  # Try to include up to 5 from TimesJobs if quality allows
        for job in sorted_jobs:
            if len(selected_jobs) >= target_count:
                break
            source = job.get('via', 'Unknown')
            if source in boosted_source_names:
                count = source_counts.get(source, 0)
                if count < max_timesjobs:
                    selected_jobs.append(job)
                    source_counts[source] = count + 1

        # First pass: Ensure diversity (at least min_per_source from each source)
        for job in sorted_jobs:
            if len(selected_jobs) >= target_count:
                break
            source = job.get('via', 'Unknown')
            count = source_counts.get(source, 0)
            if count < min_per_source and job not in selected_jobs:
                selected_jobs.append(job)
                source_counts[source] = count + 1
                if len(selected_jobs) >= target_count:
                    break

        # Second pass: Fill remaining slots with highest scored jobs
        if len(selected_jobs) < target_count:
            for job in sorted_jobs:
                if job not in selected_jobs:
                    selected_jobs.append(job)
                    if len(selected_jobs) >= target_count:
                        break
        
        # Remove score field before returning
        for job in selected_jobs:
            if '_score' in job:
                del job['_score']
        
        print(f"🎯 Selected top {len(selected_jobs)} jobs")
        print(f"📊 Source distribution: {source_counts}")

        # Final sort: by recency (most recent first) using parsed timestamp
        def _ts(j: Dict[str, Any]) -> int:
            ts = self.parse_date_to_timestamp(j.get('posted_on') or j.get('postedAt') or '')
            return ts

        selected_jobs.sort(key=lambda j: _ts(j), reverse=True)
        return selected_jobs
    
    def get_progress_percentage(self) -> float:
        """
        Calculate overall progress percentage
        """
        if not self.progress:
            return 0.0
        
        completed = sum(1 for status in self.progress.values() 
                       if status in ['completed', 'failed', 'timeout', 'error'])
        return (completed / len(self.sources)) * 100
    
    def get_current_source(self) -> Optional[str]:
        """
        Get currently fetching source
        """
        for source, status in self.progress.items():
            if status == 'fetching':
                return source.title()
        return None


async def aggregate_jobs(keyword: str, location: str, user_preferences: Dict[str, str]) -> Dict[str, Any]:
    """
    Main function to aggregate and filter jobs
    """
    aggregator = JobAggregator()
    
    # Fetch all jobs
    all_jobs = await aggregator.fetch_all_jobs(keyword, location)
    
    if not all_jobs:
        return {
            'status': 'failed',
            'message': 'No jobs found from any source',
            'data': {'jobs': []},
            'progress': 100
        }
    
    # Filter and select top 20
    top_jobs = aggregator.filter_and_select_top_jobs(all_jobs, user_preferences, target_count=20)
    
    return {
        'status': 'success',
        'message': f'Found {len(top_jobs)} best matching jobs from {len(all_jobs)} total jobs',
        'data': {'jobs': top_jobs},
        'progress': 100,
        'stats': {
            'total_fetched': len(all_jobs),
            'selected': len(top_jobs),
            'sources': aggregator.progress
        }
    }
