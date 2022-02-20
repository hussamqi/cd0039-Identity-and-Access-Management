import os
from flask import Flask, request, jsonify, abort, Response
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES

@app.route("/drinks")
def retrieve_categories():
    drinks = Drink.query.all()
    if not drinks:
        abort(404)
    drinks_list = [drink.short() for drink in drinks]
    return jsonify({'success': True, "drinks": drinks_list})


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def images(jwt):
    drinks = Drink.query.all()
    if not drinks:
        abort(404)
    drinks_list = [drink.long() for drink in drinks]
    return jsonify({'success': True, "drinks": drinks_list})


@app.route("/drinks", methods=["POST"])
@requires_auth('post:drinks')
def create_drink(jwt):
    body = request.get_json()
    try:
        title = body.get("title")
        recipe = body.get("recipe")
        if isinstance(recipe, dict):
            recipe = [recipe]
        recipe = json.dumps(recipe)
        print('====')
        print(recipe)
        print('=====')
        drink_object = Drink(title=title, recipe=recipe)
        drink_object.insert()
        drinks_list = [drink_object.long()]
        return jsonify({'success': True, "drinks": drinks_list})
    except:
        abort(422)

@app.route("/drinks/<int:drink_id>", methods=["PATCH"])
@requires_auth('patch:drinks')
def update_drink(jwt, drink_id:int):
    body = request.get_json()
    try:
        drink = Drink.query.filter_by(id=drink_id).one_or_none()
        if not drink:
            abort(404)
        drink.title = body.get("title")
        drink.recipe = json.dumps(body.get("recipe"))
        drink.update()
        drinks_list = [drink.long()]
        return jsonify({'success': True, "drinks": drinks_list})
    except:
        abort(422)


@app.route("/drinks/<int:drink_id>", methods=["DELETE"])
@requires_auth('delete:drinks')
def delete_drink(jwt, drink_id:int):
    try:
        drink = Drink.query.filter_by(id=drink_id).one_or_none()
        if not drink:
            abort(404)
        drink.delete()
        return jsonify({'success': True, "delete": drink_id})
    except:
        abort(422)

# Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(400)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400



@app.errorhandler(405)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "method not allowed"
    }), 405


@app.errorhandler(500)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal server error"
    }), 500

@app.errorhandler(AuthError)
def handle_auth_error(ex: AuthError) -> Response:
    """
    serializes the given AuthError as json and sets the response status code accordingly.
    :param ex: an auth error
    :return: json serialized ex response
    """
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response
