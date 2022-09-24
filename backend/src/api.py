import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


db_drop_and_create_all()

# ROUTES
'''
    GET /drinks
'''
@app.route('/drinks')
def retrieve_drinks():
    try:
        drinks = Drink.query.all()
        
        return jsonify({
            "success": True,
            "drinks": [drink.short() for drink in drinks]
        }), 200
    except:
        abort(422)

'''
    GET /drinks-detail
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def retrieve_drinks_detail(payload):
    try:
        drinks = Drink.query.all()
        
        return jsonify({
            "success": True,
            "drinks": [drink.long() for drink in drinks]
        }), 200
    except:
        abort(422)

'''
    POST /drinks
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drinks(payload):
    body = request.get_json()
    new_title = body.get("title")
    new_recipe = json.dumps(body.get("recipe"))
    
    if new_title is None and new_recipe is None:
        abort(422)
    
    try:
        drink = Drink(title=new_title, recipe=new_recipe)
        drink.insert()
        
        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        }), 200
    except:
        abort(422)

'''
    PATCH /drinks/<id>
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drinks(payload, drink_id):
    body = request.get_json()
    
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    
    if drink is None:
        abort(404)
    
    if body.get("title"):
        drink.title = body.get("title")
    
    if body.get("recipe"):
        drink.recipe = json.dumps(body.get("recipe"))
    
    try:
        drink.update()
        
        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        }), 200
    except:
        abort(422)

'''
    DELETE /drinks/<id>
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload, drink_id):
    drink = Drink.query.get(drink_id)
    
    if drink is None:
        abort(404)
    
    try:
        drink.delete()
        
        return jsonify({
            "success": True,
            "delete": drink_id
        }), 200
    except:
        abort(422)

'''
Error Handling
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400
    
@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unauthorized"
    }), 401
    
@app.errorhandler(405)
def not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "method not allowed"
    }), 405
    
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "internal server error"
    }), 500

@app.errorhandler(AuthError)
def handle_auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code