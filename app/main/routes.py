from app import db
from app.main import bp
from flask import render_template, redirect, url_for, request
from flask_login import current_user, login_required
from app.models import Regulation, RegulationVersion
import json


@bp.route('/', methods=['GET','POST'])
@login_required
def index():
    title = 'КАНБАЛА'
    users_regulations: Regulation = Regulation.query.filter(Regulation.creator==current_user.id).all()
    return render_template('main/index.html',
                           title=title,
                           user=current_user,
                           users_regulations=users_regulations)


@bp.route('/create_regulation', methods=['GET', 'POST'])
@login_required
def regulation_create():
    regulation = Regulation()
    regulation.creator = current_user.id
    db.session.add(regulation)
    db.session.commit()
    regulation.short_name = f'Новый регламент {regulation.id}'
    regulation_version = RegulationVersion()
    regulation_version.version_number = 1
    regulation_version.status = 'Черновик'
    regulation_version.regulation_id = regulation.id
    db.session.add(regulation_version)
    db.session.commit()
    return redirect(url_for('main.regulation_show', regulation_version_id=regulation_version.id))


@bp.route('/show_regulation_<regulation_version_id>', methods=['GET', 'POST'])
@login_required
def regulation_show(regulation_version_id):
    regulation_version: RegulationVersion = RegulationVersion.query.get(regulation_version_id)
    data = regulation_version.data
    return render_template('main/regulation_editor.html',
                           title='Редактор регламента',
                           regulation_version=regulation_version,
                           data=data)


@bp.route('/save_regulation_<regulation_version_id>', methods=['POST'])
@login_required
def regulation_save(regulation_version_id):
    data = json.loads(json.dumps(request.form))
    regulation_version: RegulationVersion = RegulationVersion.query.get(regulation_version_id)
    regulation_version.data = data
    regulation_version.parent_regulation().base_document = data['header_base_doc']
    db.session.commit()
    return redirect(request.referrer)