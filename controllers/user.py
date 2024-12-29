from models import db
from models.model import User, Score, Quiz
from datetime import datetime,date
from config import admin_credentials
from flask_login import login_required
from flasgger import Swagger, swag_from
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify


user = Blueprint('user', __name__, url_prefix='/user')

@user.route("/get_all_users", methods=['POST'])
@login_required
@swag_from({
    'tags':['User'],
    'summary':'Retrieve all users with filtering, pagination and sorting',
    'description':'This endpoint retrieves all users with filtering, pagination and sorting',
'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'search': {
                        'type': 'object',
                        'description': 'Search filters for users',
                        'example': {}
                    },
                    'where': {
                        'type': 'object',
                        'description': 'Conditions to filter the users',
                        'example': {}
                    },
                    'order': {
                        'type': 'object',
                        'description': 'Sorting options for the query',
                        'example': {}
                    },
                    'skip': {
                        'type': 'integer',
                        'description': 'Number of records to skip',
                        'example': 0
                    },
                    'take': {
                        'type': 'integer',
                        'description': 'Number of records to retrieve',
                        'example': 25
                    }
                },
                'required': ['skip', 'take']
            }
        }
    ],
    'responses': {
    200: {
        'description': 'A list of users retrieved successfully',
        'schema': {
            'type': 'object',
            'properties': {
                'rows': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer'},
                            'username': {'type': 'string'},
                            'full_name': {'type': 'string'},
                            'qualification':{'type':'string'},
                            'dob':{'type':'string'},
                            'score':{'type':'integer'},
                            'quiz_played':{'type':'integer'},
                            'user_type' : {'type':'string'},
                            'created_at': {'type': 'string'},
                            'updated_at': {'type': 'string'}
                        }
                    }
                },
                'total_rows': {
                    'type': 'integer',
                    'description': 'Total number of rows'
                }
            },
            'example': {
                'rows': [
                    {
                        'id': 1,
                        'username': 'johndoe@example.com',
                        'full_name': 'johndoe',
                        'qualification':'Btech',
                        'dob':'2021-01-01T00:00:00Z',
                        'score':100,
                        'quiz_played':1,
                        'user_type': 'admin',
                        'created_at': '2021-01-01T00:00:00Z',
                        'updated_at': '2021-01-01T00:00:00Z'
                    }
                ],
                'total_rows': 1
                }
            }
        },
        401: {
            'description': 'Unauthorized access',
            'examples': {
                'application/json': {'message': 'Login required'}
            }
        },
        500: {
            'description': 'Internal Server Error',
            'examples': {
                'application/json': {'message': 'An error occurred'}
            }
        }
    }
})
def getUsers():
    data = request.get_json()
    order = data['order']
    skip = data['skip']
    take = data['take']
    where = data['where']
    try:
        users = User.query.filter_by(**where).order_by(**order).limit(take).offset(skip).all()
        users_list = []
        for user in users:
            score_of_user = Score.query.filter_by(user_id=user.id).all()
            total_score = 0
            quiz_played = 0
            quize_of_user = Score.query.filter_by(user_id=user.id).all()
            for quiz in quize_of_user:
                quiz_played += 1
            for score in score_of_user:
                total_score += score.total_scored
            users_list.append({
                'id': user.id,
                'username': user.username,
                'full_name': user.full_name,
                'qualification': user.qualification,
                'score': total_score,
                'quiz_played': quiz_played,
                'dob': user.dob,
                'user_type': user.user_type,
                'created_at': user.created_at,
                'updated_at': user.updated_at
            })
        return jsonify({'rows': users_list, 'total_rows': len(users_list)})    
    except Exception as e:
        return jsonify({'message': 'An error occurred'}), 500