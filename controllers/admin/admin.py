#controllers/admin.py
from sqlalchemy import desc
from flasgger import swag_from
from models.model import User, Score
from controllers.decorator import role_required
from flask_login import current_user, login_required
from flask import Blueprint, render_template, session, flash, request
from controllers.admin.admin_subject import validate_fields, flash_and_redirect

admin= Blueprint("admin", __name__, url_prefix="/admin")

@admin.route("/", methods=['GET'])
@login_required
@role_required("admin")
@swag_from({
    'tags': ['Admin'],
    'summary': 'Fetch users with filters, pagination, and sorting',
    'description': 'This endpoint fetches a list of users, with options for filtering, pagination, and sorting.',
    'parameters': [
        {
            'name': 'skip',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'description': 'The number of records to skip (default: 0)',
            'example': 0
        },
        {
            'name': 'take',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'description': 'The number of records to retrieve (default: 25)',
            'example': 25
        },
        {
            'name': 'where',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Filter conditions as a JSON string (default: empty)',
            'example': '{"user_type": "admin"}'
        }
    ],
    'responses': {
        200: {
            'description': 'User list retrieved successfully',
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
                        'description': 'Total number of users'
                    },
                    'skip': {
                        'type': 'integer',
                        'description': 'Number of skipped records'
                    },
                    'take': {
                        'type': 'integer',
                        'description': 'Number of records per page'
                    }
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
                    'skip': 0,
                    'take': 25
                }
            }
        },
        401: {
            'description': 'Unauthorized',
            'examples': {
                'application/json': {'message': 'Login required'}
            }
        },
        500: {
            'description': 'Server error',
            'examples': {
                'application/json': {'message': 'An error occurred'}
            }
        }
    }
})
def admin_home():
    skip = int(request.args.get('skip', 0))
    take = int(request.args.get('take', 25))
    where = request.args.get('where', '{}')
    try:
        where = eval(where)  # Ensure this is safe; use `json.loads` if possible
        users = User.query.filter_by(**where).order_by(desc(User.created_at)).limit(take).offset(skip).all()
        total_users = User.query.count()
        
        users_list = []
        for user in users:
            score_of_user = Score.query.filter_by(user_id=user.id).all()
            total_score = sum(quiz.total_scored for quiz in score_of_user)
            quiz_played = len(score_of_user)

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

        return render_template("admin/admin.html", rows=users_list, total_rows=total_users)

    except Exception as e:
        return flash_and_redirect(f"An error occurred while fetching users: {e}", 'danger', url_for("admin_home"))
