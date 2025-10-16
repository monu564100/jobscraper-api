"""
Test LinkedIn Scraper
Run this to test if LinkedIn scraping is working properly
"""

import sys
sys.path.append('c:\\Users\\monu5\\OneDrive\\Desktop\\APP\\jobscraper-api')

from app.providers.linkedin_scraper import LinkedInScraper

def test_linkedin_scraper():
    print("🔗 Testing LinkedIn Scraper")
    print("=" * 60)
    
    # Create scraper (headless=False to see what's happening)
    print("\n1️⃣ Initializing scraper...")
    scraper = LinkedInScraper(headless=True)  # Set False to see browser
    
    try:
        # Test search
        keyword = 'python developer'
        location = 'bangalore'
        
        print(f"\n2️⃣ Searching for: '{keyword}' in '{location}'")
        print("   This may take 10-15 seconds...")
        
        jobs = scraper.scrape_jobs(keyword, location)
        
        print(f"\n3️⃣ Results:")
        print(f"   ✅ Found {len(jobs)} jobs from LinkedIn")
        
        if jobs:
            print(f"\n4️⃣ First 5 jobs:")
            for i, job in enumerate(jobs[:5], 1):
                print(f"\n   {i}. {job['title']}")
                print(f"      Company: {job['company']}")
                print(f"      Location: {job['location']}")
                print(f"      Posted: {job['posted_on']}")
                print(f"      URL: {job['link']}")
        else:
            print("\n   ⚠️  No jobs found. This could mean:")
            print("      - LinkedIn is blocking the scraper")
            print("      - No jobs match the criteria")
            print("      - Network/connection issues")
        
        print(f"\n{'=' * 60}")
        print("✅ Test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during testing:")
        print(f"   {str(e)}")
        print("\nTroubleshooting:")
        print("  1. Check if Chrome/Chromium is installed")
        print("  2. Run: pip install selenium webdriver-manager beautifulsoup4")
        print("  3. Check your internet connection")
        
    finally:
        print("\n5️⃣ Cleaning up...")
        scraper.close()
        print("   Browser closed")

if __name__ == '__main__':
    test_linkedin_scraper()
