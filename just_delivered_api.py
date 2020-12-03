from flask import Flask, request, render_template, url_for, redirect
from flask_restful import Resource, Api
from flask_mail import Mail, Message  # used for email
# used for serializer email and error handling
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
from flask_cors import CORS

from werkzeug.exceptions import BadRequest, NotFound

from dateutil.relativedelta import *
from decimal import Decimal
from datetime import datetime, date, timedelta
from hashlib import sha512
from math import ceil

import string
import decimal
import sys
import json
import pymysql
import requests

RDS_HOST = 'pm-mysqldb.cxjnrciilyjq.us-west-1.rds.amazonaws.com'
#RDS_HOST = 'localhost'
RDS_PORT = 3306
#RDS_USER = 'root'
RDS_USER = 'admin'
RDS_DB = 'just_delivered'

app = Flask(__name__)

# Allow cross-origin resource sharing
cors = CORS(app, resources={r'/api/*': {'origins': '*'}})

# Set this to false when deploying to live application
app.config['DEBUG'] = True

# Adding for email testing
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'fthtesting@gmail.com'
app.config['MAIL_PASSWORD'] = 'infiniteoptions0422'
app.config['MAIL_DEFAULT_SENDER'] = 'fthtesting@gmail.com'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
# app.config['MAIL_DEBUG'] = True
# app.config['MAIL_SUPPRESS_SEND'] = False
# app.config['TESTING'] = False

mail = Mail(app)

# API
api = Api(app)

# Get RDS password from command line argument
def RdsPw():
    if len(sys.argv) == 2:
        return str(sys.argv[1])
    return ""

# RDS PASSWORD
# When deploying to Zappa, set RDS_PW equal to the password as a string
# When pushing to GitHub, set RDS_PW equal to RdsPw()
RDS_PW = 'prashant'
# RDS_PW = RdsPw()


getToday = lambda: datetime.strftime(date.today(), "%Y-%m-%d")
getNow = lambda: datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")

# Connect to RDS
def getRdsConn(RDS_PW):
    global RDS_HOST
    global RDS_PORT
    global RDS_USER
    global RDS_DB

    print("Trying to connect to RDS...")
    try:
        conn = pymysql.connect(RDS_HOST,
                               user=RDS_USER,
                               port=RDS_PORT,
                               passwd=RDS_PW,
                               db=RDS_DB)
        cur = conn.cursor()
        print("Successfully connected to RDS.")
        return [conn, cur]
    except:
        print("Could not connect to RDS.")
        raise Exception("RDS Connection failed.")

# Connect to MySQL database (API v2)
def connect():
    global RDS_PW
    global RDS_HOST
    global RDS_PORT
    global RDS_USER
    global RDS_DB

    print("Trying to connect to RDS (API v2)...")
    try:
        conn = pymysql.connect( RDS_HOST,
                                user=RDS_USER,
                                port=RDS_PORT,
                                passwd=RDS_PW,
                                db=RDS_DB,
                                cursorclass=pymysql.cursors.DictCursor)
        print("Successfully connected to RDS. (API v2)")
        return conn
    except:
        print("Could not connect to RDS. (API v2)")
        raise Exception("RDS Connection failed. (API v2)")

# Disconnect from MySQL database (API v2)
def disconnect(conn):
    try:
        conn.close()
        print("Successfully disconnected from MySQL database. (API v2)")
    except:
        print("Could not properly disconnect from MySQL database. (API v2)")
        raise Exception("Failure disconnecting from MySQL database. (API v2)")

# Serialize JSON
def serializeResponse(response):
    try:
        for row in response:
            for key in row:
                if type(row[key]) is Decimal:
                    row[key] = float(row[key])
                elif type(row[key]) is date or type(row[key]) is datetime:
                    row[key] = row[key].strftime("%Y-%m-%d")
        return response
    except:
        raise Exception("Bad query JSON")

