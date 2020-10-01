from app.main import bp
from flask import render_template, request, redirect, url_for, make_response
from flask_login import current_user, login_required
from app import Config, mail, db
from app.models import User


@bp.route('/', methods=['GET','POST'])
@login_required
def index():
    title = 'КАНБАЛА'
    return render_template('main/index.html', title=title, user=current_user)