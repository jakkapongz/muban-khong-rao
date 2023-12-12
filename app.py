import hashlib
import json
from datetime import timedelta, datetime

from flask import Flask, render_template, request, jsonify, make_response
from flask_jwt_extended import JWTManager, create_access_token, set_access_cookies, unset_access_cookies

from auth_middleware import token_required
from db_connector import DBConnector

app = Flask(__name__)
db_connector = DBConnector(app)
# If true this will only allow the cookies that contain your JWTs to be sent
# over https. In production, this should always be set to True
app.config["JWT_COOKIE_SECURE"] = False
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this in your code!
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=30)
app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this "super secret" with something else!
md5_salt = 'mubankhongrao-private-salt'
jwt = JWTManager(app)


def get_request(request_form):
    fields = []
    values = []

    for request_field in request_form:
        request_value = request_form[request_field]
        if request_value is not None and len(request_value) > 0:
            values.append(request_value)
            fields.append(request_field)

    return fields, values


@app.route('/main', methods=['GET'])
@token_required
def go_index_page(current_user):
    visitors = db_connector.get_visitors_today(current_user['user_id'], current_user['role_name'])

    if visitors is not None:
        visitors_json = json.loads(visitors)

    problem_reports = db_connector.get_problem_reports_today()

    if problem_reports is not None:
        problem_reports_json = json.loads(problem_reports)

    patrolling_reports = db_connector.get_patrolling_reports_today()

    if patrolling_reports is not None:
        patrolling_reports_json = json.loads(patrolling_reports)

    return render_template('main.html',
                           page_name='หน้าแรก',
                           visitors=visitors_json,
                           problem_reports=problem_reports_json,
                           patrolling_reports=patrolling_reports_json,
                           current_user=current_user
                           )


@app.route('/', methods=['GET'])
@app.route('/login', methods=['GET'])
def go_login_page():
    return render_template('login.html')


@app.route('/visitors', methods=['GET'])
@token_required
def go_visitors_page(current_user):  # put application's code here
    visitors = db_connector.get_visitors(current_user['user_id'], current_user['role_name'])

    households = db_connector.get_households()

    if households is not None:
        households_json = json.loads(households)

    if visitors is not None:
        visitors_json = json.loads(visitors)

    return render_template('visitor.html',
                           page_name='ผู้มาติดต่อ',
                           visitors=visitors_json,
                           households=households_json,
                           current_user=current_user
                           )


@app.route('/problem-reports', methods=['GET'])
@token_required
def go_problem_reports_page(current_user):
    problem_reports = db_connector.get_problem_reports()

    problem_categories = db_connector.get_problem_categories()

    if problem_categories is not None:
        problem_categories_json = json.loads(problem_categories)

    if problem_reports is not None:
        problem_reports_json = json.loads(problem_reports)

    return render_template('problem_report.html',
                           page_name='แจ้งปัญหา',
                           problem_reports=problem_reports_json,
                           problem_categories=problem_categories_json,
                           current_user=current_user
                           )


@app.route('/patrolling-reports', methods=['GET'])
@token_required
def go_patrolling_reports_page(current_user):
    patrolling_reports = db_connector.get_patrolling_reports()

    if patrolling_reports is not None:
        patrolling_reports_json = json.loads(patrolling_reports)
    else:
        patrolling_reports_json = []

    return render_template('patrolling_report.html',
                           page_name='การเดินตรวจตรา',
                           patrolling_reports=patrolling_reports_json,
                           current_user=current_user
                           )


@app.route('/api/visitor', methods=['POST'])
@token_required
def api_add_visitor(current_user):
    try:
        fields, values = get_request(request.form)

        fields.append('visitor_status')
        values.append('VISITING')

        db_connector.add_data('visitors', fields, values, current_user['username'])

        data = {'status': 'success'}

        return jsonify(data), 201
    except Exception as e:
        return jsonify({
            "message": "เกิดข้อผิดพลาด",
            "error": str(e),
            "data": None
        }), 500


@app.route('/api/visitor', methods=['PUT'])
@token_required
def api_update_visitor(current_user):
    try:
        fields, values = get_request(request.form)

        db_connector.update_data('visitors', fields, values, current_user['username'])

        data = {'status': 'success'}

        return data, 200
    except Exception as e:
        return jsonify({
            "message": "เกิดข้อผิดพลาด",
            "error": str(e),
            "data": None
        }), 500


@app.route('/api/problem-report', methods=['POST'])
@token_required
def api_add_problem_report(current_user):
    try:
        fields, values = get_request(request.form)

        fields.append('problem_report_status')
        values.append('INIT')

        db_connector.add_data('problem_reports', fields, values, current_user['username'])

        data = {'status': 'success'}

        return jsonify(data), 201
    except Exception as e:
        return jsonify({
            "message": "เกิดข้อผิดพลาด",
            "error": str(e),
            "data": None
        }), 500


@app.route('/api/problem-report', methods=['PUT'])
@token_required
def api_update_problem_report(current_user):
    try:
        fields, values = get_request(request.form)

        db_connector.update_data('problem_reports', fields, values, current_user['username'])

        data = {'status': 'success'}

        return data, 200
    except Exception as e:
        return jsonify({
            "message": "เกิดข้อผิดพลาด",
            "error": str(e),
            "data": None
        }), 500


@app.route('/api/patrolling-report', methods=['POST'])
@token_required
def api_add_patrolling_report(current_user):
    try:

        fields, values = get_request(request.form)

        db_connector.add_data('patrolling_reports', fields, values, current_user['username'])

        data = {'status': 'success'}

        return jsonify(data), 201
    except Exception as e:
        return jsonify({
            "message": "เกิดข้อผิดพลาด",
            "error": str(e),
            "data": None
        }), 500


@app.route('/api/login', methods=['POST'])
def api_login():
    try:
        username = request.form.get('username')
        password = request.form.get('password')

        h = hashlib.md5(usedforsecurity=True)
        h.update('{0}{1}{2}'.format(username, md5_salt, password).encode('utf-8'))
        h.hexdigest()

        user = db_connector.login(username, h.hexdigest())

        if user is not None:
            user_json = json.loads(user)
            access_token = create_access_token(identity={
                'user_id': user_json['user_id'],
                'username': user_json['username'],
                'role': user_json['role_name']
            })
            response = jsonify({"msg": "login successful", "status": "success"})
            set_access_cookies(response, access_token)
            return response, 200
    except Exception as e:
        return jsonify({
            "message": "เกิดข้อผิดพลาด",
            "error": str(e),
            "data": None
        }), 500

    response = jsonify({"msg": "login failed", "status": "failed"})
    return response, 400


@app.route('/api/logout', methods=['DELETE'])
@token_required
def api_logout(current_user):
    response = jsonify({"msg": "logout successful", "status": "success"})
    unset_access_cookies(response)
    return response, 200


if __name__ == '__main__':
    app.run()
