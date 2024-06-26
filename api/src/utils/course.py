from flask import jsonify
from typing import Dict, Tuple
from http import HTTPStatus as HTTP
from datetime import datetime, timezone
from bson.json_util import dumps
from bson.objectid import ObjectId
from src.utils.mongo_context import MongoContext
from src.constants import COURSES_COLLECTION, USERS_COLLECTION
from src.utils.request_util import corsify_response
from pprint import pprint


def _get_db(ctx: MongoContext):
    return ctx.mongo.db


def get_complete_questions(username: str, course_id: str, db_ctx: MongoContext) -> Tuple[Dict, int]:
    users_col = _get_db(db_ctx)[USERS_COLLECTION]
    query = {"username": username,
             "registered_courses._id": ObjectId(course_id)}
    projection = {"registered_courses.$": 1}
    doc = users_col.find_one(query, projection)

    if doc is None:
        response = corsify_response(
            jsonify(msg="could not find registered course")), HTTP.NOT_FOUND.value
        return response

    pprint(doc["registered_courses"][0]["complete_questions"])
    response = corsify_response(
        jsonify(complete_questions=doc["registered_courses"][0]["complete_questions"]))
    return response, HTTP.OK.value


def add_correct_answer(username: str, course_id: str, question_num: int, db_ctx: MongoContext) -> Tuple[Dict, int]:
    users_col = _get_db(db_ctx)[USERS_COLLECTION]
    query = {"username": username}
    # Push the new value to "arr"
    update = {
        "$addToSet": {"registered_courses.$[elem].complete_questions": question_num}}
    array_filters = [{"elem._id": ObjectId(course_id)}]
    result = users_col.update_one(query, update, array_filters=array_filters)

    if result.modified_count == 1:
        response = corsify_response(jsonify(msg="Correct answer saved"))
        return response, HTTP.OK.value
    else:
        response = corsify_response(
            jsonify(msg="could not update correct questions"))
        return response, HTTP.SERVICE_UNAVAILABLE.value


def get_registered_course(username: str, course_id: str, db_ctx: MongoContext) -> Tuple[Dict, int]:
    users_col = _get_db(db_ctx)[USERS_COLLECTION]
    courses_col = _get_db(db_ctx)[COURSES_COLLECTION]

    user_doc = users_col.find_one({"username": username})
    if user_doc is None:
        response = corsify_response(
            jsonify(msg="Unable to get course; user not found"))
        return response, HTTP.UNAUTHORIZED.value

    course_doc = courses_col.find_one({"_id": ObjectId(course_id)})
    if course_doc is None:
        response = corsify_response(
            jsonify(msg="Unable to get course; course not found"))
        return response, HTTP.NOT_FOUND.value
    response = jsonify(course=dumps(course_doc))
    response = corsify_response(response)
    return response, HTTP.OK.value


def get_registered_courses(username: str, db_ctx: MongoContext) -> Tuple[Dict, int]:
    users_col = _get_db(db_ctx)[USERS_COLLECTION]
    doc = users_col.find_one({"username": username})

    if doc is None:
        response = jsonify(msg="Unable to get courses; user not found")
        response = corsify_response(response)
        return response, HTTP.UNAUTHORIZED.value
    if "registered_courses" not in doc:
        response = corsify_response(jsonify(courses="[]")), HTTP.OK.value
        return response

    courses = doc["registered_courses"]
    response = jsonify(courses=dumps(courses))
    response = corsify_response(response)
    return response, HTTP.OK.value


def get_available_courses(db_ctx: MongoContext, next_cursor: str = None) -> Tuple[Dict, int]:
    # this has been setup to use cursor pagination for infinite scrolling effects. This has not been fully implemented yet, but can be in the future
    courses_col = _get_db(db_ctx)[COURSES_COLLECTION]
    if next_cursor is None:
        query = {"private": False}
    else:
        query = {"private": False, "_id": {"$gt": next_cursor}}
    # commented out because the limit is for cursor pagination
    # cursor = courses_col.find(query, limit=10, sort={"date": -1})
    cursor = courses_col.find(query, sort={"date": -1})

    if cursor is None:
        response = corsify_response(
            jsonify(msg="Unable to get available courses"))
        return response, HTTP.SERVICE_UNAVAILABLE.value

    courses = list(cursor)
    courses = dumps(courses)
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


def register_course(username: str, course_id: str, db_ctx: MongoContext) -> Tuple[Dict, int]:
    users_col = _get_db(db_ctx)[USERS_COLLECTION]
    courses_col = _get_db(db_ctx)[COURSES_COLLECTION]
    user_doc = users_col.find_one({"username": username})
    course_doc = courses_col.find_one({"_id": ObjectId(course_id)}, {
                                      "_id": 1, "name": 1, "binary": 1})

    if user_doc is None:
        result = corsify_response(jsonify(
            msg="Could not find user account")), HTTP.NETWORK_AUTHENTICATION_REQUIRED.value
        return result
    if course_doc is None:
        result = corsify_response(
            jsonify(msg="Could not find course to register")), HTTP.NOT_FOUND.value
        return result

    if "registered_courses" in user_doc:
        if course_id in user_doc["registered_courses"]:
            result = corsify_response(
                jsonify(msg="Already registered for course")), HTTP.OK.value
            return result

    course_doc["complete_questions"] = []
    result = users_col.update_one(
        {"username": username},
        {"$push": {"registered_courses": course_doc}}
    )

    if result.modified_count > 0:
        result = corsify_response(
            jsonify(msg="Successfully registered course")), HTTP.OK.value
    else:
        result = corsify_response(
            jsonify(msg="Failed to register course")), HTTP.SERVICE_UNAVAILABLE.value
    return result


def unregister_course(username: str, course_id: str, db_ctx: MongoContext) -> Tuple[Dict, int]:
    users_col = _get_db(db_ctx)[USERS_COLLECTION]
    user_doc = users_col.find_one({"username": username})
    if user_doc is None:
        result = corsify_response(jsonify(
            msg="Could not find user account")), HTTP.NETWORK_AUTHENTICATION_REQUIRED.value
        return result

    registered = False
    for registered_course in user_doc["registered_courses"]:
        if registered_course["_id"] == ObjectId(course_id):
            registered = True

    if not registered:
        result = corsify_response(
            jsonify(msg="Not registered for course")), HTTP.OK.value
        return result

    result = users_col.update_one({"username": username}, {
        "$pull": {"registered_courses": {"_id": ObjectId(course_id)}}})
    if result.modified_count == 1:
        response = corsify_response(
            jsonify(msg="unregistered course")), HTTP.OK.value
    else:
        response = compile(
            jsonify(msg="failed to unregister for course")), HTTP.SERVICE_UNAVAILABLE.value
    return response
