from models.model import Quiz
from flasgger import swag_from
from flask_login import login_required
from controllers.decorator import role_required
from flask import request, render_template, Blueprint, session, flash

quiz = Blueprint("quiz", __name__, url_prefix="/admin/quiz")

@quiz.route("/", methods=['GET'])
@login_required
@role_required("admin")
@swag_from({
    "tags": ['Quiz'],
    "summary": "Retrieve all quizzes with filtering, pagination and sorting",
    "description": "This endpoint retrieves all quizzes with filtering, pagination and sorting",
    "parameters": [
        {
            'name':'skip',
            'in':'query',
            'required':False,
            "type":'integer',
            'description':'Number of records to skip (default is 0)',
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
            'example': '{"chapter_id": "C001"}'
        }
    ],
    'responses': {
        200: {
            'description': 'A list of subjects retrieved successfully',
            'schema': {
                'type': "object",
                "properties":{
                    'rows':{
                        'type':"array",
                        "items":{
                            'type':"object",
                            "properties":{
                                'id': {'type': 'string'},
                                'chapter_id': {'type':'string'},
                                'date_of_quiz': {'type':'date'},
                                'time_duration': {'type':'integer'},
                                'remarks':{'type':'string'},
                                'number_of_questions': {'type':'integer'},
                                'user_id': {'type':'string'},
                                'total_marks': {'type':'integer'},
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
                        'id': 'eEWR',
                        'chapter_id': 'english',
                        'time_duration': 200,
                        'remarks':"fdawegre",
                        'number_of_questions': 10,
                        'user_id': 'USDF22',
                        'total_marks': 20,
                        'date_of_quiz': '2021-01-01T00:00:00Z',
                        'created_at': '2021-01-01T00:00:00Z',
                        'updated_at': '2021-01-01T00:00:00Z'
                    }
                    ],
                    'total_rows':1,
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
@swag_from({})
def admin_quiz():
    skip = int(request.args.get("skip", 0))
    take = int(request.args.get("take",25))
    where = request.args.get("where", "{}")
    order = request.args.get("order", "created_at")
    try:
        quizzes = Quiz.query.filter_by(**where).order_by(order).limit(take).offset(skip).all()
        total_quiz=Quiz.query.all()
        return render_template("admin_quiz.html", rows=quizzes, total_rows=len(total_quiz))        
    except Exception as e:
        flash("An error occurred while fetching subjects.", 'danger')
        return render_template("admin_quiz.html", rows=[], total_rows=0)        