import os
import requests
from sqlalchemy.orm import query
from app import db
from datetime import datetime, timedelta
from dotenv import load_dotenv
from app.models.rental import Rental
from app.models.video import Video
from app.models.customer import Customer
from flask import Blueprint, json, jsonify, request

rentals_bp = Blueprint("rentals", __name__, url_prefix="/rentals")
videos_bp = Blueprint("videos", __name__, url_prefix="/videos")
customers_bp = Blueprint("customer", __name__, url_prefix="/customers")

def missing_field_in_request_body(missing_field):
    return jsonify({"details": f"Request body must include {missing_field}."}), 400

def none_value():
    return jsonify(None), 400

@videos_bp.route("", methods = ["GET", "POST"])
def handle_videos():
    videos = Video.query.all()

    if videos is None:
        return jsonify([]), 200

    elif request.method == "GET":
        videos_list = []
        for video in videos:
            videos_list.append({
                "id": video.id,
                "title": video.title,
                "release_date": video.release_date,
                "total_inventory": video.total_inventory
            })
        
        return jsonify(videos_list), 200

    elif request.method == "POST":
        request_body = request.get_json()

        missing_field_list = ["title", "release_date", "total_inventory"]

        for word in missing_field_list:
            if word not in request_body:
                return missing_field_in_request_body(word)

        new_video = Video(
            title = request_body["title"],
            release_date = request_body["release_date"],
            total_inventory = request_body["total_inventory"]
        )

        db.session.add(new_video)
        db.session.commit()

        return new_video.video_dict(), 201

@videos_bp.route("/<video_id>", methods = ["GET", "PUT", "DELETE"])
def handle_video_id(video_id):

    if video_id.isnumeric() is False:
        return none_value()
    
    video = Video.query.get(video_id)

    if video is None:
        return jsonify({"message": f"Video {video_id} was not found"}), 404

    elif request.method == "GET":
        return video.video_dict(), 200
    
    elif request.method == "PUT":
        updated_body = request.get_json()

        missing_field_list = ["title", "release_date", "total_inventory"]

        for word in missing_field_list:
            if word not in updated_body:
                return none_value()

        video.title = updated_body["title"]
        video.release_date = updated_body["release_date"]
        video.total_inventory = updated_body["total_inventory"]
        db.session.commit()

        return video.video_dict(), 200

    elif request.method == "DELETE":
        db.session.delete(video)
        db.session.commit()

        return jsonify({"id": video.id}), 200

@customers_bp.route("", methods=["GET","POST"])
def active_customers():
    if request.method == 'GET':
        customers = Customer.query.all()

        customers_response = []
        for customer in customers:
            customer_dict = customer.customer_dict()
            customers_response.append(customer_dict)

        return jsonify(customers_response),200

    elif request.method == 'POST':
        cst_request_body = request.get_json()

        missing_field_list = ["name", "postal_code", "phone"]

        for word in missing_field_list:
            if word not in cst_request_body:
                return missing_field_in_request_body(word)
        
        new_customer = Customer(
            name = cst_request_body["name"],
            phone = cst_request_body["phone"],
            postal_code = cst_request_body["postal_code"]
        )

        db.session.add(new_customer)
        db.session.commit()

        new_cst_response = new_customer.customer_dict()

        return jsonify(new_cst_response), 201

@customers_bp.route("/<customer_id>", methods =["GET", "PUT", "DELETE"])
def retrieve_customer(customer_id):

    if customer_id.isdigit() is False:
        return none_value()

    customer = Customer.query.get(customer_id)

    if customer == None:
        return jsonify({"message": "Customer 1 was not found"}), 404
    elif request.method == 'GET':
        response_body = customer.customer_dict()
        return jsonify(response_body), 200

    elif request.method == 'PUT':
        request_body = request.get_json()

        missing_field_list = ["name", "postal_code", "phone"]

        for word in missing_field_list:
            if word not in request_body:
                return none_value()

        customer.name = request_body["name"]
        customer.postal_code = request_body["postal_code"]
        customer.phone = request_body["phone"]
        db.session.commit()

        response_body = customer.customer_dict()
        return jsonify(response_body), 200

    elif request.method == "DELETE":
        db.session.delete(customer)
        db.session.commit()
        return jsonify({"id": customer.id}), 200


