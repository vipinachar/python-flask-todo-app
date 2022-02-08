from wsgiref.simple_server import make_server
from flask import Flask, request, make_response, jsonify
import logging as logger 
from flask_sqlalchemy import SQLAlchemy
import math
import pprint

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.sqlite'

db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    content = db.Column(db.Text)
    completed = db.Column(db.Boolean, default=False)

@app.route("/task", methods=['POST'])
def create_task():
    data = request.get_json()
    new_task = Task(name=data['name'], content=data['content'])
    db.session.add(new_task)
    db.session.commit()
    return make_response(jsonify("Task has been added successfully"), 201)

@app.route("/", methods=['GET'])
def get_all_taks():
    current_page = request.args.get('current_page')
    page_size = request.args.get('page_size')
    filters = request.args.get('filters')
    
    if filters == "all":
        response = Task.query.paginate(int(current_page), int(page_size), False)
    elif filters == "completed":
        response = Task.query.filter_by(completed=True).paginate(int(current_page), int(page_size), False)
    elif filters == "not_completed":
        response = Task.query.filter_by(completed=False).paginate(int(current_page), int(page_size), False)
    else:
        return make_response(jsonify('Incorrecct filter'), 400)
    total_tasks = response.total 
    response = response.items

    output = []
    for task in response:
        task_dict = {}
        task_dict['id'] = task.id
        task_dict['name'] = task.name
        task_dict['content'] = task.content
        task_dict['completed'] = task.completed
        output.append(task_dict)
    
    resp = {
        'total' : total_tasks,
        'total_pages': math.ceil(total_tasks/int(page_size)),
        'current_page' : int(current_page),
        'page_size' : int(page_size),
        'tasks':output
    }
    
    return make_response(jsonify(resp),200)

@app.route("/task/<int:id>",methods=["PUT"])
def update_task(id):
    data = request.get_json() 
    name = data['name']
    content = data['content']
    completed = data['completed']
    task = Task.query.filter_by(id=id).first()
    if not task:
        return make_response(jsonify("Task with ID does not exist"), 400)
    else:
        task.name = name 
        task.completed = completed 
        task.content = content 
        db.session.commit()
        return make_response(jsonify("Data updated"), 200)

@app.route("/task/<id>", methods=["GET"])
def get_task(id):
    task = Task.query.filter_by(id=id).first() 
    if not task:
        return make_response(jsonify("Task with ID does not exist"), 400)
    print(task)
    response = {
        "id": task.id,
        "name": task.name,
        "content": task.content,
        "completed": task.completed,
    }
    return make_response(jsonify(response), 200)

@app.route("/task/delete/<id>", methods=["DELETE"])
def delete_task(id):
    task = Task.query.filter_by(id=id).first()
    if not task:
        return make_response(jsonify("Task not found") , 400)
    db.session.delete(task)
    db.session.commit()
    return make_response(jsonify("task deleted"), 200)
    
if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)