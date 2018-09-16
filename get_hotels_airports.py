#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 15 12:42:47 2018

@author: mihirkhambete
"""

import os
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from amadeus import Client, ResponseError, Location

#airport-city-search
AMADEUS_CLIENT_ID = 'W5UNInYUVqlyn1j7A5GPWGgI2gRovFRC'
AMADEUS_CLIENT_SECRET = 'nAtRrY63wDEGUGZ9'
amadeus = Client(client_id='W5UNInYUVqlyn1j7A5GPWGgI2gRovFRC',
                 client_secret='nAtRrY63wDEGUGZ9')

#response = amadeus.travel.analytics.air_traffic.booked.get(origin='BOS', period='2017-08')
#print(response.data)
def find_airports(lat, long, max_dist = None):
    """
    This function finds Amadeus-listed airports close to a disaster site
    
    Args:
        lat: latitude of the disaster site
        long: longitude of the disaster site
        max_dist: maimum distance from hotel to site
        
    Returns:
        airport_distances_to_site: dictionary of airport name: distance pairs
    """
    #find airports within 500km.
    default_airports = amadeus.reference_data.locations.airports.get(latitude = lat,
                                                                     longitude = long)
    default_airports_data = default_airports.data
    airport_distances_to_site = {}
    
    for i in range(len(default_airports_data)):
        code = str(default_airports_data[i]['iataCode'])
        airport_lat = default_airports_data[i]['geoCode']['latitude']
        airport_long = default_airports_data[i]['geoCode']['longitude']
        coordinates = (airport_lat, airport_long)
        distance = float(geodesic((coordinates),(lat,long)).miles)
        #only allow hotels less than maxDist from disaster site
        if max_dist and distance > max_dist:
            continue
        airport_distances_to_site[code] = distance
    return airport_distances_to_site

def find_nearby_flights(airport_distances_dict, origin_airport="BOS",
                        departure_date='2018-09-21'):
    """
    Find flights to nearby airports (found in find_airports function)
    
    Args:
        airport_distances_dict: dictionary of airport names: distances from site
        (from find_airports function)
        
        origin_airport: 3-letter code for origin airport
        departure_date: date of departure from origin airport
    """
    latest_arrival_time = departure_date + 'T23:59'
    list_flights = []
    for destination_airport in airport_distances_dict.keys():
        flight_data = amadeus.shopping.flight_offers.get(origin = origin_airport, 
                                                         destination = destination_airport, 
                                                         departureDate = departure_date,
                                                         arrivalBy = latest_arrival_time,
                                                         ).data
        #print(flight_data[0])
        for i in range(len(flight_data)):
            flight_string = ""
            flight_segments = flight_data[i]['offerItems'][0]['services'][0]['segments']
            num_segments = len(flight_segments)
            for j in range(num_segments):
                flight_string += flight_segments[j]['flightSegment']['carrierCode']
                flight_string += " "
                flight_string += flight_segments[j]['flightSegment']['number']
                flight_string += " departing from"
                flight_string += flight_segments[j]['flightSegment']['departure']['iataCode']
                flight_string += " at "
                flight_string += flight_segments[j]['flightSegment']['departure']['at']
                flight_string += " to "
                flight_string += flight_segments[j]['flightSegment']['arrival']['iataCode']
                flight_string += ", "
            list_flights.append(flight_string)
    return list_flights
                

def find_hotels(lat, long, max_dist = None):
    """
    This function finds Amadeus-listed hotels close to a disaster site
    
    Args:
        lat: latitude of the disaster site
        long: longitude of the disaster site
        max_dist: maimum distance from hotel to site
        
    Returns:
        hotel_distances_to_site: dictionary of hotel name: distance pairs
    """
    #get the hotels close to the disaster site
    get_exact = amadeus.shopping.hotel_offers.get(latitude = lat,
                                             longitude = long)
    exact_data = get_exact.data
#    get_west = amadeus.shopping.hotel_offers.get(latitude = lat,
#                                             longitude = (long - 0.5))
#    west_data = get_west.data
#    get_east = amadeus.shopping.hotel_offers.get(latitude = lat,
#                                             longitude = (long + 0.5))
#    east_data = get_east.data
#    get_north = amadeus.shopping.hotel_offers.get(latitude = (lat + 0.5),
#                                             longitude = long)
#    north_data = get_north.data
#    get_south = amadeus.shopping.hotel_offers.get(latitude = (lat - 0.5),
#                                             longitude = long)
#    print("Woohoo!")
#    #south_data = get_south.data
#    all_data = list(exact_data + west_data + east_data)
    #sort the hotels by distance
    all_data = list(exact_data)
    hotel_distances_to_site = {}
    
    #match hotel coordinates to names
    for i in range(len(all_data)):
        name = all_data[i]['hotel']['name']
        hotel_lat = all_data[i]['hotel']['latitude']
        hotel_long = all_data[i]['hotel']['longitude']
        coordinates = (hotel_lat, hotel_long)
        distance = geodesic((coordinates),(lat,long)).miles
        if max_dist and distance > max_dist:
            continue
        hotel_distances_to_site[name] = distance
    return hotel_distances_to_site
    

#example function calls    
#local_airports = find_airports(33.7, -84.3, 200)
#find_flights = find_nearby_flights(local_airports,"SFO",departure_date = 2018-09-21)
#local_hotels = find_hotels(33.7, -84.3)
#
#print(local_airports)
#print(len(find_flights))
#print(local_hotels)
#test = find_nearby_flights(find_airports(34.54,-78.18), origin_airport="SFO")
#print(test)
