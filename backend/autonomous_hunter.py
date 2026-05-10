import asyncio
import os
import json
from datetime import datetime
from sqlalchemy.orm import Session
from backend.database import SessionLocal, engine
from backend import models
from backend.job_intelligence import JobIntelligence
from backend.commander import CareerCommander
from backend.rag_pipeline import RAGPipeline

class AutonomousHunter:
    """
    GOATed Background Agent: Scrapes, Filters, and Conducts War Rooms autonomously.
    """
    def __init__(self):
        self.pipeline = RAGPipeline()
        self.job_intel = JobIntelligence(pipeline=self.pipeline)
        self.commander = CareerCommander(rag_pipeline=self.pipeline)
        self.target_query = "Senior AI Machine Learning Engineer" # Target profile

    async def run_hunt_cycle(self):
        print(f"🕵️ Hunter Cycle Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        db = SessionLocal()
        
        try:
            # 1. Scrape & Index New Jobs
            print("Hunter [Scraper]: Scouting for new opportunities...")
            new_jobs = await self.job_intel.gather_intelligence(self.target_query)
            
            # 2. Query Vector DB for high-match jobs
            print("Hunter [RAG]: Analyzing relevance of found leads...")
            matches = self.pipeline.query_jobs(self.target_query, k=10)
            
            for match in matches:
                score = match['relevance_score']
                metadata = match['metadata']
                url = metadata.get('url')
                
                # Check if elite match (> 0.85) and not already processed
                if score >= 0.85:
                    existing = db.query(models.JobLead).filter(models.JobLead.url == url).first()
                    
                    if not existing or (existing and not existing.is_elite):
                        print(f"🔥 ELITE MATCH DETECTED ({score*100:.0f}%): {metadata['title']} at {metadata['company']}")
                        
                        # 3. Trigger Autonomous War Room
                        print("Hunter [Commander]: Activating autonomous War Room protocol...")
                        battle_card = await self.commander.run_war_room(
                            metadata['title'], 
                            metadata['company'], 
                            match['content']
                        )
                        
                        # 4. Persist Elite Lead
                        if not existing:
                            new_lead = models.JobLead(
                                title=metadata['title'],
                                company=metadata['company'],
                                url=url,
                                status="battle_ready",
                                is_elite=True,
                                battle_card=battle_card,
                                metadata_info=metadata
                            )
                            db.add(new_lead)
                        else:
                            existing.is_elite = True
                            existing.battle_card = battle_card
                            existing.status = "battle_ready"
                        
                        db.commit()
                        print(f"✅ Battle Card Persisted for {metadata['company']}.")
                        
        except Exception as e:
            print(f"❌ Hunter Cycle Error: {e}")
        finally:
            db.close()
            print("🕵️ Hunter Cycle Complete. Sleeping for 4 hours...")

    async def start_infinite_hunt(self):
        while True:
            await self.run_hunt_cycle()
            await asyncio.sleep(4 * 3600) # Run every 4 hours

if __name__ == "__main__":
    hunter = AutonomousHunter()
    asyncio.run(hunter.start_infinite_hunt())
