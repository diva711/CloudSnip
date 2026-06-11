from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from db import get_connection
from models import create_tables
from routes.auth import auth_bp
from routes.links import links_bp
from routes.analytics import analytics_bp

app = Flask(__name__)
CORS(app)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per minute"]
)

app.register_blueprint(auth_bp)
app.register_blueprint(links_bp)
app.register_blueprint(analytics_bp)

@app.route('/health')
def health():
    return {'status': 'ok'}, 200

if __name__ == '__main__':
    create_tables()
    app.run(host='0.0.0.0', port=5000)