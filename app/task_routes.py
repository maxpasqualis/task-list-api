from app import db
from app.models.task import Task
from .route_helpers import validate_model, send_slack_message
from flask import Blueprint, jsonify, abort, make_response, request
from datetime import datetime

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods=["POST"])
# Creates a new task and returns it as a json
def create_new_task():
    request_body = request.get_json()
    if "title" in request_body and "description" in request_body:
        new_task = Task.from_dict(request_body)

        db.session.add(new_task)
        db.session.commit()
        return {"task": new_task.as_dict()}, 201
    else:
        return {"details": "Invalid data"}, 400

@tasks_bp.route("", methods=["GET"])
# Get every task in the task list
def get_all_tasks():
    sort_param = request.args.get("sort")
    if sort_param == "desc":
        tasks = db.session.query(Task).order_by(Task.title.desc())
    elif sort_param == "asc":
        tasks = db.session.query(Task).order_by(Task.title.asc())
    else:
        tasks = Task.query.all()

    tasks_response = [task.as_dict() for task in tasks]
    return jsonify(tasks_response)

@tasks_bp.route("/<task_id>", methods=["GET"])
# Get one specific task from the task list
def get_one_task(task_id):
    task = validate_model(Task, task_id)
    return {"task": task.as_dict()}, 200

@tasks_bp.route("/<task_id>", methods=["PUT"])
# Updates specified task's name, description, and completion
def update_task(task_id):
    request_body = request.get_json()
    task = validate_model(Task, task_id)

    if "title" in request_body and "description" in request_body:
        task.title = request_body["title"]
        task.description = request_body["description"]
        
        db.session.commit()
        return {"task": task.as_dict()}, 200
    else:
        return {"details": "Invalid data"}, 404

@tasks_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = validate_model(Task, task_id)

    db.session.delete(task)
    db.session.commit()
    return {"details":f'Task {task_id} "{task.title}" successfully deleted'}, 200

@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def mark_task_complete(task_id):
    task = validate_model(Task, task_id)
    task.completed_at = datetime.now()
    task.is_complete = True
    slack_response = send_slack_message(f"Someone just completed the task {task.title}")
    db.session.commit()
    return {"task": task.as_dict()}, 200

@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def mark_task_incomplete(task_id):
    task = validate_model(Task, task_id)
    task.completed_at = None
    task.is_complete = False
    db.session.commit()
    return {"task": task.as_dict()}, 200
