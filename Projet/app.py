from flask import *
from sqlalchemy import *
import os, hashlib, json

app = Flask(__name__)

app.secret_key = os.urandom(256)

SALT = 'foo#BAR_{baz}^666'

engine = create_engine('sqlite:///base.db', echo=True)
metadata = MetaData()

Rubriques = Table('Rubriques', metadata,
    Column('id', Integer, primary_key=True),
    Column('titre', String, nullable=False),
    Column('id_page', Integer, nullable=False))
    
Elements = Table('Elements', metadata,
	Column('id', Integer, primary_key=true),
	Column('id_rubrique', Integer, nullable=False),
	Column('texte', String, nullable=False),
	Column('lien', String))

def hash_for(password):
	salted = '%s @ %s' % (SALT, password)
	return hashlib.sha256(salted).hexdigest()

@app.route('/', methods=['GET', 'POST']) 
def index():
	if 'application/json' not in request.headers['Content-Type'] :
		print  request.headers['Content-Type']
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


if __name__ == '__main__':
    app.run(debug=True)
