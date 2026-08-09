from discord.errors import HTTPException
from sqlalchemy.orm import Session
import os

from database import engine
from database.models.GuideModel import Guide
from exceptions.tvguide_errors import GuideNotCreatedError
from data_validation.validation import Validation




async def create_guide():
    from config import tvguide_scheduler
    from services.hermes.hermes import hermes

    date = Validation.get_current_date()
    session = Session(engine, expire_on_commit=False)
    
    guide = Guide(date, session)
    
    await hermes.wait_until_ready()
    ngin_id = int(os.getenv('NGIN'))
    ngin = await hermes.fetch_user(ngin_id)

    try:
        guide.create_new_guide(tvguide_scheduler)
        guide_message = guide.compose_message()
        reminder_message = guide.compose_reminder_message()
        events_message = guide.compose_events_message()

        await hermes.send_guide_message(
            guide_message,
            reminder_message,
            events_message
        )
    except HTTPException as error:
        await ngin.send(f"There was a problem sending the TVGuide messages. Error: {str(error)}")
    except GuideNotCreatedError as error:
        await ngin.send(f"The TVGuide could not be created properly. Error: {str(error)}")
    except (AttributeError, TypeError, ValueError) as error:
        await ngin.send(f"There was a problem sending the TVGuide. Error: {str(error)}")
    finally:
        session.close()
