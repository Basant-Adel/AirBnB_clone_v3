#!/usr/bin/python3
"""Create a view for Place"""

from flask import jsonify, request, abort, make_response
from api.v1.views import app_views
from models import storage
from models.city import City
from models.place import Place

# Existing code for /cities/<city_id>/places, /places/<place_id>, /places/<place_id>, and /places/<place_id>

@app_views.route('/places_search', methods=['POST'], strict_slashes=False)
def places_search():
    data = request.get_json()

    if data is None:
        abort(400, 'Not a JSON')

    states = data.get('states', [])
    cities = data.get('cities', [])
    amenities = data.get('amenities', [])

    places = storage.all("Place").values()

    if not states and not cities and not amenities:
        return jsonify([place.to_dict() for place in places])

    search_results = set()

    if states:
        for state_id in states:
            state = storage.get("State", state_id)
            if state:
                for city in state.cities:
                    search_results.update(city.places)

    if cities:
        for city_id in cities:
            city = storage.get("City", city_id)
            if city:
                search_results.update(city.places)

    if amenities:
        amenities_set = set()
        for amenity_id in amenities:
            amenity = storage.get("Amenity", amenity_id)
            if amenity:
                amenities_set.add(amenity)

        for place in search_results.copy():
            if not amenities_set.issubset(place.amenities):
                search_results.remove(place)

    return jsonify([place.to_dict() for place in search_results])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000")
