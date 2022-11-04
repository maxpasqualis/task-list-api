from app import db
from app.models.task import Task
from flask import Blueprint, jsonify, abort, make_response, request

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

def validate_model(cls, model_id):
    try:
        model_id = int(model_id)
    except:
        abort(make_response({"ERROR":f"{cls.__name__} {model_id} invalid"}, 400))

    model = cls.query.get(model_id)
    if not model:
        abort(make_response({"ERROR":f"No {cls.__name__} with ID {model_id} in database"}, 404))

    return model

@tasks_bp.route("", methods=["POST"])
# Creates a new task and returns it as a json
def create_new_task():
    request_body = request.get_json()
    new_task = Task.from_dict(request_body)

    db.session.add(new_task)
    db.session.commit()
    return {"task": new_task.as_dict()}, 201

@tasks_bp.route("", methods=["GET"])
# Get every task in the task list
def get_all_tasks():
    tasks = Task.query.all()
    tasks_response = []
    for task in tasks:
        tasks_response.append(task.as_dict())

    return jsonify(tasks_response)

@tasks_bp.route("/<task_id>", methods=["GET"])
# Get one specific task from the task list
def get_one_task(task_id):
    task = validate_model(Task, task_id)
    return {"task": task.as_dict()}
