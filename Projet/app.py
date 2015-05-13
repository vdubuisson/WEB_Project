from flask import *
from sqlalchemy import *
import os, hashlib, json

app = Flask(__name__)

app.secret_key = os.urandom(256)

SALT = 'foo#BAR_{baz}^666'

engine = create_engine('sqlite:///base.db', echo=True)
metadata = MetaData()

Rubriques = Table('Rubriques', metadata,
    Column('id', Integer, primary_key=true),
    Column('titre', String, nullable=False),
    Column('id_parent', Integer),
    Column('id_page', Integer, nullable=False))

def hash_for(password):
	salted = '%s @ %s' % (SALT, password)
	return hashlib.sha256(salted).hexdigest()

@app.route('/')
def index():
	db = engine.connect()
	#data = []
	try:
		row = db.execute(select([Rubriques.c.titre]).where(Rubriques.c.id == 1)).fetchone()
		#for title in row:
		#	data.append({'titre': title})
	finally:
		db.close()
	data = [{'titre':row[0]}]
	content = json.dumps(data)
	return render_template('accueil.html', name="Accueil", rubriques=content)

    































if __name__ == '__main__':
    app.run(debug=True)
