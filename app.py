#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import pytz
from sqlalchemy import desc
import re
import sys
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from models import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
# db = SQLAlchemy(app)
db.init_app(app)
migrate = Migrate(app, db)
# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# class Venue(db.Model):
#     __tablename__ = 'venues'

#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String)
#     city = db.Column(db.String(120))
#     state = db.Column(db.String(120))
#     address = db.Column(db.String(120))
#     phone = db.Column(db.String(120))
#     image_link = db.Column(db.String(500))
#     facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# class Artist(db.Model):
#     __tablename__ = 'artists'

#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String)
#     city = db.Column(db.String(120))
#     state = db.Column(db.String(120))
#     phone = db.Column(db.String(120))
#     genres = db.Column(db.String(120))
#     image_link = db.Column(db.String(500))
#     facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
# db.create_all()
with app.app_context():
    db.create_all()
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  areas=[]
  i=0
  j=0
  utc=pytz.UTC
  taw = utc.localize(datetime.now()) 
  allv=Venue.query.distinct(Venue.city, Venue.state).all()
  while i < len(allv):
    onereslt={"city": allv[i].city,
            "state": allv[i].state}
    venCIST=Venue.query.filter_by(city=allv[i].city, state=allv[i].state).all()
    num_up=0
    venues=[]
    for v in venCIST:
      shows = Show.query.filter_by(venues_id=v.id).all()
      for show in shows:
        if show.start_time >taw:
          num_up+= 1
      venues.append({
                "id": v.id,
                "name": v.name,
                "num_upcoming_shows": num_up
            })
    onereslt["venues"] = venues
    areas.append(onereslt)
    i=i+1
    
  return render_template('pages/venues.html', areas=areas);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  utc=pytz.UTC
  taw = utc.localize(datetime.now()) 
  kifchybanou = []
  for v in Venue.query.filter(Venue.name.ilike(f'%{request.form.get("search_term")}%')).all():
    gdchlga = 0
    for shows in v.shows:
       if(shows.start_time > taw):
        gdchlga +=1
    kifchybanou.append({
      'id':v.id,
      'name': v.name,
      'num_upcoming_shows': gdchlga 
   })       
  return render_template('pages/search_venues.html', results={
    "count": len(kifchybanou),
    "data":kifchybanou}, search_term=request.form.get('search_term', ''))
 
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  if(len(Venue.query.filter_by(id=venue_id).all())!=0):
    utc=pytz.UTC
    taw = utc.localize(datetime.now()) 
    v = Venue.query.get(venue_id)
    shows = db.session.query(Show).join(Artist).all()
    artist=db.session.query(Artist)
    fatou= []
    mazalou = []
    showsfatou=[]
    showsmazalou=[]
    for s in shows:
      if s.venues_id == v.id:
        if s.start_time < taw:
          fatou.append(s)
        else:
          mazalou.append(s)
    for show in fatou:
      for a in artist:
        if a.id==show.artists_id:
          showsfatou.append({
            'artist_id': show.artists_id,
            'artist_name': a.name,
            'artist_image_link': a.image_link,
            'start_time': show.start_time.strftime("%c")
            })
    for show in mazalou:
      for a in artist:
        if a.id==show.artists_id:
          showsmazalou.append({
            'artist_id': show.artists_id,
            'artist_name': a.name,
            'artist_image_link': a.image_link,
            'start_time': show.start_time.strftime("%c")
            })
    vi= {
            'id': v.id,
            'name': v.name,
            'genres': v.genres,
            'address': v.address,
            'city':v.city,
            'state': v.state,
            'phone': v.phone,
            'website': v.website,
            'facebook_link': v.facebook_link,
            'image_link': v.image_link,
            'seeking_talent': v.seeking_talent,
            'seeking_description': v.seeking_description,
            'past_shows': showsfatou,
            'upcoming_shows': showsmazalou,
            'past_shows_count': len(showsfatou),
            'upcoming_shows_count': len(showsmazalou)
            }

    return render_template('pages/show_venue.html', venue=vi)
  else:
    flash('Venue does not exist')
    return redirect(url_for('venues'))

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

    # if request.form['phone'] == "":
    #         flash('Your Phone number has to be 15 number in format ', 'error')
    #         return render_template('forms/new_venue.html', form=form)
    # if request.form['phone'].isalpha():
    #         flash('Invalid phone number format', 'error')
    #         return render_template('forms/new_venue.html', form=form)
    # if not re.search(r"\d{3}[-]\d{3}[-]\d{4}$", request.form['phone']):
    #         flash('Invalid phone number', 'error')
    #         return render_template('forms/new_venue.html', form=form)
    # if  request.form['image_link'] == "":
    #         flash('Please provide a valid URL for the image link.', 'error')
    #         return render_template('forms/new_venue.html', form=form)
    # if request.form['website_link'] == "":
    #         flash('Please provide a valid URL for the website link.', 'error')
    #         return render_template('forms/new_venue.html', form=form)
    # if request.form.get('seeking_talent')  == 'y':
    #         seeking_talent = True
    #         if request.form['seeking_description'] == "":
    #             flash('Please enter a description for the venue you seek.', 'error')
    #             return render_template('forms/new_venue.html', form=form)
  # try:
    
  #   NewVenue = Venue(name=request.form['name'],
  # city=request.form['city'],
  # state=request.form['state'],
  # address=request.form['address'],
  # phone=request.form['phone'],
  # image_link=request.form['image_link'],
  # facebook_link=request.form.get('facebook_link'),
  # genres=request.form.getlist('genres'),
  # website=request.form['website_link'],
  # seeking_talent=seeking_talent,
  # seeking_description=request.form['seeking_description'])
  #   for v in allv:
  #     if v==NewVenue:
  #       flash('exust v', 'error')
  #       return render_template('forms/new_venue.html', form=form)
  #   db.session.add(NewVenue)
  #   db.session.commit()
  # except:
  #           error = True
  #           db.session.rollback()
  #           print(sys.exc_info())
  # finally:
  #           db.session.close()
  # if not error:
  #           flash('Venue ' + request.form['name'] + ' was successfully listed!', 'success')
  #           return redirect(url_for('index'))
  # else:
  #           flash('An error occurred. Venue ' +
  #              request.form['name'] + ' could not be listed.', 'error')
  #           return render_template('forms/new_venue.html', form=form)
  form = VenueForm(request.form)
  new_venue = Venue()
  seeking_talent=False
  if form.validate():
      # TODO: insert form data as a new Venue record in the db, instead
      # TODO: modify data to be the data object returned from db insertion
      if request.form['phone'].isalpha():
            flash('Invalid phone number format', 'error')
            return render_template('forms/new_venue.html', form=form)
      if not re.search(r"\d{3}[-]\d{3}[-]\d{4}$", request.form['phone']):
            flash('Invalid phone number', 'error')
            return render_template('forms/new_venue.html', form=form)  
      if request.form.get('seeking_talent')  == 'y':
            seeking_talent = True
            if request.form['seeking_description'] == "":
                flash('Please enter a description for the venue you seek.', 'error')
                return render_template('forms/new_venue.html', form=form)
      new_venue.name = request.form['name']
      new_venue.city = request.form['city']
      new_venue.state = request.form['state']
      new_venue.address = request.form['address']
      new_venue.phone = request.form['phone']
      new_venue.facebook_link = request.form['facebook_link']
      new_venue.genres =request.form.getlist('genres')
      new_venue.website = request.form['website_link']
      new_venue.image_link = request.form['image_link']
      new_venue.seeking_description = request.form['seeking_description']
      new_venue.seeking_talent = seeking_talent
      try:
        db.session.add(new_venue)
        db.session.commit()

        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
      except:
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occured. Venue' + request.form["name"] + 'could not be listed')
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
      finally:
        db.session.close()
  else:
    flash(f'Error with venue {new_venue.name}')
    flash(form.errors)
    return render_template('forms/new_venue.html', form=form) 
  return render_template('pages/home.html')
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  return render_template('pages/artists.html', artists=Artist.query.all())

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  utc=pytz.UTC
  taw = utc.localize(datetime.now()) 
  kifchybanou = []
  for a in Artist.query.filter(Artist.name.ilike( f'%{request.form.get("search_term")}%' )).all():
    gdchlga = 0
    for shows in a.shows:
       if(shows.start_time > taw):
        gdchlga +=1
    kifchybanou.append({
      'id':a.id,
      'name': a.name,
      'num_upcoming_shows': gdchlga 
   })       
  
  return render_template('pages/search_artists.html', results={
    "count": len(kifchybanou),
    "data":kifchybanou}, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  # utc=pytz.UTC
  # taw = utc.localize(datetime.now()) 
  # artists = Artist.query.get(artist_id)
  # shows = db.session.query(Show).join(Venue).all()
  # aLLven=db.session.query(Venue)
  # fatou= []
  # mazalou = []
  # showsfatou=[]
  # showsmazalou=[]
  # genres=[]
  # for s in shows:
  #   if s.artists_id == artists.id:
  #     if s.start_time < taw:
  #       fatou.append(s)
  #     else:
  #       mazalou.append(s)
  

  # for show in fatou:
  #   for a in aLLven:
  #     if a.id==show.venues_id:
  #       showsfatou.append({
  #           'venue_id': show.artists_id,
  #           'venue_name': a.name,
  #           'venue_image_link': a.image_link,
  #           'start_time': show.start_time.strftime("%c")
  #           })

  # for show in mazalou:
  #   for a in aLLven:
  #     if a.id==show.venues_id:
  #        showsmazalou.append({
  #           'venue_id': show.artists_id,
  #           'venue_name': a.name,
  #           'venue_image_link': a.image_link,
  #           'start_time': show.start_time.strftime("%c")
  #           })

  # vi={
  #   "id": artists.id,
  #   "name":artists.name,
  #   "genres":artists.genres,
  #   "city": artists.city,
  #   "state": artists.state,
  #   "phone": artists.phone,
  #   "seeking_venue": artists.seeking_venue,
  #   "image_link": artists.image_link,
  #   "seeking_description":artists.seeking_description,
  #   'past_shows': showsfatou,
  #   'upcoming_shows': showsmazalou,
  #   'past_shows_count': len(showsfatou),
  #   'upcoming_shows_count': len(showsmazalou)
  # }
  # return render_template('pages/show_artist.html', artist=vi)
  utc=pytz.UTC
  myartist = Artist.query.get(artist_id)
  if(len(Artist.query.filter_by(id=artist_id).all())!=0):
    past = []
    for show in Show.query.filter(Show.artists_id==artist_id).order_by(desc(Show.start_time)).limit(10):
      if show.start_time < utc.localize(datetime.now()):
        past.append({
          "venue_id":show.venues_id,
          "venue_name":Venue.query.filter(Venue.id==show.venues_id).first().name,
          "venue_image_link":Venue.query.filter(Venue.id==show.venues_id).first().image_link,
          "start_time":show.start_time.strftime("%c")
          
        })  
    upcoming = []
    for show in Show.query.filter(Show.artists_id==artist_id).order_by(desc(Show.start_time)).limit(10):
      if show.start_time > utc.localize(datetime.now()):
        upcoming.append({
          "venue_id":show.venues_id,
          "venue_name":Venue.query.filter(Venue.id==show.venues_id).first().name,
          "venue_image_link":Venue.query.filter(Venue.id==show.venues_id).first().image_link,
          "start_time":show.start_time.strftime("%c")
        })
    data={
      "id": myartist.id,
      "name": myartist.name,
      "genres": myartist.genres,
      "city": myartist.city,
      "state": myartist.state,
      "phone": myartist.phone,
      "website": myartist.website,
      "facebook_link": myartist.facebook_link,
      "seeking_venue": myartist.seeking_venue,
      "seeking_description": myartist.seeking_description,
      "image_link": myartist.image_link,
      "past_shows": past,
      "upcoming_shows": upcoming,
      "past_shows_count": len(past),
      "upcoming_shows_count": len(upcoming)
    }
    data = list(filter(lambda d: d['id'] == artist_id, [data]))[0]
    return render_template('pages/show_artist.html',past_shows=past,upcoming_shows=upcoming,artist=data)
  else:
    flash('Artist does not exist')
    return redirect(url_for('artists'))
#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  if artist: 
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres
    form.facebook_link.data = artist.facebook_link
    form.image_link.data = artist.image_link
    form.website_link.data = artist.website
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description
    return render_template('forms/edit_artist.html', form=form, artist=artist)
@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    form = ArtistForm(request.form)
    artist_data = Artist.query.get(artist_id)
    if artist_data:
        if form.validate():
            seeking_venue = False
            seeking_description = ''
            if 'seeking_venue' in request.form:
                seeking_venue = request.form['seeking_venue'] == 'y'
            if 'seeking_description' in request.form:
                seeking_description = request.form['seeking_description']
            setattr(artist_data, 'name', request.form['name'])
            setattr(artist_data, 'genres', request.form.getlist('genres'))
            setattr(artist_data, 'city', request.form['city'])
            setattr(artist_data, 'state', request.form['state'])
            setattr(artist_data, 'phone', request.form['phone'])
            setattr(artist_data, 'website', request.form['website_link'])
            setattr(artist_data, 'facebook_link', request.form['facebook_link'])
            setattr(artist_data, 'image_link', request.form['image_link'])
            setattr(artist_data, 'seeking_description', seeking_description)
            setattr(artist_data, 'seeking_venue', seeking_venue)
            db.session.commit()
            return redirect(url_for('show_artist', artist_id=artist_id))
        else:
            print(form.errors)
    return render_template('errors/404.html'), 404

  

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  # try:
  #   oneart=Artist(name=request.form.get('name'),
  #   city=  request.form.get('city'),
  #   state=  request.form.get('state'),
  #   phone=  request.form.get('phone'),
  #   genres= request.form.getlist('genres'),
  #   facebook_link=  request.form.get('facebook_link'),
  #   image_link=request.form.get('image_link'),
  #   website= request.form.get('website'),
  #   seeking_description=request.form.get('seeking_description'))
   
  #   db.session.add(oneart)
  #   db.session.commit()
  #  # on successful db insert, flash success
  #   flash('Artist ' + request.form['name'] + ' was successfully listed!')
 
  # # TODO: on unsuccessful db insert, flash an error instead.
  # except:
  #   db.session.rollback()
  #   flash('An error occurred. Artist ' + oneart.name + ' could not be listed.')
  # finally:
  #   db.session.close()
  # return render_template('pages/home.html')

    # if not re.search(r"\d{3}[-]\d{3}[-]\d{4}$", request.form['phone']):
    #         flash('"Invalid phone number"', 'error')
    #         return render_template('forms/new_venue.html', form=form)
  
  form = ArtistForm(request.form)
  new_artist = Artist()
  seeking_venue = False
  if form.validate():
      # TODO: insert form data as a new Venue record in the db, instead
      # TODO: modify data to be the data object returned from db insertion
      if request.form['phone'].isalpha():
            flash('Invalid phone number format', 'error')
            return render_template('forms/new_artist.html', form=form)
      if not re.search(r"\d{3}[-]\d{3}[-]\d{4}$", request.form['phone']):
            flash('Invalid phone number', 'error')
            return render_template('forms/new_artist.html', form=form)  
      if request.form.get('seeking_venue') == 'y':
            seeking_venue = True
            if request.form['seeking_description'] == "":
                flash('Please enter a description for the venue you seek.', 'error')
                return render_template('forms/new_artist.html', form=form)
      new_artist.name = request.form['name']
      new_artist.city = request.form['city']
      new_artist.state = request.form['state']
      new_artist.phone = request.form['phone']
      new_artist.facebook_link = request.form['facebook_link']
      new_artist.genres = request.form.getlist('genres')
      new_artist.website = request.form['website_link']
      new_artist.image_link = request.form['image_link']
      new_artist.seeking_venue = seeking_venue
      new_artist.seeking_description = request.form['seeking_description']
      try:
        db.session.add(new_artist)
        db.session.commit()

        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!', 'success')
        
      except:
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Artist ' +
               request.form['name'] + ' could not be listed.', 'error')
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
      finally:
        db.session.close()
  else:
    flash(f'Error with Artist {new_artist.name}')
    flash(form.errors)
    return render_template('forms/new_artist.html', form=form)
  return render_template('pages/home.html')
