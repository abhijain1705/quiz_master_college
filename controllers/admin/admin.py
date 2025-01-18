#controllers/admin.py
from flasgger import swag_from
from models.model import User, Score
from controllers.decorator import role_required
from flask_login import current_user, login_required
from flask import Blueprint, render_template, session, flash, request

admin= Blueprint("admin", __name__, url_prefix="/admin")

# /admin/subject?skip=0&take=25&order=created_at&where={}
@admin.route("/", methods=['GET'])
@login_required
@role_required("admin")
@swag_from({
    'tags': ['Admin'],
    'summary': 'Retrieve all users with filtering, pagination and sorting',
    'description': 'This endpoint retrieves all users with filtering, pagination and sorting',
    'parameters': [
        {
            'name': 'skip',
            'in': 'query',
            'required': False,
            'type': 'integer',
            'description': 'Number of records to skip (default is 0)',
            'example': 0
        },
        {
            'name': 'take',
            'in': 'query',
            'required': False,
            'type': 'integer',
            'description': 'Number of records to retrieve (default is 25)',
            'example': 25
        },
        {
            'name': 'order',
            'in': 'query',
            'required': False,
            'type': 'string',
            'description': 'Sorting options for the query (default is "created_at")',
            'example': 'created_at'
        },
        {
            'name': 'where',
            'in': 'query',
            'required': False,
            'type': 'string',
            'description': 'Filter conditions for the query as a JSON string (default is empty)',
            'example': '{"user_type": "admin"}'
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
                                'id': {'type': 'string'},
                                'email': {'type': 'string'},
                                'full_name': {'type': 'string'},
                                'qualification': {'type': 'string'},
                                'dob': {'type': 'string'},
                                'score': {'type': 'integer'},
                                'quiz_played': {'type': 'integer'},
                                'user_type': {'type': 'string'},
                                'created_at': {'type': 'string'},
                                'updated_at': {'type': 'string'}
                            }
                        }
                    },
                    'total_rows': {
                        'type': 'integer',
                        'description': 'Total number of rows'
                    },
                    'skip': {
                        'type': 'integer',
                        "description": "current skipped rows"
                    },
                    'take':{
                        'type':'integer',
                        "description": 'current page size'
                    },
                    'current_page':{
                        'type':'integer',
                        "description":"current page number starts from 0"
                    },
                    'has_next':{
                        'type':'boolean',
                        'description':'if new page is available or not'
                    },
                    'nxt_skip': {
                        'type': 'integer',
                        "description": "next skipped rows"
                    },
                },
                'example': {
                    'rows': [
                        {
                            'id': 'evrev',
                            'email': 'johndoe@example.com',
                            'full_name': 'johndoe',
                            'qualification': 'Btech',
                            'dob': '2021-01-01T00:00:00Z',
                            'score': 100,
                            'quiz_played': 1,
                            'user_type': 'admin',
                            'created_at': '2021-01-01T00:00:00Z',
                            'updated_at': '2021-01-01T00:00:00Z'
                        }
                    ],
                    'total_rows': 1,
                    'current_page':0,
                    "has_next": False,
                    "nxt_skip": None,
                    "take":25,
                    "skip":0
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
def admin_home():
    skip = int(request.args.get('skip', 0))
    take = int(request.args.get('take', 25))
    order = request.args.get('order', 'created_at')
    where = request.args.get('where', '{}')
    try:
        where = eval(where)
        users = User.query.filter_by(**where).order_by(order).limit(take).offset(skip).all()
        total_users = User.query.all()
        users_list = []
        for user in users:
            score_of_user = Score.query.filter_by(user_id=user.id).all()
            total_score = 0
            quiz_played = 0
            for quiz in score_of_user:
                quiz_played += 1
                total_score += quiz.total_scored
            users_list.append({
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'qualification': user.qualification,
                'score': total_score,
                'quiz_played': quiz_played,
                'dob': user.dob,
                'user_type': user.user_type,
                'created_at': user.created_at,
                'updated_at': user.updated_at
            })
        return render_template("admin.html", rows=users_list, total_rows=len(total_users))
    except Exception as e:
        flash("An error occurred while fetching users.", 'danger')
        return render_template("admin.html", rows=[], total_rows=0)    