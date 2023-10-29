#!/usr/bin/python3
""" Create a view for Place """

from flask import Flask, jsonify, request, abort, make_response
from api.v1.views import app_views
from models import storage
from models.city import City
from models.place import Place
from models.state import State
from models.amenity import Amenity


@app_views.route('/cities/<city_id>/places', methods=['GET'],
                 strict_slashes=False)
def get_places_by_city(city_id):
    """Retrieves the list of all Place objects of a city"""
    city = storage.get("City", city_id)
    if not city:
        abort(404)
    return jsonify([place.to_dict() for place in city.places])


@app_views.route('/places/<place_id>', methods=['GET'], strict_slashes=False)
def get_place(place_id):
    """Retrieves a place object by ID"""
    place = storage.get("Place", place_id)
    if place is None:
        abort(404)
    return jsonify(place.to_dict())


@app_views.route('/places/<place_id>', methods=['DELETE'],
                 strict_slashes=False)
def delete_place(place_id):
    """Deletes a Place object by ID"""
    place = storage.get("Place", place_id)
    if place is None:
        abort(404)
    place.delete()
    storage.save()
    return make_response(jsonify({}), 200)


@app_views.route('/cities/<city_id>/places', methods=['POST'],
                 strict_slashes=False)
def create_place(city_id):
    """Creates a Place object"""
    city = storage.get("City", city_id)
    if not city:
        abort(404)
    data = request.get_json()
    if not data:
        abort(400, 'Not a JSON')
    if 'user_id' not in data:
        abort(400, 'Missing user_id')
    user = storage.get("User", data["user_id"])
    if not user:
        abort(404)
    if 'name' not in data:
        abort(400, 'Missing name')
    place = Place(**data)
    setattr(place, 'city_id', city_id)
    storage.new(place)
    storage.save()
    return make_response(jsonify(place.to_dict()), 201)


@app_views.route('/places/<place_id>', methods=['PUT'],
                 strict_slashes=False)
def update_place(place_id):
    """Updates a Place object by ID"""
    place = storage.get("Place", place_id)
    if place is None:
        abort(404)
    data = request.get_json()
    if not data:
        abort(400, 'Not a JSON')

    # Update the State object's attributes based on the JSON data
    for key, value in data.items():
        if key not in ['id', 'user_id', 'city_id', 'created_at', 'updated_at']:
            setattr(place, key, value)
    storage.save()
    return make_response(jsonify(place.to_dict()), 200)


@app_views.route('/api/v1/places_search', methods=['POST'])
def places_search():
    if not request.is_json:
        return jsonify({"error": "Not a JSON"}), 400

    data = request.get_json()

    if not data or all(not data.get(key) for key in ['states', 'cities',
                                                     'amenities']):
        # Retrieve all places if JSON body is empty || each list is empty
        return jsonify(places)

    filtered_places = places

    if data.get('states'):
        # Filter Places by Sstates
        filtered_places = [
            place for place in filtered_places if place['state'] /
            in data['states']
        ]

    if data.get('cities'):
        # Filter Places by Cities
        filtered_places = [
            place for place in filtered_places if place['city'] /
            in data['cities']
        ]

    if data.get('amenities'):
        # Filter places by Amenities
        filtered_places = [
            place for place in filtered_places /
            if set(data['amenities']).issubset(place['amenities'])
        ]

    return jsonify(filtered_places)