#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows=db.session.query(
          Venue.name,
          Artist.name,
          Artist.image_link,
          Show.venues_id,
          Show.artists_id,
          Show.start_time
        ) \
        .filter(Venue.id == Show.venues_id, Artist.id == Show.artists_id)
  va = []
  for show in shows:
        va.append({
          'venue_name': show[0],
          'artist_name': show[1],
          'artist_image_link': show[2],
          'venue_id': show[3],
          'artist_id': show[4],
          'start_time': str(show[5])
        })
        
 
  data=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]
  return render_template('pages/shows.html', shows=va)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead    
  form = ShowForm(request.form)
  new_show = Show()
  if form.validate():
      # TODO: insert form data as a new Venue record in the db, instead
      # TODO: modify data to be the data object returned from db insertion
      if request.form['artist_id'] == '' or request.form['venue_id'] == '':
        flash('fill the id artist and id venue.', 'error')
        return render_template('forms/new_show.html', form=form)
      if Artist.query.get(request.form['artist_id']) == None:
            flash(' ID artist does not exists.', 'error')
            return render_template('forms/new_show.html', form=form)
      elif Venue.query.get(request.form['venue_id']) == None:
            flash('ID venue does not exists.', 'error')
            return render_template('forms/new_show.html', form=form)
    
      new_show.venues_id =request.form.get('venue_id')
      new_show.artists_id=request.form.get('artist_id')
      new_show.start_time=request.form.get('start_time')

      try:
        db.session.add(new_show)
        db.session.commit()

        # on successful db insert, flash success
        flash('Show was successfully listed!', 'success')
      except:
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Show could not be listed.', 'error')
        return render_template('forms/new_show.html', form=form)
        
            
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
      finally:
        db.session.close()
  else:
    flash(f'Error with show{new_venue.name}')
    flash(form.errors)
    return render_template('forms/new_show.html', form=form)
  return render_template('pages/home.html')
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''