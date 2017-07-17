from flask import Blueprint, flash, render_template, request, redirect, url_for,g
from app import app,db
from flask_login import login_required
from helpers import object_list #For pagination
from models import Entry, Tag
from entries.forms import EntryForm, ImageForm
from werkzeug import secure_filename
import os

"""Flash message doesn't work in Atom browser but works in Chrome.

Probably due to cookie management"""



entries = Blueprint('entries', __name__, template_folder='templates')

@entries.route('/')
def index():
    entries = Entry.query.order_by(Entry.created_timestamp.desc())
    # return object_list('entries/index.html', entries) #object lsit renders paginated entries (by20)
    return entry_list('entries/index.html', entries) #performs the search

@entries.route('/tags/')
def tag_index():
    tags = Tag.query.order_by(Tag.name)
    return object_list('entries/tag_index.html', tags)

@entries.route('/tags/<slug>/')
def tag_detail(slug):
    tag = Tag.query.filter(Tag.slug == slug).first_or_404()
    entries = tag.entries.order_by(Entry.created_timestamp.desc())
    return entry_list('entries/tag_detail.html', entries, tag=tag)
    # return object_list('entries/tag_detail.html', entries, tag=tag)

####### The detail function
@entries.route('/<slug>/')
def detail(slug):
    entry = get_entry_or_404(slug,author=None) ##helper function from below which checks for Status of the Entry
    return render_template('entries/detail.html', entry=entry)

######## CREATING and EDITING and DELETING Posts
#this function is being hit twice. First time when the user opens the page and
#and second time when the user posts the form
@entries.route('/create/', methods=['GET', 'POST'])
@login_required #will handle the next_page redirect alone
def create():
    if request.method == 'POST':
        form = EntryForm(request.form)
        if form.validate():
            entry = form.save_entry(Entry(author=g.user))
            db.session.add(entry)
            db.session.commit()
            flash('Entry "%s" created successfully.' % entry.title, 'success')
            return redirect(url_for('entries.detail', slug=entry.slug))
    else:
        form = EntryForm()

    return render_template('entries/create.html', form=form) #object lsit renders paginated entries (by20)

@entries.route('/<slug>/edit/', methods=['GET', 'POST'])
@login_required
def edit(slug):
    entry = get_entry_or_404(slug,author=None) ##helper function from below which checks for Status of the Entry
    if request.method == 'POST':
        form = EntryForm(request.form, obj=entry)
        if form.validate():
            entry = form.save_entry(entry)
            db.session.add(entry)
            db.session.commit()
            flash('Entry "%s" has been saved.' % entry.title, 'success')
            return redirect(url_for('entries.detail', slug=entry.slug))
    else:
        form = EntryForm(obj=entry)

    return render_template('entries/edit.html', entry=entry, form=form)

@entries.route('/<slug>/delete/', methods=['GET', 'POST'])
@login_required
def delete(slug):
    entry =get_entry_or_404(slug,author=None) ##helper function from below which checks for Status of the Entry
    if request.method == 'POST':
        entry.status = Entry.STATUS_DELETED
        db.session.add(entry)
        db.session.commit()
        flash('Entry "%s" has been deleted.' % entry.title, 'success')
        return redirect(url_for('entries.index'))

    return render_template('entries/delete.html', entry=entry)

################################### IMAGES
@entries.route('/image-upload/', methods=['GET', 'POST'])
@login_required
def image_upload():
    if request.method == 'POST':
        form = ImageForm(request.form)
        if form.validate():
            image_file = request.files['file']
            filename = os.path.join(app.config['IMAGES_DIR'],
                                    secure_filename(image_file.filename))
            image_file.save(filename)
            flash('Saved %s' % os.path.basename(filename), 'success')
            return redirect(url_for('entries.index'))
    else:
        form = ImageForm()

    return render_template('entries/image_upload.html', form=form)

@entries.route('/images')
def image_view():

    all_images=[]
    for filename in os.listdir(app.config['IMAGES_DIR']):
        print(filename , "aaand", app.config['IMAGES_DIR'])
        if filename.endswith(".jpg"):
            all_images.append(os.path.join(app.config['IMAGES_DIR'], filename))
        else:
            continue
    return render_template('entries/images_show.html',all_images=all_images)

##################### This helper function is useful for
#prefeltering entries. Checking for Search filter if any, paginating if needed, and
#displaying only Statuses we require !

def entry_list(template, query, **context):
    query = filter_status_by_user(query)

    valid_statuses = (Entry.STATUS_PUBLIC, Entry.STATUS_DRAFT)
    query = query.filter(Entry.status.in_(valid_statuses))
    if request.args.get("q"):
        search = request.args["q"]
        query = query.filter(
            (Entry.body.contains(search)) |
            (Entry.title.contains(search)))
    return object_list(template, query, **context) #object lsit renders paginated entries (by20)

def get_entry_or_404(slug,author=None):
  query = Entry.query.filter(Entry.slug == slug)
  if author:
        query = query.filter(Entry.author == author)
  else:
        query = filter_status_by_user(query)
  return query.first_or_404()

#This function makes sure that
def filter_status_by_user(query):
 if not g.user.is_authenticated:
        query = query.filter(Entry.status == Entry.STATUS_PUBLIC)
 else:
    # Allow user to view their own drafts.
    query = query.filter(
        (Entry.status == Entry.STATUS_PUBLIC) |
        ((Entry.author == g.user) &
         (Entry.status != Entry.STATUS_DELETED)))
 return query
