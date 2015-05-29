from flask import *
from sqlalchemy import *
import os, hashlib, json
import jwt, Crypto.PublicKey.RSA as RSA, datetime

app = Flask(__name__)

app.secret_key = os.urandom(256)

key = RSA.generate(2048)

SALT = 'foo#BAR_{baz}^666'

engine = create_engine('sqlite:///base.db', echo=True)
metadata = MetaData()

Rubriques = Table('Rubriques', metadata,
    Column('id', Integer, primary_key=True),
    Column('titre', String, nullable=False),
    Column('id_page', Integer, nullable=False))
    
Elements = Table('Elements', metadata,
	Column('id', Integer, primary_key=True),
	Column('id_rubrique', Integer, nullable=False),
	Column('texte', String, nullable=False),
	Column('lien', String))

Pages = Table('Pages', metadata,
	Column('id', Integer, primary_key=True),
	Column('titre', String, nullable=False))

Admins = Table('Admins', metadata,
	Column('id', Integer, primary_key=True),
	Column('username', String, nullable=False),
	Column('hash_passwd', String, nullable=False))

Concert = Table('Concert', metadata,
	Column('id', Integer, primary_key=True),
	Column('titre', String, nullable=False),
	Column('date', String, nullable=False),
	Column('description', String),
	Column('auteur', String),
	Column('horaire', String, nullable=False),
	Column('lieu', String),
	Column('participation', String),
	Column('id_tarif', Integer),
	Column('style', String, nullable=False),
	Column('id_image', Integer),
	Column('id_video', Integer),
	Column('nb_places', Integer),
	Column('reservable', Integer))

Media = Table('Media', metadata,
	Column('id', Integer, primary_key=True),
	Column('titre', String, nullable=False),
	Column('type', String, nullable=False),
	Column('chemin', String, nullable=False))

Tarifs = Table('Tarifs', metadata,
	Column('id', Integer, primary_key=True),
	Column('enfant', Float),
	Column('etudiant', Float),
	Column('plein', Float))

def hash_for(password):
	salted = '%s @ %s' % (SALT, password)
	return hashlib.sha256(salted).hexdigest()

@app.route('/', methods=['GET', 'POST']) 
def index():
	if 'application/json' not in request.headers['Content-Type'] :
		return redirect(url_for('static', filename='index.html'))
		
	db = engine.connect()
	try:
		data = []
		row = db.execute(select([Rubriques.c.id, Rubriques.c.titre]).where(Rubriques.c.id_page == 1)).fetchall()
		
		for rubrique in row :
			row_elem = db.execute(select([Elements.c.texte, Elements.c.lien]).where(Elements.c.id_rubrique == rubrique[0])).fetchall()
			
			elements = []
			for element in row_elem :
				elements.append({'texte': element[0], 'lien': element[1]})
			
			data.append({'titre': rubrique[1], 'elements': elements})

	finally:
		db.close()
	return json.dumps(data)


@app.route('/Enseignement')
def enseignement():
	return redirect(url_for('static', filename='enseignement.html'))

@app.route('/Concert', methods=['GET', 'POST'])
def concert():
	if 'application/json' not in request.headers['Content-Type'] :
		return redirect(url_for('static', filename='concert.html'))

	req = request.json.get('type')
	if req == "all" :
		db = engine.connect()
		try:
			data = []
			row = db.execute(select([Concert])).fetchall()
		
			for concert in row :
				row_tarifs = db.execute(select([Tarifs]).where(Tarifs.c.id == concert[8])).fetchone()
				if row_tarifs :
					tarifs = {'enfant': row_tarifs[1], 'etudiant': row_tarifs[2], 'plein': row_tarifs[3]}
				else :
					tarifs = {}

				row_image = db.execute(select([Media]).where(Media.c.id == concert[10])).fetchone()
				if row_image :
					image = {'titre': row_image[1], 'chemin': row_image[3]}
				else :
					image = {}

				row_video = db.execute(select([Media]).where(Media.c.id == concert[11])).fetchone()
				if row_video :
					video = {'titre': row_video[1], 'chemin': row_video[3]}
				else :
					video = {}

				data.append({'titre': concert[1], 'date': concert[2], 'description': concert[3], 'auteur': concert[4], 'horaire': concert[5], 'lieu': concert[6], 'participation': concert[7], 'tarif': tarifs, 'style': concert[9], 'image': image, 'id_video': video, 'nb_places': concert[12], 'reservable': concert[13], 'deplie': False})

		finally:
			db.close()

		return json.dumps(data)


