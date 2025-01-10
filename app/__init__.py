# 150240721
# Berkay Emre Keskin
# BLG317E

import random
from flask import Flask
from app.auth import auth  
from app.landing import main  
from app.movies import movies_bp
from app.user import user  

app = Flask(__name__)
app.secret_key = random.randbytes(16) 
app.config['SECRET_KEY'] = 'top_secret'

# ----------------------------- REGISTERING THE BLUEPRINTS -----------------------------

app.register_blueprint(main, url_prefix='/')
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(movies_bp, url_prefix='/movies')
app.register_blueprint(user, url_prefix='/user')

if __name__ == '__main__':
    app.run(debug=True)
