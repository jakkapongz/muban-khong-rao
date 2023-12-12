import json

from dotenv import dotenv_values
from flask_mysqldb import MySQL


def parse_to_json_array(cur, resultsets):
    if resultsets is not None:
        row_headers = [row[0] for row in cur.description]
        json_data = []
        for result in resultsets:
            json_data.append(dict(zip(row_headers, result)))

        return json.dumps(json_data, default=str)

    return None


class DBConnector:

    def __init__(self, app):
        config = dotenv_values(".env")
        # Required
        app.config["MYSQL_USER"] = config['DB_USERNAME']
        app.config["MYSQL_PASSWORD"] = config['DB_PASSWORD']
        app.config["MYSQL_DB"] = config['DB_NAME']
        self.mysql = MySQL(app)

    def login(self, username, password):
        cur = self.mysql.connection.cursor()

        sql = ("select u.user_id, u.username,r.role_name from users u "
               " inner join user_roles r on u.role_id = r.role_id"
               " where u.username = \'{0}\' and password = \'{1}\'").format(username, password)

        cur.execute(sql)
        resultset = cur.fetchone()

        if resultset is not None:
            row_headers = [row[0] for row in cur.description]
            json_data = dict(zip(row_headers, resultset))
            return json.dumps(json_data, default=str)

        return None

    def get_user_by_id(self, user_id):
        cur = self.mysql.connection.cursor()

        sql = ("select u.user_id, u.username,r.role_name from users u "
               " inner join user_roles r on u.role_id = r.role_id"
               " where u.user_id = \'{0}\'").format(user_id)

        cur.execute(sql)
        resultset = cur.fetchone()

        if resultset is not None:
            row_headers = [row[0] for row in cur.description]
            json_data = dict(zip(row_headers, resultset))
            return json.dumps(json_data, default=str)

        return None

    def add_data(self, table, fields, values, username):
        comma = ""
        field_sql = ""

        for field in fields:
            field_sql += "{0}{1}".format(comma, field)
            comma = ","

        comma = ""
        value_sql = ""
        for value in values:
            value_sql += "{0}\'{1}\'".format(comma, value)
            comma = ","

        sql = ("insert into {0} ({1}, created_datetime, created_by, updated_datetime, updated_by) "
               "values ({2}, now(), \'{3}\', now(), \'{3}\')").format(table, field_sql, value_sql, username)

        cur = self.mysql.connection.cursor()
        cur.execute(sql)
        self.mysql.connection.commit()

    def update_data(self, table, fields, values, user_id):
        comma = ""
        update_sql = ""
        criteria_sql = ""

        for f, v in zip(fields, values):
            update_sql += "{0}{1}=\'{2}\'".format(comma, f, v)
            comma = ","

            if table == 'visitors' and f == "visitor_id":
                criteria_sql = "WHERE visitor_id = \'{0}\'".format(v)
            elif table == 'problem_reports' and f == "problem_report_id":
                criteria_sql = "WHERE problem_report_id = \'{0}\'".format(v)

        sql = ("update {0} set {1}, updated_datetime=now(), updated_by=\'{2}\' {3}"
               .format(table, update_sql, user_id, criteria_sql))

        cur = self.mysql.connection.cursor()
        cur.execute(sql)
        self.mysql.connection.commit()

    def get_visitors(self, user_id, role):
        cur = self.mysql.connection.cursor()

        sql = (
            "select v.visitor_id,h.household_name as household_no, v.visitor_name,v.visitor_description,v.vehicle_license_plate,"
            " v.visitor_image,v.visitor_status, v.visitor_remark, v.created_by, v.created_datetime, v.updated_by, v.updated_datetime "
            " from visitors v "
            " left join users u"
            " on u.household_id = v.household_id"
            " left join households h"
            " on u.household_id = h.household_id WHERE v.created_datetime >= (now() - interval 30 day)")

        if role == 'VILLAGER':
            sql = "{0} AND u.user_id = {1}".format(sql, user_id)

        sql = "{0} ORDER BY v.updated_datetime DESC".format(sql)

        cur.execute(sql)
        resultsets = cur.fetchall()

        return parse_to_json_array(cur, resultsets)

    def get_visitors_today(self, user_id, role):
        cur = self.mysql.connection.cursor()

        sql = (
            "select v.visitor_id,h.household_name as household_no, v.visitor_name,v.visitor_description,v.vehicle_license_plate,"
            " v.visitor_image,v.visitor_status, v.visitor_remark, v.created_by, v.created_datetime, v.updated_by, v.updated_datetime "
            " from visitors v "
            " left join users u"
            " on u.household_id = v.household_id"
            " left join households h"
            " on u.household_id = h.household_id "
            " where DATE_FORMAT(v.created_datetime, '%Y-%m-%d') = DATE_FORMAT(now(), '%Y-%m-%d')"
            " and v.visitor_status = 'VISITING'")

        if role == 'VILLAGER':
            sql = "{0} AND u.user_id = {1}".format(sql, user_id)

        sql = "{0} ORDER BY v.updated_datetime DESC".format(sql)

        cur.execute(sql)
        resultsets = cur.fetchall()

        return parse_to_json_array(cur, resultsets)

    def get_households(self):
        cur = self.mysql.connection.cursor()

        sql = "select household_id, household_name from households"

        cur.execute(sql)
        resultsets = cur.fetchall()

        return parse_to_json_array(cur, resultsets)

    def get_problem_categories(self):
        cur = self.mysql.connection.cursor()

        sql = "select problem_category_id, category_name from problem_categories"

        cur.execute(sql)
        resultsets = cur.fetchall()

        return parse_to_json_array(cur, resultsets)

    def get_problem_reports(self):
        cur = self.mysql.connection.cursor()

        sql = ("select pr.problem_report_id, pc.category_name, pr.problem_report_title, pr.problem_report_description, "
               "pr.problem_report_status, pr.problem_image, pr.problem_report_remark, pr.created_by, pr.created_datetime, pr.updated_by, "
               "pr.updated_datetime "
               "from problem_reports pr inner join problem_categories pc "
               "on pr.problem_category_id = pc.problem_category_id "
               "where pr.created_datetime >= (now() - interval 30 day) order by pr.created_datetime desc;")

        cur.execute(sql)
        resultsets = cur.fetchall()

        return parse_to_json_array(cur, resultsets)

    def get_problem_reports_today(self):
        cur = self.mysql.connection.cursor()

        sql = ("select pr.problem_report_id, pc.category_name, pr.problem_report_title, pr.problem_report_description, "
               "pr.problem_report_status, pr.problem_image, pr.created_by, pr.created_datetime, pr.updated_by, "
               "pr.updated_datetime "
               "from problem_reports pr inner join problem_categories pc "
               "on pr.problem_category_id = pc.problem_category_id "
               "where DATE_FORMAT(pr.created_datetime, '%Y-%m-%d') = DATE_FORMAT(now(), '%Y-%m-%d') order by pr.created_datetime desc;")

        cur.execute(sql)
        resultsets = cur.fetchall()

        return parse_to_json_array(cur, resultsets)

    def get_patrolling_reports(self):
        cur = self.mysql.connection.cursor()

        sql = ("select * from patrolling_reports pr where pr.created_datetime >= (now() - interval 30 day) "
               "order by pr.created_datetime desc;")

        cur.execute(sql)
        resultsets = cur.fetchall()

        return parse_to_json_array(cur, resultsets)

    def get_patrolling_reports_today(self):
        cur = self.mysql.connection.cursor()

        sql = ("select * from patrolling_reports pr where DATE_FORMAT(pr.created_datetime, '%Y-%m-%d') = DATE_FORMAT(now(), '%Y-%m-%d') "
               "order by pr.created_datetime desc;")

        cur.execute(sql)
        resultsets = cur.fetchall()

        return parse_to_json_array(cur, resultsets)