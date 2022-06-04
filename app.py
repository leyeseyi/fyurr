#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
# from xmlrpc.client import DateTime
import dateutil.parser
import sys
import babel
from sqlalchemy import func
from flask import Flask, render_template, request, Response, flash, redirect, url_for, request
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from forms import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)


# Models.

from models import *

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
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
    areas = Venue.query.with_entities(func.count(Venue.id), Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
    for area in areas:
      area_venue=Venue.query.filter_by(state=area.state).filter_by(city=area.city).all() 
    
    return render_template('pages/venues.html', areas=areas, area_venue=area_venue)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form.get('search_term')
    if search_term:
        venues = Venue.query.filter(Venue.name.contains(search_term)|Venue.city.contains(search_term))
        search_count= Venue.query.filter(Venue.name.contains(search_term)|Venue.city.contains(search_term)).count()
    else:
        return redirect(url_for('venues'))
   
    return render_template('pages/search_venues.html', venues=venues, search_count=search_count, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    real_venue = Venue.query.filter_by(id=venue_id).all()
    upcoming_shows = Show.query.filter_by(
        venue_id=venue_id, future_show=True).all()
    past_shows = Show.query.filter_by(
        venue_id=venue_id, future_show=False).all()
    upcoming_show_count = Show.query.filter_by(
        venue_id=venue_id, future_show=True).count()
    past_show_count = Show.query.filter_by(
        venue_id=venue_id, future_show=False).count()
    return render_template('pages/show_venue.html', real_venue=real_venue, past_shows=past_shows, past_show_count=past_show_count, upcoming_shows=upcoming_shows, upcoming_show_count=upcoming_show_count)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    error = False
    try:
        form = VenueForm()
        if form.validate_on_submit():
            venue_to_create = Venue(name=form.name.data, city=form.city.data, state=form.state.data, address=form.address.data, phone=form.phone.data, image_link=form.image_link.data, genres=form.genres.data,
                                    facebook_link=form.facebook_link.data, website_link=form.website_link.data, seeking_talent=form.seeking_talent.data, seeking_description=form.seeking_description.data)
            db.session.add(venue_to_create)
            db.session.commit()

    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash(
            f'There was an error with creating a venue:{form.name.data}', category='danger')
    else:
        flash(f'Venue  {form.name.data} was successfully listed!',
              category='success')

    return render_template('pages/home.html')


@app.route('/delete_venue/<venue_id>')
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    error = False
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash(f'An error occurred. Venue {venue_id} could not be deleted.')
    else:
        flash(f'Venue {venue_id} was successfully deleted.')
        return redirect(url_for('index'))
    return render_template('pages/home.html')

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database

    real_artist = Artist.query.all()
    return render_template('pages/artists.html', real_artist=real_artist)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get('search_term')
    if search_term:
        artists = Artist.query.filter(Artist.name.contains(search_term))
        search_count= Artist.query.filter(Artist.name.contains(search_term)).count()
    else:
        return redirect(url_for('artists'))
    return render_template('pages/search_artists.html', artists=artists, search_count=search_count, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    real_data = Artist.query.filter_by(id=artist_id).all()
    upcoming_shows = Show.query.filter_by(
        artist_id=artist_id, future_show=True).all()

    past_shows = Show.query.filter_by(
        artist_id=artist_id, future_show=False).all()
    upcoming_show_count = Show.query.filter_by(
        artist_id=artist_id, future_show=True).count()
    past_show_count = Show.query.filter_by(
        artist_id=artist_id, future_show=False).count()
    return render_template('pages/show_artist.html', real_data=real_data, past_shows=past_shows, past_show_count=past_show_count, upcoming_shows=upcoming_shows, upcoming_show_count=upcoming_show_count)

#  Update
#  ----------------------------------------------------------------


@app.route('/edit_artist/<int:artist_id>', methods=['GET'])
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
        form.website_link.data = artist.website_link
        form.seeking_venue.data = artist.seeking_venues
        form.seeking_description.data = artist.seeking_description
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    
    error = False
    artist = Artist.query.get(artist_id)
    try:
        artist.name = request.form['name']
        artist.city = request.form['city']
        artist.state = request.form['state']
        # artist.address = request.form['address']
        artist.phone = request.form['phone']
        artist.genres = request.form.getlist('genres')
        artist.image_link = request.form['image_link']
        artist.facebook_link = request.form['facebook_link']
        artist.website_link = request.form['website_link']
        artist.seeking_venues = True if 'seeking_venue' in request.form else False
        artist.seeking_description = request.form['seeking_description']
    
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash(f'An error occurred. Artist could not be changed.')
    if not error:
        flash(f'Artist was successfully updated!')
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/edit_venue/<int:venue_id>', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)

    if venue:
        form.name.data = venue.name
        form.city.data = venue.city
        form.state.data = venue.state
        form.phone.data = venue.phone
        form.address.data = venue.address
        form.genres.data = venue.genres
        form.facebook_link.data = venue.facebook_link
        form.image_link.data = venue.image_link
        form.website_link.data = venue.website_link
        form.seeking_talent.data = venue.seeking_talent
        form.seeking_description.data = venue.seeking_description
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    error = False
    venue = Venue.query.get(venue_id)
    try:
        venue.name = request.form['name']
        venue.city = request.form['city']
        venue.state = request.form['state']
        venue.address = request.form['address']
        venue.phone = request.form['phone']
        venue.genres = request.form.getlist('genres')
        venue.image_link = request.form['image_link']
        venue.facebook_link = request.form['facebook_link']
        venue.website_link = request.form['website_link']
        venue.seeking_talent = True if 'seeking_talent' in request.form else False
        venue.seeking_description = request.form['seeking_description']
    
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash(f'An error occurred. Venue could not be changed.')
    if not error:
        flash(f'Venue was successfully updated!')
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
    form = ArtistForm()
    if form.validate_on_submit():
        artist_to_create = Artist(name=form.name.data, city=form.city.data, state=form.state.data, phone=form.phone.data, image_link=form.image_link.data, genres=form.genres.data,
                                  facebook_link=form.facebook_link.data, website_link=form.website_link.data, seeking_venues=form.seeking_venue.data, seeking_description=form.seeking_description.data)
        db.session.add(artist_to_create)
        db.session.commit()
        # on successful db insert, flash success
        flash(
            f'Artist  {artist_to_create.name} was successfully listed!', category='success')
    # TODO: modify data to be the data object returned from db insertion

    else:
        flash(
            f'There was an error with creating a venue:{form.name.data}', category='danger')

    # on successful db insert, flash success
    # flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    shows = Show.query.join(Artist).join(Venue).all()

    return render_template('pages/shows.html', shows=shows)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    future_date = True
    form = ShowForm()
    if form.start_time.data < datetime.today():
        future_date = False

    if form.validate_on_submit():
        show_to_create = Show(artist_id=form.artist_id.data, venue_id=form.venue_id.data,
                              start_time=form.start_time.data, future_show=future_date)
        db.session.add(show_to_create)
        db.session.commit()
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead

    # on successful db insert, flash success
    flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
