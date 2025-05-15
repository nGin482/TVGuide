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
    
    if request.args.get("date"):
        date = datetime.strptime(request.args.get("date"), "%d/%m/%Y")
    else:
        date = Validation.get_current_date()
    
    guide = Guide.get_date(date, session)
    if not guide:
        return { "message": "There is no guide for this date" }, 404
    
    guide.get_shows()
    
    return guide.to_dict()
