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

@app.route('/', methods=['GET', 'POST']) 
def index():
	if 'application/json' not in request.headers['Content-Type'] :
		print  request.headers['Content-Type']
		return redirect(url_for('static', filename='index.html'))
		
	db = engine.connect()
	try:
		data = []
		row = db.execute(select([Rubriques.c.titre]).where(Rubriques.c.id_page == 1)).fetchall()
		for title in row:
			print(title)
			#data.append({'titre': title})
	finally:
		db.close()
	data = [{'titre': "Exemple"}, {'titre': "Ex 2"}, {'titre': "Ex autre"}]
	return json.dumps(data)
	
	
	

    































if __name__ == '__main__':
    app.run(debug=True)
