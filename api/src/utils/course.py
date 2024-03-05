from flask import jsonify
from typing import Dict, Tuple
from pprint import pprint
from http import HTTPStatus as HTTP
from datetime import datetime, timezone
from bson.json_util import dumps, loads
from src.utils.mongo_context import MongoContext
from src.constants import COURSES_COLLECTION, USERS_COLLECTION
from src.utils.request_util import corsify_response


def _get_db(ctx: MongoContext):
    return ctx.mongo.db


def get_user_courses(username: str, db_ctx: MongoContext) -> Tuple[Dict, int]:
    users_col = _get_db(db_ctx)[USERS_COLLECTION]
    doc = users_col.find_one({"username": username})

    if doc is None:
        response = jsonify(msg="Unable to get courses; user not found")
        response = corsify_response(response)
        return response, HTTP.UNAUTHORIZED.value

    courses = doc["courses"]
    response = jsonify(courses=courses)
    response = corsify_response(response)
    return response, HTTP.OK.value


def get_available_courses(db_ctx: MongoContext, next_cursor: str = None) -> Tuple[Dict, int]:
    courses_col = _get_db(db_ctx)[COURSES_COLLECTION]
    if next_cursor is None:
        query = {"private": False}
    else:
        query = {"private": False, "_id": {"$gt": next_cursor}}
    cursor = courses_col.find(query, limit=10, sort={"date": -1})

    if cursor is None:
        response = corsify_response(
            jsonify(msg="Unable to get available courses"))
        return response, HTTP.SERVICE_UNAVAILABLE.value

    courses = list(cursor)
    courses = dumps(courses)
    pprint(courses)
    response = corsify_response(jsonify(courses=courses))
    return response, HTTP.OK.value


def insert_course(username: str, course: Dict, db_ctx: MongoContext) -> Tuple[Dict, int]:
    courses_col = _get_db(db_ctx)[COURSES_COLLECTION]
    course["author"] = username
    course["date"] = datetime.now(tz=timezone.utc)
    doc = courses_col.insert_one(course)

    if doc is None:
        response = corsify_response(jsonify(msg="unable to insert course"))
        return response, HTTP.SERVICE_UNAVAILABLE.value

    response = corsify_response(jsonify(msg="course inserted"))
    return response, HTTP.OK.value