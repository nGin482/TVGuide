from dotenv import load_dotenv

load_dotenv('.env')

from database import engine
from services.TVGuideScheduler import TVGuideScheduler


tvguide_scheduler = TVGuideScheduler(engine)