# Execute an SQL command (API v2)
# Set cmd parameter to 'get' or 'post'
# Set conn parameter to connection object
# OPTIONAL: Set skipSerialization to True to skip default JSON response serialization
def execute(sql, cmd, conn, skipSerialization = False):
    response = {}
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            if cmd is 'get':
                result = cur.fetchall()
                response['message'] = 'Successfully executed SQL query.'
                # Return status code of 280 for successful GET request
                response['code'] = 280
                if not skipSerialization:
                    result = serializeResponse(result)
                response['result'] = result
            elif cmd in 'post':
                conn.commit()
                response['message'] = 'Successfully committed SQL command.'
                # Return status code of 281 for successful POST request
                response['code'] = 281
            else:
                response['message'] = 'Request failed. Unknown or ambiguous instruction given for MySQL command.'
                # Return status code of 480 for unknown HTTP method
                response['code'] = 480
    except:
        response['message'] = 'Request failed, could not execute MySQL command.'
        # Return status code of 490 for unsuccessful HTTP request
        response['code'] = 490
    finally:
        response['sql'] = sql
        return response

# Close RDS connection
def closeRdsConn(cur, conn):
    try:
        cur.close()
        conn.close()
        print("Successfully closed RDS connection.")
    except:
        print("Could not close RDS connection.")

# Runs a select query with the SQL query string and pymysql cursor as arguments
# Returns a list of Python tuples
def runSelectQuery(query, cur):
    try:
        cur.execute(query)
        queriedData = cur.fetchall()
        return queriedData
    except:
        raise Exception("Could not run select query and/or return data")

# -- Queries start here -------------------------------------------------------------------------------


#Get Drivers
class GetDrivers(Resource):
    def get(self):
        response = {}
        items = {}
        try:
            conn = connect()
            print("P")
            items = execute("""SELECT * FROM drivers;""", 'get', conn)

            response['message'] = 'successful'
            response['result'] = items

            return response, 200
        except:
            raise BadRequest('Request failed, please try again later.')
        finally:
            disconnect(conn)

#Get Businesses
class GetBusiness(Resource):
    def get(self):
        response = {}
        items = {}
        try:
            conn = connect()
            print("P")
            items = execute("""SELECT * FROM business;""", 'get', conn)

            response['message'] = 'successful'
            response['result'] = items

            return response, 200
        except:
            raise BadRequest('Request failed, please try again later.')
        finally:
            disconnect(conn)

#Get Customers
class GetCustomers(Resource):
    def get(self):
        response = {}
        items = {}
        try:
            conn = connect()
            print("P")
            items = execute("""SELECT * FROM customers;""", 'get', conn)

            response['message'] = 'successful'
            response['result'] = items

            return response, 200
        except:
            raise BadRequest('Request failed, please try again later.')
        finally:
            disconnect(conn)

#Driver for each customer on route
class GetCustomerRoutes(Resource):
    def get(self):
        response = {}
        items = {}
        try:
            conn = connect()
            print("P")
            items = execute("""SELECT temp2.route_id,
                                    temp2.driver_id,
                                    temp2.driver_first_name,
                                    temp2.driver_last_name,
                                    temp2.business_id,
		                            customers.customer_id,
		                            customers.customer_first_name, 
		                            customers.customer_last_name,
                                    customers.customer_street,
                                    customers.customer_city,
                                    customers.customer_state,
                                    customers.customer_zip,
                                    customers.customer_email,
                                    customers.customer_phone_num,
                                    customers.customer_latitude,
                                    customers.customer_longitude
                                FROM 
			                            (SELECT temp.route_id,
					                            temp.driver_id,
					                            drivers.driver_first_name,
					                            drivers.driver_last_name,
                                                drivers.business_id,
					                            temp.customer_id
			                            FROM
				                                    (SELECT route_id, 
						                                    driver_id, 
						                                    CAST(JSON_EXTRACT(route,val) AS CHAR) AS customer_id 
						                            FROM 
							                                route JOIN numbers ON JSON_LENGTH(route) >= n) AS temp 
			                            JOIN drivers on temp.driver_id = drivers.driver_id) AS temp2
		                        JOIN customers ON temp2.customer_id = customers.customer_id; """, 'get', conn)

            response['message'] = 'successful'
            response['result'] = items

            return response, 200
        except:
            raise BadRequest('Request failed, please try again later.')
        finally:
            disconnect(conn)

