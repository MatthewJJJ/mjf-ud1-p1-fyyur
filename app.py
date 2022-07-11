# Imports
import json
from msilib.schema import Error
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
from datetime import datetime

# App Config.
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Models.
class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True) 
    ven_name = db.Column(db.String)
    city = db.Column(db.String(120))
    ven_state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    web_link = db.Column(db.String(250))
    talent = db.Column(db.Boolean, default=False)
    description = db.Column(db.String)
    ven_shows = db.relationship('Show', backref='ven_list', lazy=True)

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True) 
    art_name = db.Column(db.String)
    city = db.Column(db.String(120))
    art_state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    web_link = db.Column(db.String(120))
    description = db.Column(db.String)
    looking_for_venue = db.Column(db.Boolean, default=False)
    art_shows = db.relationship('Show', backref='art_list', lazy=True)

class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    artist = db.Column(db.Integer, db.ForeignKey("artists.id"), nullable=False)
    show_location = db.Column(db.Integer, db.ForeignKey("venues.id"), nullable=False)
    start_time = db.Column(db.DateTime)

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

# Controllers.
@app.route('/')
def index():
  return render_template('pages/home.html')

def get_sorted_shows(data):
  now = datetime.now()
  past = []
  upcoming = []
  for element in data:
      print(element)
      format = "%Y-%m-%d %H:%M:%S"
      dt_object = datetime.strptime(element['start_time'], format)
      if now > dt_object:
        past.append(element)
      else:
        upcoming.append(element)
  return {'past': past, 'upcoming': upcoming}

def get_sorted_shows_mod(data):
  now = datetime.now()
  past = []
  upcoming = []
  for element in data:
      print(element)
      if now > element.start_time:
        past.append(element)
      else:
        upcoming.append(element)
  return {'past': past, 'upcoming': upcoming}

