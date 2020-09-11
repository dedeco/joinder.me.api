from flask import Blueprint

lover_blueprint = Blueprint('lover', __name__)


from . import resources

