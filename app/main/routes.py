from app import db
from app.main import bp
from flask import render_template, redirect, url_for, request
from flask_login import current_user, login_required
from app.models import Regulation, RegulationVersion, BaseDoc
from app.main.forms import RenameRegulationForm, AddBaseDocumentLink
import json
import re


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
    regulation_version.data = json.dumps({})
    regulation_version.regulation_id = regulation.id
    db.session.add(regulation_version)
    db.session.commit()
    return redirect(url_for('main.regulation_show', regulation_version_id=regulation_version.id))


@bp.route('/show_regulation_<regulation_version_id>', methods=['GET', 'POST'])
@login_required
def regulation_show(regulation_version_id):
    regulation_version: RegulationVersion = RegulationVersion.query.get(regulation_version_id)
    data = json.loads(regulation_version.data)
    rename_regulation_form = RenameRegulationForm()
    add_document_link = AddBaseDocumentLink()

    if rename_regulation_form.validate_on_submit():
        regulation_version.parent_regulation().short_name = rename_regulation_form.name.data
        db.session.commit()
        return redirect(request.referrer)

    if add_document_link.validate_on_submit():
        new_doc = BaseDoc()
        new_doc.link = add_document_link.link.data
        new_doc.regulation_id = regulation_version.parent_regulation().id
        db.session.add(new_doc)
        db.session.commit()
        return redirect(request.referrer)

    return render_template('main/regulation_editor.html',
                           title='Редактор регламента',
                           regulation_version=regulation_version,
                           data=data,
                           rename_regulation_form=rename_regulation_form,
                           add_document_link=add_document_link,
                           regulation_base_documents=regulation_version.parent_regulation().get_base_documents())


@bp.route('/save_regulation_<regulation_version_id>', methods=['POST'])
@login_required
def regulation_save(regulation_version_id):
    data = json.loads(json.dumps(request.form))
    print(data)
    regulation_version: RegulationVersion = RegulationVersion.query.get(regulation_version_id)
    regulation_version_data = json.loads(regulation_version.data)
    for item in data:
        regulation_version_data[item] = data[item]
    regulation_version.data = json.dumps(regulation_version_data)
    # regulation_version.parent_regulation().base_document = data['header_base_doc']
    db.session.commit()
    return redirect(request.referrer)


@bp.route('/editor_add_chapter_<regulation_version_id>', methods=['GET', 'POST'])
@login_required
def editor_add_chapter(regulation_version_id):
    regulation_version: RegulationVersion = RegulationVersion.query.get(regulation_version_id)
    regulation_version_data = json.loads(regulation_version.data)
    chapters_count = 0
    for item in regulation_version_data:
        if re.match('chapter_\d', item):
            chapters_count += 1
    regulation_version_data[f'chapter_{chapters_count+1}'] = ''
    regulation_version.data = json.dumps(regulation_version_data)
    db.session.commit()
    return redirect(request.referrer)

@bp.route('/add_paragraph_<regulation_version_id>_<chapter_number>')
def add_paragraph(regulation_version_id, chapter_number):
    regulation_version: RegulationVersion = RegulationVersion.query.get(regulation_version_id)
    regulation_version_data = json.loads(regulation_version.data)

    paragraph_count = 0
    for item in regulation_version_data:
        if re.match(f'paragraph_{chapter_number}_\d', item):
            paragraph_count += 1
    regulation_version_data[f'paragraph_{chapter_number}_{paragraph_count+1}'] = ''
    regulation_version.data = json.dumps(regulation_version_data)
    db.session.commit()
    return redirect(request.referrer)