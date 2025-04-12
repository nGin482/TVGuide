from datetime import datetime
from flask import Blueprint, request
from flask_cors import CORS
from sqlalchemy.orm import Session

from database import engine
from database.models import Guide
from data_validation.validation import Validation

guide_blueprint = Blueprint("guide_blueprint", __name__)

@guide_blueprint.route("")
def guide():
    session = Session(engine)
    
    if request.args.get(""):
        dates = request.args.get("date").split("/")
        date = datetime(year=int(dates[2]), month=int(dates[1]), day=int(dates[0]))
    else:
        date = Validation.get_current_date()
    
    guide = Guide(date, session)
    guide.get_shows()
    
    return guide.to_dict()