#  Venues
@app.route('/venues')
def venues():
  venue_data = db.session.query(Venue).group_by(Venue.id, Venue.city, Venue.ven_state).all()
  group_map = []
  aggregated_data = []
  for element in venue_data:
    shows = get_sorted_shows_mod(element.ven_shows)
    if f'{element.city}-{element.ven_state}' not in group_map:
      group_map.append(f'{element.city}-{element.ven_state}')
      aggregated_data.append({
        "city": element.city,
        "state": element.ven_state,
        "venues": [{
          "id": element.id,
          "name": element.ven_name,
          "num_upcoming_shows": len(shows['upcoming']), 
      }]})
    else:
      index = group_map.index(f'{element.city}-{element.ven_state}')
      aggregated_data[index]['venues'].append({
          "id": element.id,
          "name": element.ven_name,
          "num_upcoming_shows": len(shows['upcoming']),
      })
  return render_template('pages/venues.html', areas=aggregated_data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  data = db.session.query(Venue).filter(Venue.ven_name.like("%"+request.form.get('search_term', '')+"%")).all()
  aggregated_data = {"count": len(data), "data": []}
  for element in data:
    shows = get_sorted_shows_mod(element.ven_shows)
    aggregated_data["data"].append({
      "id": element.id, 
      "name": element.ven_name, 
      "num_upcoming_shows": len(shows['upcoming'])
      })
  return render_template('pages/search_venues.html', results=aggregated_data, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  data = Venue.query.filter_by(id=venue_id)
  if data.join(Show).join(Artist).all():
    data = data.join(Show).join(Artist).all()
  venue = data[0]
  aggregated_shows = []
  for element in venue.ven_shows:
    aggregated_shows.append(
      {
        "artist_name": element.art_list.art_name,
        "artist_id": element.art_list.id,
        "artist_image_link":element.art_list.image_link, 
        "start_time": str(element.start_time)
      }
    )
  aggregated_shows= get_sorted_shows(aggregated_shows)
  aggregated_data = {
    "id": venue.id,
    "name": venue.ven_name,
    "genres": str(venue.genres)[1:-1].split(','),
    "address": venue.address,
    "city": venue.city,
    "state": venue.ven_state,
    "phone": venue.phone,
    "website": venue.web_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.talent,
    "image_link": venue.image_link,
    "past_shows": aggregated_shows['past'], 
    "upcoming_shows": aggregated_shows['upcoming'],
    "past_shows_count": len(aggregated_shows['past']),
    "upcoming_shows_count": len(aggregated_shows['upcoming'])
  }
  return render_template('pages/show_venue.html', venue=aggregated_data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  try: 
    new_venue = Venue(
      ven_name=request.form['name'],
      city=request.form['city'],
      ven_state=request.form['state'],
      address=request.form['address'],
      phone=request.form['phone'],
      genres=request.form.getlist('genres'),
      image_link = request.form['image_link'],
      facebook_link = request.form['facebook_link'],
      web_link = request.form['website_link'],
      talent = bool('seeking_talent' in request.form  and request.form['seeking_talent'] == 'y'),
      description = request.form['seeking_description']
    )
    db.session.add(new_venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except Exception as e:
    print(e)
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try: 
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except Exception as e:
    print(e)
    db.session.rollback()
  finally:
    db.session.close()
  return None

#  Artists
@app.route('/artists')
def artists():
  aggregated_data = []
  raw_data = Artist.query.all()
  for element in raw_data:
    aggregated_data.append({"id":element.id,"name":element.art_name})
  return render_template('pages/artists.html', artists=aggregated_data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  data = db.session.query(Artist).filter(Artist.art_name.like("%"+request.form.get('search_term', '')+"%")).all()
  aggregated_data = {"count": len(data), "data": []}
  for element in data:
    shows = get_sorted_shows_mod(element.art_shows)
    aggregated_data["data"].append({
      "id": element.id, 
      "name": element.art_name, 
      "num_upcoming_shows": len(shows['upcoming'])
      })
  return render_template('pages/search_artists.html', results=aggregated_data, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  data = Artist.query.filter_by(id=artist_id)
  if data.join(Show).join(Venue).all():
    data = data.join(Show).join(Venue).all()
  artist = data[0]
  aggregated_shows = []
  for element in artist.art_shows:
    aggregated_shows.append(
      {
        "venue_id": element.ven_list.ven_name,
        "venue_id": element.ven_list.id,
        "venue_image_link":element.ven_list.image_link, 
        "start_time": str(element.start_time)
      }
    )
  aggregated_shows = get_sorted_shows(aggregated_shows)
  aggregated_data = {
    "id": artist.id,
    "name": artist.art_name,
    "genres": str(artist.genres)[1:-1].split(','),
    "city": artist.city,
    "state": artist.art_state,
    "phone": artist.phone,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.looking_for_venue,
    "image_link": artist.image_link,
    "website": artist.web_link,
    "past_shows": aggregated_shows['past'], 
    "upcoming_shows": aggregated_shows['upcoming'],
    "past_shows_count": len(aggregated_shows['past']),
    "upcoming_shows_count": len(aggregated_shows['upcoming']),
    "seeking_description": artist.description
  }
  return render_template('pages/show_artist.html', artist=aggregated_data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # UI wasn't accepting mock data and doesn't seem to be accepting mine either... 
  form = ArtistForm()
  query_response = Artist.query.filter_by(id=artist_id)
  data = query_response[0]
  artist={
    "id": data.id,
    "name": data.art_name,
    "genres": data.genres,
    "city": data.city,
    "state": data.art_state,
    "phone": data.phone,
    "facebook_link": data.facebook_link,
    "seeking_venue": data.looking_for_venue,
    "image_link": data.image_link,
    "website": data.web_link
  }
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  try: 
    artist = db.session.query(Artist).get(artist_id)
    if len(request.form['name']) > 0:
      artist.art_name = request.form['name']
    if len(request.form['city']) > 0:
      artist.city = request.form['city']
    if len(request.form['state']) > 0:
      artist.art_state = request.form['state']
    if len(request.form['phone']) > 0:
      artist.phone = request.form['phone']
    if len(request.form['genres']) > 0:
      artist.genres = request.form['genres']
    if len(request.form.getlist('genres')) > 0:
      artist.facebook_link = request.form['facebook_link']
    if len(request.form['image_link']) > 0:
      artist.image_link = request.form['image_link']
    if len(request.form['website']) > 0:
      artist.web_link = request.form['website']
    if request.form['seeking_venue']:
      artist.looking_for_venue = True
    db.session.commit()
  except Exception as e:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be edited ...')
    print(e)
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # UI wasn't accepting mock data and doesn't seem to be accepting mine either...
  form = VenueForm()
  query_response = Venue.query.filter_by(id=venue_id)
  data = query_response[0]
  venue ={
    "id": data.id,
    "name": data.ven_name,
    "genres": data.genres,
    "address": data.address,
    "city": data.city,
    "state": data.ven_state,
    "phone": data.phone,
    "website": data.web_link,
    "facebook_link": data.facebook_link,
    "seeking_talent": data.talent,
    "image_link": data.image_link
  }
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  try: 
    venue = db.session.query(Venue).get(venue_id)
    if len(request.form['name']) > 0:
      venue.ven_name = request.form['name']
    if len(request.form['city']) > 0:
      venue.city = request.form['city']
    if len(request.form['address']) > 0:
      venue.address = request.form['address']
    if len(request.form['state']) > 0:
      venue.ven_state = request.form['state']
    if len(request.form['phone']) > 0:
      venue.phone = request.form['phone']
    if len(request.form['genres']) > 0:
      venue.genres = request.form['genres']
    if len(request.form.getlist('genres')) > 0:
      Venue.facebook_link = request.form['facebook_link']
    if len(request.form['image_link']) > 0:
      venue.image_link = request.form['image_link']
    if len(request.form['website']) > 0:
      venue.web_link = request.form['website']
    db.session.commit()
  except Exception as e:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be edited ...')
    print(e)
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  try: 
    new_artist = Artist(
      art_name = request.form['name'],
      city = request.form['city'],
      art_state = request.form['state'],
      phone = request.form['phone'],
      genres = request.form.getlist('genres'),
      image_link = request.form['image_link'],
      facebook_link = request.form['facebook_link'],
      description = request.form['seeking_description'],
      looking_for_venue = bool('seeking_venue' in request.form  and request.form['seeking_venue'] == 'y')
    )
    db.session.add(new_artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully added!')
  except Exception as e:
    print(e)
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be added...')
  finally:
    db.session.close()
  return render_template('pages/home.html');


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  raw_data = db.session.query(Show).join(Artist).join(Venue).all()
  aggregated_data = []
  for element in raw_data:
    aggregated_data.append({
      "venue_id": element.show_location,
      "venue_name": element.ven_list.ven_name,
      "artist_id": element.artist,
      "artist_name": element.art_list.art_name,
      "artist_image_link": element.art_list.image_link,
      "start_time": str(element.start_time)
  })
  return render_template('pages/shows.html', shows=aggregated_data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST']) 
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  try: 
    new_show = Show(
      artist = request.form['artist_id'],
      show_location = request.form['venue_id'],
      start_time = request.form['start_time']
    )
    db.session.add(new_show)
    db.session.commit()
    flash('Show for artist with id ' + request.form['artist_id'] + ' was successfully added!')
  except Exception as e:
    print(e)
    db.session.rollback()
    flash('An error occurred. Show for artist with id  ' + request.form['artist_id'] + ' could not be added...')
  finally:
    db.session.close()
  return render_template('pages/home.html');

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

# Launch.

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
