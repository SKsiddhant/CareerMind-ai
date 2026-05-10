import os
import re
import asyncio
from langchain_community.tools import DuckDuckGoSearchRun

class HiringIntelligence:
    """
    GOATed OSINT Agent: Identifies real Hiring Managers and predicts contact info.
    No more mock data.
    """
    def __init__(self):
        self.search = DuckDuckGoSearchRun()
        self.email_patterns = [
            "{first}.{last}@{domain}",
            "{first}@{domain}",
            "{f}{last}@{domain}",
            "{first}{last}@{domain}"
        ]

    def predict_email(self, name, domain):
        if not name or name == "Unknown Manager" or not domain:
            return []
        
        parts = name.lower().split()
        if len(parts) < 2:
            return [f"{parts[0]}@{domain}"]
        
        first = parts[0]
        last = parts[-1]
        f = first[0]
        
        emails = []
        for pattern in self.email_patterns:
            emails.append(pattern.format(first=first, last=last, f=f, domain=domain))
        
        return list(set(emails))

    def get_domain(self, company_name):
        # Improved domain mapping
        domains = {
            "OpenAI": "openai.com",
            "Google": "google.com",
            "Meta": "meta.com",
            "Anthropic": "anthropic.com",
            "NVIDIA": "nvidia.com",
            "Microsoft": "microsoft.com",
            "Apple": "apple.com",
            "Amazon": "amazon.com",
            "Netflix": "netflix.com",
            "Mistral AI": "mistral.ai",
            "Cohere": "cohere.com"
        }
        if company_name in domains:
            return domains[company_name]
        return f"{company_name.lower().replace(' ', '').replace('ai', '')}.com"

    async def discover_manager(self, company, job_title):
        """
        Uses live search to find real names on LinkedIn.
        """
        print(f"🔍 Running OSINT for {job_title} at {company}...")
        
        query = f"site:linkedin.com/in/ \"Hiring Manager\" OR \"Technical Lead\" OR \"Engineering Manager\" {company} {job_title}"
        
        try:
            # Run search in a thread to keep it async-friendly
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(None, self.search.run, query)
            
            # Simple regex to extract names from common LinkedIn title formats
            # Format: "Name - Title - Company | LinkedIn"
            name_pattern = r"([A-Z][a-z]+ [A-Z][a-z]+)"
            potential_names = re.findall(name_pattern, results)
            
            # Filter out common false positives
            blacklist = ["LinkedIn", "Google", "Hiring", "Manager", "Technical", "Lead", "Engineering", "Jobs", "About"]
            found_names = [n for n in potential_names if not any(b in n for b in blacklist)]
            
            manager_name = found_names[0] if found_names else "Unknown Manager"
            domain = self.get_domain(company)
            emails = self.predict_email(manager_name, domain)
            
            return {
                "name": manager_name,
                "emails": emails,
                "company": company,
                "domain": domain,
                "source": "LinkedIn OSINT"
            }
        except Exception as e:
            print(f"OSINT Discovery failed: {e}")
            return {
                "name": "Unknown Manager",
                "emails": [],
                "company": company,
                "domain": "unknown.com"
            }

if __name__ == "__main__":
    # Test Run
    hi = HiringIntelligence()
    import asyncio
    async def test():
        info = await hi.discover_manager("OpenAI", "AI Engineer")
        print(f"Found: {info['name']}")
        print(f"Predicted Emails: {info['emails']}")
    
    asyncio.run(test())
