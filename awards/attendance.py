from flask import Blueprint, render_template

bp = Blueprint('attendance', __name__)


@bp.route('/attendance')
def index():
    pass