@app.route('/Connexion')
def connect():
	return redirect(url_for('static', filename='connexion.html'))

@app.route('/Authenticate', methods=['POST'])
def auth():
	username = request.json.get('username')
	password = hash_for(request.json.get('password'))
	
	db = engine.connect()
	try:
		row = db.execute(select([Admins]).where(Admins.c.username == username)).fetchone()

		if row and row[2] == password :
			payload = {'id': row[0], 'username': row[1]}
			token = jwt.generate_jwt(payload, key, 'PS256', datetime.timedelta(minutes=60))
			data = {'token': token}
			return json.dumps(data)
		else :
			abort(401)

	finally:
		db.close()


@app.route('/Ajout')
def ajout():
	return redirect(url_for('static', filename='ajout-concert.html'))

@app.route('/Suppression')
def suppression():
	return redirect(url_for('static', filename='suppression-concert.html'))

@app.route('/newConcert', methods=['POST'])
def newConcert():
	if 'Authorization' in request.headers :
		token = request.headers['Authorization']

		try:
			header, claims = jwt.verify_jwt(token, key, ['PS256'])
		except Exception, e:
			abort(403)

		concert = request.json
		tarif = concert.get('tarif')
		image = concert.get('image')
		video = concert.get('video')
		
		db = engine.connect()
		try:
			if tarif.get('enfant') or tarif.get('etudiant') or tarif.get('plein'):
				db.execute(Tarifs.insert(), [tarif])
				id_tarif = db.execute(select([func.max(Tarifs.c.id)])).fetchone()
				id_tarif = id_tarif[0]
			else :
				id_tarif = None

			if image.get('chemin'):
				db.execute(Media.insert(), [{'titre': image.get('titre'), 'type': "image", 'chemin': image.get('chemin')}])
				id_image = db.execute(select([func.max(Media.c.id)])).fetchone()
				id_image = id_image[0]
			else :
				id_image = None

			if video.get('chemin'):
				db.execute(Media.insert(), [{'titre': video.get('titre'), 'type': "video", 'chemin': video.get('chemin')}])
				id_video = db.execute(select([func.max(Media.c.id)])).fetchone()
				id_video = id_video[0]
			else :
				id_video = None

			db.execute(Concert.insert(), [{'titre': concert.get('titre'), 'date': concert.get('date'), 'description': concert.get('description'), 'auteur': concert.get('auteur'), 'horaire': concert.get('horaire'), 'lieu': concert.get('lieu'), 'participation': concert.get('participation'), 'id_tarif': id_tarif, 'style': concert.get('style'), 'id_image': id_image, 'id_video': id_video, 'nb_places': concert.get('nb_places'), 'reservable': concert.get('reservable')}])

			return "ok"
		finally:
			db.close()

	else :
		abort(401)
	
@app.route('/cleanConcert', methods=['POST'])
def cleanConcert():
	if 'Authorization' in request.headers :
		token = request.headers['Authorization']

		try:
			header, claims = jwt.verify_jwt(token, key, ['PS256'])
		except Exception, e:
			abort(403)

		date = request.json.get('date')
		
		db = engine.connect()
		try:
			row_tarif = db.execute(select([Concert.c.id_tarif]).where(Concert.c.date < date)).fetchall()
			for tarif in row_tarif:
				db.execute(Tarifs.delete(Tarifs.c.id == tarif[0]))

		finally:
			db.close()

		return "ok"

	else :
		abort(401)


if __name__ == '__main__':
    app.run(debug=True)
