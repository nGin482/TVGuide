from datetime import datetime
from flask import Blueprint, request
from flask_cors import CORS
from sqlalchemy.orm import Session

from database import engine
from database.models import Guide
import utils

guide_blueprint = Blueprint("guide_blueprint", __name__)

@guide_blueprint.route("")
def guide():
    session = Session(engine)
    
    if request.args.get("date"):
        date = datetime.strptime(request.args.get("date"), "%d/%m/%Y")
    else:
        date = utils.get_current_date()
    
    guide = Guide.get_date(date, session)
    if not guide:
        session.close()
        return { "message": "There is no guide for this date" }, 404
    
    guide.get_shows()

    session.close()
    return guide.to_dict()
