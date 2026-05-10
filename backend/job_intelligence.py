import asyncio
import json
import os
from scrapers.job_scraper import JobScraper
from backend.rag_pipeline import RAGPipeline
from backend.hiring_intelligence import HiringIntelligence
from langchain_community.tools import DuckDuckGoSearchRun

class JobIntelligence:
    """
    Orchestrates job discovery across multiple companies and indexes them.
    This is the core of our 'Job Intelligence' Agent.
    """
    def __init__(self, scraper=None, pipeline=None, hiring_agent=None):
        self.scraper = scraper or JobScraper()
        self.pipeline = pipeline or RAGPipeline()
        self.hiring_agent = hiring_agent or HiringIntelligence()
        self.search_tool = DuckDuckGoSearchRun()
        self.target_sources = {
            "OpenAI": "https://openai.com/careers/search",
            "Google AI": "https://www.google.com/about/careers/applications/jobs/results/?q=AI",
            "LinkedIn": "https://www.linkedin.com/jobs/search/?keywords=",
            "Unstop": "https://unstop.com/jobs?keywords=",
            "Naukri": "https://www.naukri.com/{query}-jobs",
            "Wellfound": "https://wellfound.com/role/l/{query}",
            "Otta": "https://otta.com/jobs?q={query}",
            "Indeed": "https://www.indeed.com/jobs?q={query}",
            "Glassdoor": "https://www.glassdoor.com/Job/jobs.htm?sc.keyword={query}",
            "ZipRecruiter": "https://www.ziprecruiter.com/Jobs/Search?search={query}",
            "Anthropic": "https://www.anthropic.com/careers",
            "Mistral AI": "https://mistral.ai/careers/",
            "Meta": "https://www.metacareers.com/jobs/?q={query}",
            "Apple": "https://www.apple.com/jobs/us/search.html?search={query}",
            "NVIDIA": "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite?q={query}",
            "Microsoft": "https://jobs.microsoft.com/us/en/search-results?keywords={query}",
            "Amazon": "https://www.amazon.jobs/en/search?base_query={query}",
            "Y Combinator": "https://www.ycombinator.com/jobs/role/{query}",
        }

    async def gather_intelligence(self, search_query):
        print(f"\n🐐 GOATed Intelligence Mode Activated for: '{search_query}'")
        
        # Step 1: Query Expansion (Searching for Synonyms)
        expanded_queries = [search_query]
        if "engineer" in search_query.lower():
            base = search_query.lower().replace("engineer", "").strip()
            expanded_queries.extend([f"{base} developer", f"fullstack {base}", f"backend {base}"])
        
        print(f"Expanding search to: {expanded_queries}")
        
        all_jobs = []
        
        # Step 2: Parallel Batch Execution (Super Fast - sf)
        tasks = []
        
        # Parallel Dynamic Discovery
        for query in expanded_queries:
            tasks.append(self._discover_and_scrape_dynamic(query))
        
        # Parallel Hardcoded Sources
        for name, base_url in self.target_sources.items():
            for query in expanded_queries:
                tasks.append(self._scrape_source(name, base_url, query))
        
        print(f"Launching {len(tasks)} parallel intelligence tasks...")
        results = await asyncio.gather(*tasks)
        
        # Flatten results
        for job_list in results:
            if job_list:
                all_jobs.extend(job_list)
        
        # Step 3: Deduplicate and Index
        unique_jobs = {job['url']: job for job in all_jobs if job}.values()
        print(f"\n✅ GOATed Intelligence gathered {len(unique_jobs)} unique leads.")
        
        # Save and Index
        with open("data/jobs.json", "w") as f:
            json.dump(list(unique_jobs), f, indent=4)
            
        self.pipeline.add_jobs_to_index()
        return list(unique_jobs)

    async def _discover_and_scrape_dynamic(self, query):
        discovered_jobs = []
        try:
            search_results = self.search_tool.run(f"{query} jobs San Francisco career pages")
            import re
            discovered_urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', search_results)
            
            for url in discovered_urls[:3]: # Precision over quantity
                if not any(domain in url for domain in ["google.com", "bing.com", "duckduckgo.com"]):
                    links = await self.scraper.discover_job_links(url, search_keyword=query)
                    for link in links[:3]:
                        job = await self.scraper.scrape_url(link)
                        if job: 
                            # Intelligence Phase - Find Manager
                            manager_info = await self.hiring_agent.discover_manager(job['company'], job['title'])
                            job['hiring_manager'] = manager_info['name']
                            job['predicted_emails'] = manager_info['emails']
                            discovered_jobs.append(job)
        except Exception as e:
            print(f"Dynamic discovery failed for {query}: {e}")
        return discovered_jobs

    async def _scrape_source(self, name, base_url, query):
        source_jobs = []
        try:
            # Smart URL Formatting
            if "{query}" in base_url:
                url = base_url.format(query=query.replace(" ", "%20"))
            elif name == "Naukri":
                url = base_url.format(query=query.replace(" ", "-"))
            elif name == "LinkedIn" or name == "Unstop":
                url = base_url + query.replace(" ", "%20")
            else:
                url = base_url
            
            links = await self.scraper.discover_job_links(url, search_keyword=query)
            for link in links[:3]:
                job = await self.scraper.scrape_url(link)
                if job: 
                    # Intelligence Phase - Find Manager
                    manager_info = await self.hiring_agent.discover_manager(job['company'], job['title'])
                    job['hiring_manager'] = manager_info['name']
                    job['predicted_emails'] = manager_info['emails']
                    source_jobs.append(job)
        except Exception as e:
            print(f"Source {name} failed for {query}: {e}")
        return source_jobs

async def main():
    intelligence = JobIntelligence()
    # Let's search for 'engineer' as a broad test
    found_jobs = await intelligence.gather_intelligence("engineer")
    
    print("\n--- Intelligence Output ---")
    for i, job in enumerate(found_jobs):
        print(f"{i+1}. {job['title']} ({job['url']})")

if __name__ == "__main__":
    asyncio.run(main())