#Order for each customer
class GetCustomerOrders(Resource):
    def get(self):
        response = {}
        items = {}
        try:
            conn = connect()
            print("P")
            items = execute("""SELECT customers.customer_id,
		                            customers.customer_first_name, 
		                            customers.customer_last_name,
                                    customers.customer_street,
                                    customers.customer_city,
                                    customers.customer_state,
                                    customers.customer_zip,
                                    customers.customer_email,
                                    customers.customer_phone_num,
                                    customers.customer_latitude,
                                    customers.customer_longitude,
                                    orders.order_id,
                                    orders.items,
                                    orders.amount,
                                    orders.order_instructions,
                                    orders.delivery_instructions,
                                    orders.order_type,
                                    orders.order_status
	                        FROM 
		                            customers JOIN orders ON customers.customer_id = orders.customer_id;""", 'get', conn)

            response['message'] = 'successful'
            response['result'] = items

            return response, 200
        except:
            raise BadRequest('Request failed, please try again later.')
        finally:
            disconnect(conn)

#Constraints for each business
class BusinessConstraints(Resource):
    def get(self):
        response = {}
        items = {}
        try:
            conn = connect()
            print("P")
            items = execute("""SELECT business.business_id,
		                            business.business_name,
                                    business.business_street,
                                    business.business_city,
                                    business.business_state,
                                    business.business_zip,
                                    constraints.num_driver,
                                    constraints.max_distance,
                                    constraints.min_distance,
                                    constraints.units_distance,
                                    constraints.max_time,
                                    constraints.min_time,
                                    constraints.units_time,
                                    constraints.max_deliveries,
                                    constraints.min_deliveries
                                FROM 
			                        business JOIN constraints ON business.business_id = constraints.business_id;""", 'get', conn)

            response['message'] = 'successful'
            response['result'] = items

            return response, 200
        except:
            raise BadRequest('Request failed, please try again later.')
        finally:
            disconnect(conn)

#Order for each business
class GetBusinessOrders(Resource):
    def get(self):
        response = {}
        items = {}
        try:
            conn = connect()
            print("P")
            items = execute("""SELECT orders.business_id,
		                            business.business_name,
                                    business.business_street,
                                    business.business_city,
                                    business.business_state,
                                    business.business_phone_num,
                                    business.business_email,
                                    business.business_latitude,
                                    business.business_longitude,
		                            orders.orders_id,
                                    orders.items,
                                    orders.amount,
                                    orders.order_type,
                                    orders.order_status,
                                    orders.delivery_latitude,
                                    orders.delivery_longitude
                                FROM 
			                        orders JOIN business ON orders.business_id = business.business_id;""", 'get', conn)

            response['message'] = 'successful'
            response['result'] = items

            return response, 200
        except:
            raise BadRequest('Request failed, please try again later.')
        finally:
            disconnect(conn)

#Driver for each business
class GetBusinessDrivers(Resource):
    def get(self):
        response = {}
        items = {}
        try:
            conn = connect()
            print("P")
            items = execute("""SELECT drivers.driver_id,
		                            drivers.driver_first_name,
                                    drivers.driver_last_name,
                                    drivers.driver_hours,
                                    drivers.business_id,
                                    business.business_name,
                                    business.business_street,
                                    business.business_city,
                                    business.business_state,
                                    business.business_email,
                                    business.business_phone_num,
                                    business.business_latitude,
                                    business.business_longitude
                                FROM
			                        drivers JOIN business ON drivers.business_id = business.business_id;""", 'get', conn)

            response['message'] = 'successful'
            response['result'] = items

            return response, 200
        except:
            raise BadRequest('Request failed, please try again later.')
        finally:
            disconnect(conn)





#Api Routes
api.add_resource(GetDrivers, '/api/v2/getDrivers')
api.add_resource(GetBusiness, '/api/v2/getBusinesses')
api.add_resource(GetCustomers, '/api/v2/getCustomers')
api.add_resource(GetCustomerRoutes, '/api/v2/getCustomerRoutes')
api.add_resource(GetCustomerOrders, '/api/v2/getCustomerOrders')
api.add_resource(BusinessConstraints, '/api/v2/BusinessConstraints')
api.add_resource(GetBusinessOrders, '/api/v2/getBusinessOrders')
api.add_resource(GetBusinessDrivers, '/api/v2/getBusinessDrivers')



if __name__ == '__main__':
    app.run(host='127.0.0.1', port=4000)