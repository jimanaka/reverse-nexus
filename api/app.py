from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager, get_jwt_identity, jwt_required, get_jwt
from flask_cors import CORS
from datetime import timedelta
import logging

from src.utils.mongo_context import MongoContext
import src.utils.auth as auth

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.config.from_object("src.config.Config")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=1)
# app.config['JWT_ACCESS_COOKIE_PATH'] = "/api/auth/"
app.config["JWT_REFRESH_COOKIE_PATH"] = "/api/token/"
app.config["JWT_REFRESH_CSRF_COOKIE_PATH"] = "/api/token/"
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_COOKIE_SECURE"] = False
app.config["CORS_HEADERS"] = "Content-Type"

jwt = JWTManager(app)
db_ctx = MongoContext(app)
CORS(app)
db = db_ctx.mongo.db

users_collection = db.users
templates_collection = db.templates
token_blacklist = db.tokenBlacklist
token_blacklist.create_index("expirationDate", expireAfterSeconds=0)


@app.route("/test")
def hello_world():
    return jsonify(status="api is up!"), 200


@app.route("/auth/register", methods=["POST"])
def register():
    new_user = request.get_json()
    response = auth.register_user(new_user, db_ctx)
    return response


@app.route("/auth/login", methods=["POST"])
def login():
    login_details = request.get_json()
    response = auth.login_user(login_details, db_ctx)
    return response


@app.route("/auth/verify-user")
@jwt_required(optional=True)
def verify_user():
    current_user = get_jwt_identity()
    response = auth.verify_user(current_user)
    return response


@app.route("/token/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    current_jti = get_jwt()["jti"]
    response = auth.refresh_token(current_user, current_jti, db_ctx)
    return response


@app.route("/token/logout", methods=["POST"])
@jwt_required(refresh=True)
def logout():
    current_user = get_jwt()
    response = auth.logout_user(current_user, db_ctx)
    return response
