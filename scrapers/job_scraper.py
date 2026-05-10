import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

class JobScraper:
    """
    Advanced Job Scraper using Playwright to handle dynamic content (JS).
    Supports extraction from common ATS platforms and job boards.
    """
    def __init__(self):
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"

    async def scrape_url(self, url):
        print(f"Scraping with Playwright: {url}")
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            # More realistic browser context
            context = await browser.new_context(
                user_agent=self.user_agent,
                viewport={'width': 1920, 'height': 1080},
                device_scale_factor=1,
                has_touch=False,
                is_mobile=False
            )
            page = await context.new_page()

            try:
                # Set extra headers to look more like a real user
                await page.set_extra_http_headers({
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                    "Referer": "https://www.google.com/"
                })
                
                # Navigate and wait for content
                await page.goto(url, wait_until="networkidle", timeout=60000)
                
                # Handle common cookie banners or overlays (wait a bit)
                await asyncio.sleep(2)
                
                # Auto-scroll to ensure all content is loaded
                await self._auto_scroll(page)

                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')

                # Priority 1: Extract from JSON-LD (Structured Data)
                job_data = await self._extract_from_json_ld(soup)
                
                # Priority 2: Fallback to Selectors if JSON-LD is missing or incomplete
                if not job_data:
                    job_data = {
                        "title": await self._extract_title(page, soup),
                        "company": await self._extract_company(page, soup),
                        "description": await self._extract_description(page, soup),
                    }
                
                # Extract Skills/Tech Stack (New Advanced Feature)
                job_data["skills"] = self._extract_skills(job_data.get("description", ""))
                
                # Ensure URL and metadata are present
                job_data.update({
                    "url": url,
                    "scraped_at": datetime.now().isoformat(),
                    "hiring_manager": job_data.get("hiring_manager") or await self._extract_hiring_info(page, soup)
                })

                # Sanity Check: Discard junk data
                invalid_indicators = ["page not found", "couldn't find", "can't find", "sorry", "not active", "404", "we can’t find"]
                title_low = job_data.get("title", "").lower()
                desc_low = job_data.get("description", "").lower()
                
                is_invalid = any(ind in title_low for ind in invalid_indicators) or \
                             any(ind in desc_low[:500] for ind in invalid_indicators) or \
                             len(job_data.get("description", "")) < 200 or \
                             (job_data.get("company") == "Unknown" and "jobs" in title_low)
                
                if is_invalid:
                    print(f"Discarding invalid job data for {url} (Title: {job_data.get('title')})")
                    await browser.close()
                    return None

                await browser.close()
                return job_data

            except Exception as e:
                print(f"Error scraping {url}: {e}")
                await browser.close()
                return None

    async def _auto_scroll(self, page):
        """Scrolls the page to trigger lazy loading."""
        await page.evaluate("""
            async () => {
                await new Promise((resolve) => {
                    let totalHeight = 0;
                    let distance = 100;
                    let timer = setInterval(() => {
                        let scrollHeight = document.body.scrollHeight;
                        window.scrollBy(0, distance);
                        totalHeight += distance;
                        if(totalHeight >= scrollHeight || totalHeight > 5000){
                            clearInterval(timer);
                            resolve();
                        }
                    }, 100);
                });
            }
        """)

    async def _extract_from_json_ld(self, soup):
        """Extracts structured job data from JSON-LD tags."""
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                # JSON-LD can be a single object or a list
                if isinstance(data, list):
                    data = next((item for item in data if item.get("@type") == "JobPosting"), None)
                
                if data and (data.get("@type") == "JobPosting" or "JobPosting" in str(data.get("@type"))):
                    return {
                        "title": data.get("title"),
                        "company": data.get("hiringOrganization", {}).get("name") if isinstance(data.get("hiringOrganization"), dict) else data.get("hiringOrganization"),
                        "description": data.get("description"),
                        "location": data.get("jobLocation", {}).get("address", {}).get("addressLocality") if isinstance(data.get("jobLocation"), dict) else None,
                        "date_posted": data.get("datePosted")
                    }
            except:
                continue
        return None

    def _extract_skills(self, description):
        """Extracts key skills/tech from description using a prioritized keyword list."""
        if not description: return []
        
        tech_keywords = [
            "Python", "JavaScript", "TypeScript", "React", "Angular", "Vue", "Node.js", 
            "Express", "Django", "Flask", "FastAPI", "Go", "Rust", "Java", "C++", 
            "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", "SQL", 
            "PostgreSQL", "MongoDB", "Redis", "Kafka", "PyTorch", "TensorFlow", 
            "Scikit-Learn", "LangChain", "LLM", "RAG", "Generative AI", "LoRA", 
            "Fine-tuning", "Mistral", "Llama", "OpenAI", "NLP", "Computer Vision"
        ]
        
        found = []
        desc_lower = description.lower()
        for tech in tech_keywords:
            # Match whole words to avoid sub-string issues (e.g., 'Go' in 'Google')
            import re
            pattern = r'\b' + re.escape(tech.lower()) + r'\b'
            if re.search(pattern, desc_lower):
                found.append(tech)
        return found

    async def _extract_company(self, page, soup):
        selectors = [
            ".topcard__org-name-link", 
            ".job-details-jobs-unified-top-card__company-name", 
            "div.company-name",
            "[class*='companyName']",
            "[class*='employer']",
            "a[data-at='company-name']"
        ]
        for s in selectors:
            el = soup.select_one(s)
            if el: return el.get_text(strip=True)
        return "Unknown"

    async def _extract_hiring_info(self, page, soup):
        """Attempts to find recruiter/hiring manager name from LinkedIn or other boards"""
        selectors = [
            ".app-aware-link.recruiter-name", # LinkedIn
            ".hiring-manager-name",
            ".recruiter-profile-card__name"
        ]
        for s in selectors:
            el = soup.select_one(s)
            if el: return el.get_text(strip=True)
        return None

    async def _extract_title(self, page, soup):
        # Try specific selectors for Greenhouse/LinkedIn/Indeed
        selectors = [
            "h1.app-title", # Greenhouse
            "h1", 
            ".job-title", 
            "h2"
        ]
        for selector in selectors:
            element = soup.select_one(selector)
            if element and len(element.get_text(strip=True)) > 3:
                return element.get_text(strip=True)
        
        # Try finding the first large header
        for i in range(1, 4):
            header = soup.find(f'h{i}')
            if header:
                return header.get_text(strip=True)
        return "N/A"

    async def _extract_description(self, page, soup):
        # Try common description containers
        containers = [
            "div#content", # Greenhouse
            "div.description",
            "div.job-description",
            "section.job-description",
            "div#jobDescriptionText", # Indeed
            "div.show-more-less-html__markup", # LinkedIn
            "main",
            "article",
            "[class*='description']",
            "[id*='description']"
        ]
        
        for container in containers:
            element = soup.select_one(container)
            if element:
                # Remove script and style tags
                for script_or_style in element(["script", "style"]):
                    script_or_style.decompose()
                text = element.get_text(separator='\n', strip=True)
                if len(text) > 100: # Ensure it's not just a small snippet
                    return text
        
        # Final Fallback: Grab the largest text block in the body
        return soup.body.get_text(separator='\n', strip=True)

    async def discover_job_links(self, career_page_url, search_keyword=None):
        """
        Navigates to a career page and finds individual job posting links.
        """
        print(f"Discovering jobs at: {career_page_url}")
        async with async_playwright() as p:
            # Using a real browser look for job boards
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=self.user_agent,
                viewport={'width': 1920, 'height': 1080}
            )
            page = await context.new_page()

            try:
                await page.goto(career_page_url, wait_until="domcontentloaded", timeout=60000)
                # Wait longer for job boards as they have complex JS
                await asyncio.sleep(5) 
                
                # Scroll down to trigger lazy loading if any
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight/2)")
                await asyncio.sleep(2)

                # Get all links
                links = await page.eval_on_selector_all("a", "elements => elements.map(e => e.href)")
                
                job_links = []
                # Expanded patterns for aggregator sites and ATS
                patterns = [
                    "/jobs/", "/posting/", "/view/", "gh_jid=", 
                    "job-detail", "/opportunity/", # Unstop
                    "-jobs-", "job-listings-", # Naukri
                    "/careers/", "apply/", "jobs.lever.co",
                    "boards.greenhouse.io", "myworkdayjobs.com",
                    "smartrecruiters.com", "breezy.hr", "workable.com"
                ]
                
                # Exclude common non-job links
                exclude = ["/login", "/signup", "/register", "/blog", "/about", "/terms", "/privacy", "/cookies"]

                for link in set(links):
                    if any(pattern in link for pattern in patterns):
                        if not any(ex in link for ex in exclude):
                            if search_keyword:
                                # Loose keyword matching for discovery
                                if search_keyword.lower() in link.lower() or "job" in link.lower() or "career" in link.lower():
                                    job_links.append(link)
                            else:
                                job_links.append(link)

                # Remove duplicates and limit
                unique_links = list(set(job_links))
                print(f"Found {len(unique_links)} potential job links.")
                
                await browser.close()
                return unique_links[:15] # Return top 15

            except Exception as e:
                print(f"Error discovering links at {career_page_url}: {e}")
                await browser.close()
                return []

    def save_to_json(self, job_data, filename="data/jobs.json"):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        jobs = []
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                try:
                    jobs = json.load(f)
                except json.JSONDecodeError:
                    jobs = []
        
        # Check if job already exists (simple URL check)
        if not any(j['url'] == job_data['url'] for j in jobs):
            jobs.append(job_data)
            with open(filename, 'w') as f:
                json.dump(jobs, f, indent=4)
            print(f"Saved job to {filename}")
        else:
            print("Job already exists in records.")

async def main():
    scraper = JobScraper()
    test_urls = [
        "https://boards.greenhouse.io/openai/jobs/4320490005", # Greenhouse
        "https://jobs.lever.co/lever/506f0e9b-008f-4a0b-9c7b-9c1c6f4a7f0e", # Lever (Example)
        "https://www.linkedin.com/jobs/view/3784561234", # LinkedIn (Example)
        "https://www.indeed.com/viewjob?jk=1234567890", # Indeed (Example)
    ]
    
    for url in test_urls:
        print(f"\n--- Testing URL: {url} ---")
        data = await scraper.scrape_url(url)
        if data:
            if "Page not found" in data.get("title", "") or "not active" in data.get("description", "").lower():
                print(f"Warning: Job at {url} seems to be inactive.")
            else:
                scraper.save_to_json(data)
                print(f"Scrape successful for: {data.get('title')} at {data.get('company')}")
        else:
            print(f"Scrape failed for {url}")

if __name__ == "__main__":
    # To run this script: python scrapers/job_scraper.py
    # Note: Requires playwright install
    asyncio.run(main())