@customers_bp.route("/<customer_id>/rentals", methods=["GET"])
def get_rentals_for_customer(customer_id):
    
    customer = Customer.query.get(customer_id)
    
    if customer is None:
        return jsonify({"message": f"Customer {customer_id} was not found"}), 404
    
    elif request.method == "GET":
        list_of_videos = []
        for rental in customer.rentals:
            video = Video.query.get(rental.video_id)
            response_body = {
                "release_date": video.release_date,
                "title": video.title,
                "due_date": rental.due_date
            }
            list_of_videos.append(response_body)

        return jsonify(list_of_videos), 200


@videos_bp.route("/<video_id>/rentals", methods = ["GET"])
def get_videos_for_rental(video_id):
    video = Video.query.get(video_id)

    if video is None:
        return jsonify (
            {"message": f"Video {video_id} was not found"}), 404
    elif request.method == 'GET':
        rented_out_videos = Rental.query.filter(Rental.video_id == video_id)
        
        list_of_customers = []
        for rental in video.rentals:
            customer = Customer.query.get(rental.customer_id)
            response_body = {
                "due_date": rental.due_date,
                "name": customer.name,
                "phone": customer.phone,
                "postal_code": customer.postal_code
            }
            list_of_customers.append(response_body)

        return jsonify(list_of_customers), 200


@rentals_bp.route("/check-out", methods = ["POST"])
def get_rental_check_out():
    request_body = request.get_json()

    missing_field_list = ["video_id", "customer_id"]

    for word in missing_field_list:
        if word not in request_body:
            return none_value()

    video = Video.query.get(request_body["video_id"])
    customer = Customer.query.get(request_body["customer_id"])

    if video is None:
        return jsonify({"message":"Video does not exist"}), 404 

    if customer is None:
        return jsonify ({"message": "Customer does not exist"}), 404
    
    videos_checked_out = Rental.query.filter(Rental.video_id == request_body["video_id"], Rental.checked_out == True).count()
    
    if videos_checked_out == video.total_inventory:
        return jsonify ({
            "message": "Could not perform checkout"
        }), 400
    
    new_rental = Rental(
        video_id=request_body["video_id"],
        customer_id=request_body["customer_id"],
        checked_out=True
    )

    db.session.add(new_rental)
    db.session.commit()

    videos_checked_out = Rental.query.filter(Rental.video_id==request_body["video_id"], Rental.checked_out==True).count()

    available_inventory = video.total_inventory - videos_checked_out

    return jsonify({
        "customer_id": customer.id,
        "video_id": video.id,
        "due_date": datetime.now() + timedelta(days=7),
        "videos_checked_out_count": videos_checked_out,
        "available_inventory": available_inventory
    }), 200

@rentals_bp.route("/check-in", methods = ["POST"])
def get_rental():
    request_body = request.get_json()

    missing_field_list = ["video_id", "customer_id"]

    for word in missing_field_list:
        if word not in request_body:
            return none_value()

    video = Video.query.get(request_body["video_id"])
    customer = Customer.query.get(request_body["customer_id"])   

    if video is None or customer is None:
        return jsonify({"message": "Video and customer does not exist"}), 404

    rental = Rental.query.filter(Rental.video_id == request_body["video_id"], Rental.customer_id == customer.id, Rental.checked_out == True).first()

    if rental is None:
        return jsonify({"message": f"No outstanding rentals for customer {customer.id} and video {video.id}"}), 400
        
    rental.checked_out = False

    db.session.commit()

    videos_checked_out = Rental.query.filter(Rental.video_id == request_body["video_id"], Rental.checked_out == True).count()

    available_inventory = video.total_inventory - videos_checked_out

    videos_checked_out_by_customer = Rental.query.filter(Rental.customer_id == request_body["customer_id"], Rental.checked_out == True).count()

    return jsonify({
        "customer_id": customer.id,
        "video_id": video.id,
        "videos_checked_out_count": videos_checked_out_by_customer,
        "available_inventory": available_inventory
    }), 200