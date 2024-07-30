from flask import Flask, request  # type: ignore
from config import Config
import yaml
from models import db
from Middleware.Middleware import Middleware
from Services.JWTService import JWTService
from routes.user_routes import user_bp
from routes.pdf_routes import pdf_bp
from routes.auth_routes import auth_bp

app = Flask(__name__)
app.config.from_object(Config)

with open("../config/config.yaml") as f:
    yaml_dict = yaml.safe_load(f)
    jwt_secret = yaml_dict["jwt_service"]['jwt_secret']

jwt_service = JWTService(jwt_secret)
middleware = Middleware(jwt_service)

app.before_request(lambda: middleware.auth(request))

db.init_app(app)

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(pdf_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api')

@app.before_request
def create_tables():
    app.before_request_funcs[None].remove(create_tables)
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)    
