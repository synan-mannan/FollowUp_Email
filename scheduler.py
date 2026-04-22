from apscheduler.schedulers.background import BackgroundScheduler
import time
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
import atexit
from models import Lead
from core.followup_engine import execute_followup
from config import settings
import logging
import sqlalchemy as sa

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

engine = create_engine(f"sqlite:///{settings.db_path}")
SessionLocal = sa.orm.sessionmaker(bind=engine)

def check_active_leads():
    """Job: check all active leads and execute followups if needed."""
    db = SessionLocal()
    try:
        # Active: contacted, not closed, followup_count <5
        active_leads = db.query(Lead.id).filter(
            Lead.status != "closed",
            Lead.followup_count < 5
        ).all()
        
        processed = 0
        for lead_record in active_leads:
            lead_id = lead_record[0]
            try:
                execute_followup(lead_id)
                processed += 1
            except Exception as e:
                logger.error(f"Error processing lead {lead_id}: {e}")
        
        logger.info(f"Processed {processed}/{len(active_leads)} active leads")
    finally:
        db.close()

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=check_active_leads,
        trigger="interval",
        minutes=30,  # Check every 30 min
        id="lead_followup_check",
        replace_existing=True
    )
    scheduler.start()
    logger.info("Scheduler started. Checking active leads every 30 minutes.")
    
    # Keep running
    try:
        while True:
            time.sleep(60)  # Sleep 1 min
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()

if __name__ == "__main__":
    start_scheduler()

