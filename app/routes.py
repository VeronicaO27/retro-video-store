import os
import requests
from sqlalchemy.orm import query
from app import db
from datetime import datetime
from dotenv import load_dotenv
from app.models.rental import Rental
from app.models.video import Video
from app.models.customer import Customer
from flask import Blueprint ,jsonify, request

rentals_bp = Blueprint("rentals", __name__, url_prefix="/rentals")
videos_bp = Blueprint("videos", __name__, url_prefix="/videos")
customers_bp = Blueprint("customer", __name__, url_prefix="/customers")

@customers_bp.route("", methods=["GET","POST"])
def active_customers():
    if request.method == 'GET':
        customers = Customer.query.all()

        customers_response = []
        for customer in customers:
            # customers_response.append(
                customer_dict = customer.customer_dict()
                customers_response.append(customer_dict)

        return jsonify(customers_response),200

    elif request.method == 'POST':
        cst_request_body = request.get_json()
        if "name" not in cst_request_body or "postal_code" not in cst_request_body or "phone" not in cst_request_body:
            return jsonify({
                "details": "Invalid data"
            }), 400

        new_customer = Customer(
            name = cst_request_body["name"],
            postal_code = cst_request_body["postal_code"],
            phone = cst_request_body["phone"]
        )

        db.session.add(new_customer)
        db.session.commit()

        new_cst_response = {"The phone number you provide must be 10 digits.":new_customer.customer_dict()}

        return jsonify(new_cst_response),201

@customers_bp.route("/<customer_id>", methods =["GET", "PUT", "DELETE"])
def retrieve_customer(customer_id):
    if customer_id.isdigit() is False:
        return jsonify(None), 400
    customer = Customer.query.get(customer_id)
    if customer == None:
        return jsonify({"message": "Customer 1 was not found"}), 404
    elif request.method == 'GET':
        response_body  = customer.customer_dict()
        return jsonify(response_body), 200

    elif request.method == 'PUT':
        request_body = request.get_json()
        customer.name = request_body["name"]
        customer.postal_code = request_body["postal_code"]
        customer.phone_ = request_body["phone"]
        db.session.commit()

        response_body={"customer":(customer.customer_dict())}
        return jsonify(response_body),200

    elif request.method == "DELETE":
        db.session.delete(customer)
        db.session.commit()
        return jsonify({f"message": "Customer {customer.id} was not found"}),200
