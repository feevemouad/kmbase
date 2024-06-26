from flask import Flask
from config import Config
from models import db
from routes.user_routes import user_bp
from routes.pdf_routes import pdf_bp

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(pdf_bp, url_prefix='/api')

@app.before_request
def create_tables():
    app.before_request_funcs[None].remove(create_tables)
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
