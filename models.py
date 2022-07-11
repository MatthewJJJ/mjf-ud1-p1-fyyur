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