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
# db_drop_and_create_all()
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

# CORS Headers
# @app.after_request
# def after_request(response):
#     response.headers.add(
#         "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
#     )
#     response.headers.add(
#         "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
#     )
#     return response


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

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
     where drink an array containing  only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks", methods=["POST"])
@requires_auth('post:drinks')
def create_drink(jwt):
    body = request.get_json()
    try:
        title = body.get("title")
        recipe = json.dumps(body.get("recipe"))
        drink_object = Drink(title=title, recipe=recipe)
        drink_object.insert()
        drinks_list = [drink_object.long()]
        return jsonify({'success': True, "drinks": drinks_list})
    except:
        abort(422)
'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
