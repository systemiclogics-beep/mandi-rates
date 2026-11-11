#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BharatMandi - Automated Krishi Mausam (Weather & Rain Advisory) Fetcher
------------------------------------------------------------------------
Batch queries Open-Meteo free API for verified APMC Mandi coordinates across
Bharat and generates lightweight weather.json with actionable farmer advisories.
"""

import os
import sys
import json
import time
from datetime import datetime
import requests

# Verified APMC Mandi and District Coordinates for weather querying
APMC_COORDINATES = {
  "Neemuch": {
    "market": "Neemuch",
    "district": "Neemuch",
    "state": "Madhya Pradesh",
    "lat": 24.4727,
    "lon": 74.8703
  },
  "Mandsaur": {
    "market": "Mandsaur",
    "district": "Mandsaur",
    "state": "Madhya Pradesh",
    "lat": 24.0722,
    "lon": 75.0694
  },
  "Indore": {
    "market": "Indore",
    "district": "Indore",
    "state": "Madhya Pradesh",
    "lat": 22.6841,
    "lon": 75.8398
  },
  "Ujjain": {
    "market": "Ujjain",
    "district": "Ujjain",
    "state": "Madhya Pradesh",
    "lat": 23.1765,
    "lon": 75.7885
  },
  "Ratlam": {
    "market": "Ratlam",
    "district": "Ratlam",
    "state": "Madhya Pradesh",
    "lat": 23.3315,
    "lon": 75.0367
  },
  "Dewas": {
    "market": "Dewas",
    "district": "Dewas",
    "state": "Madhya Pradesh",
    "lat": 22.9676,
    "lon": 76.0534
  },
  "Harda": {
    "market": "Harda",
    "district": "Harda",
    "state": "Madhya Pradesh",
    "lat": 22.3444,
    "lon": 77.0982
  },
  "Sehore": {
    "market": "Sehore",
    "district": "Sehore",
    "state": "Madhya Pradesh",
    "lat": 23.2032,
    "lon": 77.0844
  },
  "Vidisha": {
    "market": "Vidisha",
    "district": "Vidisha",
    "state": "Madhya Pradesh",
    "lat": 23.5251,
    "lon": 77.8081
  },
  "Khargone": {
    "market": "Khargone",
    "district": "Khargone",
    "state": "Madhya Pradesh",
    "lat": 21.8234,
    "lon": 75.6146
  },
  "Khandwa": {
    "market": "Khandwa",
    "district": "Khandwa",
    "state": "Madhya Pradesh",
    "lat": 21.8314,
    "lon": 76.3498
  },
  "Sagar": {
    "market": "Sagar",
    "district": "Sagar",
    "state": "Madhya Pradesh",
    "lat": 23.8388,
    "lon": 78.7378
  },
  "Jabalpur": {
    "market": "Jabalpur",
    "district": "Jabalpur",
    "state": "Madhya Pradesh",
    "lat": 23.1815,
    "lon": 79.9864
  },
  "Kalyan": {
    "market": "Kalyan",
    "district": "Thane",
    "state": "Maharashtra",
    "lat": 19.2403,
    "lon": 73.1305
  },
  "Ulhasnagar": {
    "market": "Ulhasnagar",
    "district": "Thane",
    "state": "Maharashtra",
    "lat": 19.2215,
    "lon": 73.1645
  },
  "Bhiwandi": {
    "market": "Bhiwandi",
    "district": "Thane",
    "state": "Maharashtra",
    "lat": 19.2967,
    "lon": 73.0631
  },
  "Thane": {
    "market": "Thane",
    "district": "Thane",
    "state": "Maharashtra",
    "lat": 19.2183,
    "lon": 72.9781
  },
  "Mumbai": {
    "market": "Mumbai",
    "district": "Mumbai",
    "state": "Maharashtra",
    "lat": 19.076,
    "lon": 72.8777
  },
  "Palghar": {
    "market": "Palghar",
    "district": "Palghar",
    "state": "Maharashtra",
    "lat": 19.6967,
    "lon": 72.7699
  },
  "Raigad": {
    "market": "Raigad",
    "district": "Raigad",
    "state": "Maharashtra",
    "lat": 18.5158,
    "lon": 73.1822
  },
  "Murbad": {
    "market": "Murbad",
    "district": "Thane",
    "state": "Maharashtra",
    "lat": 19.252,
    "lon": 73.398
  },
  "Vashi": {
    "market": "Vashi",
    "district": "Thane",
    "state": "Maharashtra",
    "lat": 19.0771,
    "lon": 73.0039
  },
  "Panvel": {
    "market": "Panvel",
    "district": "Raigad",
    "state": "Maharashtra",
    "lat": 18.9894,
    "lon": 73.1175
  },
  "Karjat": {
    "market": "Karjat",
    "district": "Raigad",
    "state": "Maharashtra",
    "lat": 18.91,
    "lon": 73.33
  },
  "Shahapur": {
    "market": "Shahapur",
    "district": "Thane",
    "state": "Maharashtra",
    "lat": 19.45,
    "lon": 73.33
  },
  "Lasalgaon": {
    "market": "Lasalgaon",
    "district": "Nashik",
    "state": "Maharashtra",
    "lat": 20.1472,
    "lon": 74.2256
  },
  "Pimpalgaon": {
    "market": "Pimpalgaon",
    "district": "Nashik",
    "state": "Maharashtra",
    "lat": 20.1741,
    "lon": 73.987
  },
  "Nashik": {
    "market": "Nashik",
    "district": "Nashik",
    "state": "Maharashtra",
    "lat": 20.011,
    "lon": 73.7903
  },
  "Pune": {
    "market": "Pune",
    "district": "Pune",
    "state": "Maharashtra",
    "lat": 18.5204,
    "lon": 73.8567
  },
  "Baramati": {
    "market": "Baramati",
    "district": "Pune",
    "state": "Maharashtra",
    "lat": 18.1511,
    "lon": 74.5772
  },
  "Ahmednagar": {
    "market": "Ahmednagar",
    "district": "Ahmednagar",
    "state": "Maharashtra",
    "lat": 19.0952,
    "lon": 74.7496
  },
  "Solapur": {
    "market": "Solapur",
    "district": "Solapur",
    "state": "Maharashtra",
    "lat": 17.6599,
    "lon": 75.9064
  },
  "Latur": {
    "market": "Latur",
    "district": "Latur",
    "state": "Maharashtra",
    "lat": 18.4088,
    "lon": 76.5604
  },
  "Amravati": {
    "market": "Amravati",
    "district": "Amravati",
    "state": "Maharashtra",
    "lat": 20.932,
    "lon": 77.7523
  },
  "Akola": {
    "market": "Akola",
    "district": "Akola",
    "state": "Maharashtra",
    "lat": 20.7002,
    "lon": 77.0082
  },
  "Nagpur": {
    "market": "Nagpur",
    "district": "Nagpur",
    "state": "Maharashtra",
    "lat": 21.1458,
    "lon": 79.0882
  },
  "Jalgaon": {
    "market": "Jalgaon",
    "district": "Jalgaon",
    "state": "Maharashtra",
    "lat": 21.0077,
    "lon": 75.5626
  },
  "Sangli": {
    "market": "Sangli",
    "district": "Sangli",
    "state": "Maharashtra",
    "lat": 16.8524,
    "lon": 74.5815
  },
  "Rajkot": {
    "market": "Rajkot",
    "district": "Rajkot",
    "state": "Gujarat",
    "lat": 22.3486,
    "lon": 70.8122
  },
  "Gondal": {
    "market": "Gondal",
    "district": "Rajkot",
    "state": "Gujarat",
    "lat": 21.9619,
    "lon": 70.7983
  },
  "Unjha": {
    "market": "Unjha",
    "district": "Mehsana",
    "state": "Gujarat",
    "lat": 23.8042,
    "lon": 72.3962
  },
  "Surat": {
    "market": "Surat",
    "district": "Surat",
    "state": "Gujarat",
    "lat": 21.1702,
    "lon": 72.8311
  },
  "Ahmedabad": {
    "market": "Ahmedabad",
    "district": "Ahmedabad",
    "state": "Gujarat",
    "lat": 23.0225,
    "lon": 72.5714
  },
  "Amreli": {
    "market": "Amreli",
    "district": "Amreli",
    "state": "Gujarat",
    "lat": 21.6032,
    "lon": 71.2221
  },
  "Junagadh": {
    "market": "Junagadh",
    "district": "Junagadh",
    "state": "Gujarat",
    "lat": 21.5222,
    "lon": 70.4579
  },
  "Jamnagar": {
    "market": "Jamnagar",
    "district": "Jamnagar",
    "state": "Gujarat",
    "lat": 22.4707,
    "lon": 70.0577
  },
  "Deesa": {
    "market": "Deesa",
    "district": "Banaskantha",
    "state": "Gujarat",
    "lat": 24.2584,
    "lon": 72.1812
  },
  "Morbi": {
    "market": "Morbi",
    "district": "Morbi",
    "state": "Gujarat",
    "lat": 22.812,
    "lon": 70.8384
  },
  "Kota": {
    "market": "Kota",
    "district": "Kota",
    "state": "Rajasthan",
    "lat": 25.1328,
    "lon": 75.8458
  },
  "Jaipur": {
    "market": "Jaipur",
    "district": "Jaipur",
    "state": "Rajasthan",
    "lat": 26.9124,
    "lon": 75.7873
  },
  "Jodhpur": {
    "market": "Jodhpur",
    "district": "Jodhpur",
    "state": "Rajasthan",
    "lat": 26.2389,
    "lon": 73.0243
  },
  "Bikaner": {
    "market": "Bikaner",
    "district": "Bikaner",
    "state": "Rajasthan",
    "lat": 28.0229,
    "lon": 73.3119
  },
  "Sri Ganganagar": {
    "market": "Sri Ganganagar",
    "district": "Sri Ganganagar",
    "state": "Rajasthan",
    "lat": 29.9038,
    "lon": 73.8772
  },
  "Alwar": {
    "market": "Alwar",
    "district": "Alwar",
    "state": "Rajasthan",
    "lat": 27.553,
    "lon": 76.6346
  },
  "Baran": {
    "market": "Baran",
    "district": "Baran",
    "state": "Rajasthan",
    "lat": 25.1011,
    "lon": 76.5132
  },
  "Nagaur": {
    "market": "Nagaur",
    "district": "Nagaur",
    "state": "Rajasthan",
    "lat": 27.207,
    "lon": 73.7423
  },
  "Agra": {
    "market": "Agra",
    "district": "Agra",
    "state": "Uttar Pradesh",
    "lat": 27.1767,
    "lon": 78.0081
  },
  "Kanpur": {
    "market": "Kanpur",
    "district": "Kanpur Nagar",
    "state": "Uttar Pradesh",
    "lat": 26.4499,
    "lon": 80.3319
  },
  "Lucknow": {
    "market": "Lucknow",
    "district": "Lucknow",
    "state": "Uttar Pradesh",
    "lat": 26.8467,
    "lon": 80.9462
  },
  "Varanasi": {
    "market": "Varanasi",
    "district": "Varanasi",
    "state": "Uttar Pradesh",
    "lat": 25.3176,
    "lon": 82.9739
  },
  "Ludhiana": {
    "market": "Ludhiana",
    "district": "Ludhiana",
    "state": "Punjab",
    "lat": 30.901,
    "lon": 75.8573
  },
  "Khanna": {
    "market": "Khanna",
    "district": "Ludhiana",
    "state": "Punjab",
    "lat": 30.7024,
    "lon": 76.2166
  },
  "Gurugram": {
    "market": "Gurugram",
    "district": "Gurugram",
    "state": "Haryana",
    "lat": 28.4595,
    "lon": 77.0266
  },
  "Faridabad": {
    "market": "Faridabad",
    "district": "Faridabad",
    "state": "Haryana",
    "lat": 28.4089,
    "lon": 77.3178
  },
  "Karnal": {
    "market": "Karnal",
    "district": "Karnal",
    "state": "Haryana",
    "lat": 29.6857,
    "lon": 76.9905
  },
  "Sirsa": {
    "market": "Sirsa",
    "district": "Sirsa",
    "state": "Haryana",
    "lat": 29.5349,
    "lon": 75.0298
  },
  "Hisar": {
    "market": "Hisar",
    "district": "Hisar",
    "state": "Haryana",
    "lat": 29.1492,
    "lon": 75.7217
  },
  "Ambala": {
    "market": "Ambala",
    "district": "Ambala",
    "state": "Haryana",
    "lat": 30.3782,
    "lon": 76.7767
  },
  "Rohtak": {
    "market": "Rohtak",
    "district": "Rohtak",
    "state": "Haryana",
    "lat": 28.8955,
    "lon": 76.6066
  },
  "Guntur": {
    "market": "Guntur",
    "district": "Guntur",
    "state": "Andhra Pradesh",
    "lat": 16.3067,
    "lon": 80.4365
  },
  "Kurnool": {
    "market": "Kurnool",
    "district": "Kurnool",
    "state": "Andhra Pradesh",
    "lat": 15.8281,
    "lon": 78.0373
  },
  "Pasighat": {
    "market": "Pasighat",
    "district": "East Siang",
    "state": "Arunachal Pradesh",
    "lat": 28.0668,
    "lon": 95.3268
  },
  "Guwahati": {
    "market": "Guwahati",
    "district": "Kamrup",
    "state": "Assam",
    "lat": 26.1445,
    "lon": 91.7362
  },
  "Nagaon": {
    "market": "Nagaon",
    "district": "Nagaon",
    "state": "Assam",
    "lat": 26.3468,
    "lon": 92.684
  },
  "Gulabbagh": {
    "market": "Gulabbagh",
    "district": "Purnea",
    "state": "Bihar",
    "lat": 25.7771,
    "lon": 87.5186
  },
  "Patna": {
    "market": "Patna",
    "district": "Patna",
    "state": "Bihar",
    "lat": 25.5941,
    "lon": 85.1376
  },
  "Chandigarh": {
    "market": "Chandigarh",
    "district": "Chandigarh",
    "state": "Chandigarh",
    "lat": 30.7333,
    "lon": 76.7794
  },
  "Raipur": {
    "market": "Raipur",
    "district": "Raipur",
    "state": "Chhattisgarh",
    "lat": 21.2514,
    "lon": 81.6296
  },
  "Rajnandgaon": {
    "market": "Rajnandgaon",
    "district": "Rajnandgaon",
    "state": "Chhattisgarh",
    "lat": 21.0974,
    "lon": 81.0375
  },
  "Azadpur": {
    "market": "Azadpur",
    "district": "North Delhi",
    "state": "Delhi",
    "lat": 28.7107,
    "lon": 77.1783
  },
  "Narela": {
    "market": "Narela",
    "district": "North Delhi",
    "state": "Delhi",
    "lat": 28.8527,
    "lon": 77.0945
  },
  "Ponda": {
    "market": "Ponda",
    "district": "North Goa",
    "state": "Goa",
    "lat": 15.4026,
    "lon": 74.0151
  },
  "Shimla": {
    "market": "Shimla",
    "district": "Shimla",
    "state": "Himachal Pradesh",
    "lat": 31.1048,
    "lon": 77.1734
  },
  "Solan": {
    "market": "Solan",
    "district": "Solan",
    "state": "Himachal Pradesh",
    "lat": 30.9045,
    "lon": 77.0967
  },
  "Sopore": {
    "market": "Sopore",
    "district": "Baramulla",
    "state": "Jammu and Kashmir",
    "lat": 34.2987,
    "lon": 74.4691
  },
  "Jammu": {
    "market": "Jammu",
    "district": "Jammu",
    "state": "Jammu and Kashmir",
    "lat": 32.7266,
    "lon": 74.857
  },
  "Ranchi": {
    "market": "Ranchi",
    "district": "Ranchi",
    "state": "Jharkhand",
    "lat": 23.3441,
    "lon": 85.3096
  },
  "Bengaluru": {
    "market": "Bengaluru",
    "district": "Bengaluru Urban",
    "state": "Karnataka",
    "lat": 12.9716,
    "lon": 77.5946
  },
  "Hubballi": {
    "market": "Hubballi",
    "district": "Dharwad",
    "state": "Karnataka",
    "lat": 15.3647,
    "lon": 75.124
  },
  "Davanagere": {
    "market": "Davanagere",
    "district": "Davanagere",
    "state": "Karnataka",
    "lat": 14.4644,
    "lon": 75.9218
  },
  "Palakkad": {
    "market": "Palakkad",
    "district": "Palakkad",
    "state": "Kerala",
    "lat": 10.7867,
    "lon": 76.6548
  },
  "Kochi": {
    "market": "Kochi",
    "district": "Ernakulam",
    "state": "Kerala",
    "lat": 9.9312,
    "lon": 76.2673
  },
  "Imphal": {
    "market": "Imphal",
    "district": "Imphal West",
    "state": "Manipur",
    "lat": 24.817,
    "lon": 93.9368
  },
  "Shillong": {
    "market": "Shillong",
    "district": "East Khasi Hills",
    "state": "Meghalaya",
    "lat": 25.5788,
    "lon": 91.8933
  },
  "Aizawl": {
    "market": "Aizawl",
    "district": "Aizawl",
    "state": "Mizoram",
    "lat": 23.7271,
    "lon": 92.7176
  },
  "Dimapur": {
    "market": "Dimapur",
    "district": "Dimapur",
    "state": "Nagaland",
    "lat": 25.9095,
    "lon": 93.7266
  },
  "Bhubaneswar": {
    "market": "Bhubaneswar",
    "district": "Khordha",
    "state": "Odisha",
    "lat": 20.2961,
    "lon": 85.8245
  },
  "Cuttack": {
    "market": "Cuttack",
    "district": "Cuttack",
    "state": "Odisha",
    "lat": 20.4625,
    "lon": 85.8828
  },
  "Bargarh": {
    "market": "Bargarh",
    "district": "Bargarh",
    "state": "Odisha",
    "lat": 21.333,
    "lon": 83.6219
  },
  "Sambalpur": {
    "market": "Sambalpur",
    "district": "Sambalpur",
    "state": "Odisha",
    "lat": 21.4669,
    "lon": 83.9812
  },
  "Puducherry": {
    "market": "Puducherry",
    "district": "Puducherry",
    "state": "Puducherry",
    "lat": 11.9416,
    "lon": 79.8083
  },
  "Gangtok": {
    "market": "Gangtok",
    "district": "East Sikkim",
    "state": "Sikkim",
    "lat": 27.3314,
    "lon": 88.6138
  },
  "Chennai": {
    "market": "Chennai",
    "district": "Chennai",
    "state": "Tamil Nadu",
    "lat": 13.0827,
    "lon": 80.2707
  },
  "Coimbatore": {
    "market": "Coimbatore",
    "district": "Coimbatore",
    "state": "Tamil Nadu",
    "lat": 11.0168,
    "lon": 76.9558
  },
  "Erode": {
    "market": "Erode",
    "district": "Erode",
    "state": "Tamil Nadu",
    "lat": 11.341,
    "lon": 77.7172
  },
  "Dindigul": {
    "market": "Dindigul",
    "district": "Dindigul",
    "state": "Tamil Nadu",
    "lat": 10.3673,
    "lon": 77.9803
  },
  "Hyderabad": {
    "market": "Hyderabad",
    "district": "Hyderabad",
    "state": "Telangana",
    "lat": 17.385,
    "lon": 78.4867
  },
  "Warangal": {
    "market": "Warangal",
    "district": "Warangal",
    "state": "Telangana",
    "lat": 17.9784,
    "lon": 79.5941
  },
  "Nizamabad": {
    "market": "Nizamabad",
    "district": "Nizamabad",
    "state": "Telangana",
    "lat": 18.6725,
    "lon": 78.0941
  },
  "Agartala": {
    "market": "Agartala",
    "district": "West Tripura",
    "state": "Tripura",
    "lat": 23.8315,
    "lon": 91.2868
  },
  "Haldwani": {
    "market": "Haldwani",
    "district": "Nainital",
    "state": "Uttarakhand",
    "lat": 29.2183,
    "lon": 79.513
  },
  "Haridwar": {
    "market": "Haridwar",
    "district": "Haridwar",
    "state": "Uttarakhand",
    "lat": 29.9457,
    "lon": 78.1642
  },
  "Kolkata": {
    "market": "Kolkata",
    "district": "Kolkata",
    "state": "West Bengal",
    "lat": 22.5726,
    "lon": 88.3639
  },
  "Burdwan": {
    "market": "Burdwan",
    "district": "Purba Bardhaman",
    "state": "West Bengal",
    "lat": 23.2324,
    "lon": 87.8615
  },
  "Siliguri": {
    "market": "Siliguri",
    "district": "Darjeeling",
    "state": "West Bengal",
    "lat": 26.7271,
    "lon": 88.3953
  },
  "458441": {
    "market": "Neemuch",
    "district": "Neemuch",
    "state": "Madhya Pradesh",
    "lat": 24.4727,
    "lon": 74.8703
  },
  "458110": {
    "market": "Neemuch",
    "district": "Neemuch",
    "state": "Madhya Pradesh",
    "lat": 24.4727,
    "lon": 74.8703
  },
  "458001": {
    "market": "Mandsaur",
    "district": "Mandsaur",
    "state": "Madhya Pradesh",
    "lat": 24.0722,
    "lon": 75.0694
  },
  "458002": {
    "market": "Mandsaur",
    "district": "Mandsaur",
    "state": "Madhya Pradesh",
    "lat": 24.0722,
    "lon": 75.0694
  },
  "458667": {
    "market": "Mandsaur",
    "district": "Mandsaur",
    "state": "Madhya Pradesh",
    "lat": 24.0722,
    "lon": 75.0694
  },
  "422306": {
    "market": "Lasalgaon",
    "district": "Nashik",
    "state": "Maharashtra",
    "lat": 20.1472,
    "lon": 74.2256
  },
  "422209": {
    "market": "Pimpalgaon",
    "district": "Nashik",
    "state": "Maharashtra",
    "lat": 20.1741,
    "lon": 73.987
  },
  "422001": {
    "market": "Nashik",
    "district": "Nashik",
    "state": "Maharashtra",
    "lat": 20.011,
    "lon": 73.7903
  },
  "422003": {
    "market": "Nashik",
    "district": "Nashik",
    "state": "Maharashtra",
    "lat": 20.011,
    "lon": 73.7903
  },
  "421501": {
    "market": "Ambernath",
    "district": "Thane",
    "state": "Maharashtra",
    "lat": 19.1979,
    "lon": 73.1932
  },
  "421505": {
    "market": "Ambernath Anand Nagar",
    "district": "Thane",
    "state": "Maharashtra",
    "lat": 19.2085,
    "lon": 73.1895
  },
  "421301": {
    "market": "Kalyan",
    "district": "Thane",
    "state": "Maharashtra",
    "lat": 19.2403,
    "lon": 73.1305
  },
  "421401": {
    "market": "Murbad",
    "district": "Thane",
    "state": "Maharashtra",
    "lat": 19.252,
    "lon": 73.398
  },
  "400703": {
    "market": "Vashi",
    "district": "Thane",
    "state": "Maharashtra",
    "lat": 19.0771,
    "lon": 73.0039
  },
  "410206": {
    "market": "Panvel",
    "district": "Raigad",
    "state": "Maharashtra",
    "lat": 18.9894,
    "lon": 73.1175
  },
  "410201": {
    "market": "Karjat",
    "district": "Raigad",
    "state": "Maharashtra",
    "lat": 18.91,
    "lon": 73.33
  },
  "421601": {
    "market": "Shahapur",
    "district": "Thane",
    "state": "Maharashtra",
    "lat": 19.45,
    "lon": 73.33
  },
  "411037": {
    "market": "Pune (Gultekdi)",
    "district": "Pune",
    "state": "Maharashtra",
    "lat": 18.49,
    "lon": 73.87
  },
  "413102": {
    "market": "Baramati",
    "district": "Pune",
    "state": "Maharashtra",
    "lat": 18.1511,
    "lon": 74.5772
  },
  "360001": {
    "market": "Rajkot",
    "district": "Rajkot",
    "state": "Gujarat",
    "lat": 22.3486,
    "lon": 70.8122
  },
  "360003": {
    "market": "Rajkot",
    "district": "Rajkot",
    "state": "Gujarat",
    "lat": 22.3486,
    "lon": 70.8122
  },
  "360311": {
    "market": "Gondal",
    "district": "Rajkot",
    "state": "Gujarat",
    "lat": 21.9619,
    "lon": 70.7983
  },
  "384170": {
    "market": "Unjha",
    "district": "Mehsana",
    "state": "Gujarat",
    "lat": 23.8042,
    "lon": 72.3962
  },
  "385535": {
    "market": "Deesa",
    "district": "Banaskantha",
    "state": "Gujarat",
    "lat": 24.2584,
    "lon": 72.1812
  },
  "324001": {
    "market": "Kota",
    "district": "Kota",
    "state": "Rajasthan",
    "lat": 25.1328,
    "lon": 75.8458
  },
  "324005": {
    "market": "Kota",
    "district": "Kota",
    "state": "Rajasthan",
    "lat": 25.1328,
    "lon": 75.8458
  },
  "452001": {
    "market": "Indore",
    "district": "Indore",
    "state": "Madhya Pradesh",
    "lat": 22.6841,
    "lon": 75.8398
  },
  "452009": {
    "market": "Indore",
    "district": "Indore",
    "state": "Madhya Pradesh",
    "lat": 22.6841,
    "lon": 75.8398
  },
  "456001": {
    "market": "Ujjain",
    "district": "Ujjain",
    "state": "Madhya Pradesh",
    "lat": 23.1765,
    "lon": 75.7885
  },
  "457001": {
    "market": "Ratlam",
    "district": "Ratlam",
    "state": "Madhya Pradesh",
    "lat": 23.3315,
    "lon": 75.0367
  },
  "132001": {
    "market": "Karnal",
    "district": "Karnal",
    "state": "Haryana",
    "lat": 29.6857,
    "lon": 76.9905
  },
  "125055": {
    "market": "Sirsa",
    "district": "Sirsa",
    "state": "Haryana",
    "lat": 29.5349,
    "lon": 75.0298
  },
  "125001": {
    "market": "Hisar",
    "district": "Hisar",
    "state": "Haryana",
    "lat": 29.1492,
    "lon": 75.7217
  },
  "134003": {
    "market": "Ambala",
    "district": "Ambala",
    "state": "Haryana",
    "lat": 30.3782,
    "lon": 76.7767
  },
  "124001": {
    "market": "Rohtak",
    "district": "Rohtak",
    "state": "Haryana",
    "lat": 28.8955,
    "lon": 76.6066
  },
  "141001": {
    "market": "Ludhiana",
    "district": "Ludhiana",
    "state": "Punjab",
    "lat": 30.901,
    "lon": 75.8573
  },
  "141401": {
    "market": "Khanna",
    "district": "Ludhiana",
    "state": "Punjab",
    "lat": 30.7024,
    "lon": 76.2166
  },
  "282001": {
    "market": "Agra",
    "district": "Agra",
    "state": "Uttar Pradesh",
    "lat": 27.1767,
    "lon": 78.0081
  },
  "208001": {
    "market": "Kanpur",
    "district": "Kanpur Nagar",
    "state": "Uttar Pradesh",
    "lat": 26.4499,
    "lon": 80.3319
  },
  "110033": {
    "market": "Azadpur",
    "district": "North Delhi",
    "state": "Delhi",
    "lat": 28.7107,
    "lon": 77.1783
  },
  "110040": {
    "market": "Narela",
    "district": "North Delhi",
    "state": "Delhi",
    "lat": 28.8527,
    "lon": 77.0945
  },
  "160026": {
    "market": "Chandigarh",
    "district": "Chandigarh",
    "state": "Chandigarh",
    "lat": 30.7333,
    "lon": 76.7794
  },
  "522004": {
    "market": "Guntur",
    "district": "Guntur",
    "state": "Andhra Pradesh",
    "lat": 16.3067,
    "lon": 80.4365
  },
  "518001": {
    "market": "Kurnool",
    "district": "Kurnool",
    "state": "Andhra Pradesh",
    "lat": 15.8281,
    "lon": 78.0373
  },
  "791102": {
    "market": "Pasighat",
    "district": "East Siang",
    "state": "Arunachal Pradesh",
    "lat": 28.0668,
    "lon": 95.3268
  },
  "781001": {
    "market": "Guwahati",
    "district": "Kamrup",
    "state": "Assam",
    "lat": 26.1445,
    "lon": 91.7362
  },
  "782001": {
    "market": "Nagaon",
    "district": "Nagaon",
    "state": "Assam",
    "lat": 26.3468,
    "lon": 92.684
  },
  "854326": {
    "market": "Gulabbagh",
    "district": "Purnea",
    "state": "Bihar",
    "lat": 25.7771,
    "lon": 87.5186
  },
  "800001": {
    "market": "Patna",
    "district": "Patna",
    "state": "Bihar",
    "lat": 25.5941,
    "lon": 85.1376
  },
  "492001": {
    "market": "Raipur",
    "district": "Raipur",
    "state": "Chhattisgarh",
    "lat": 21.2514,
    "lon": 81.6296
  },
  "491441": {
    "market": "Rajnandgaon",
    "district": "Rajnandgaon",
    "state": "Chhattisgarh",
    "lat": 21.0974,
    "lon": 81.0375
  },
  "403401": {
    "market": "Ponda",
    "district": "North Goa",
    "state": "Goa",
    "lat": 15.4026,
    "lon": 74.0151
  },
  "171012": {
    "market": "Shimla",
    "district": "Shimla",
    "state": "Himachal Pradesh",
    "lat": 31.1048,
    "lon": 77.1734
  },
  "173212": {
    "market": "Solan",
    "district": "Solan",
    "state": "Himachal Pradesh",
    "lat": 30.9045,
    "lon": 77.0967
  },
  "193201": {
    "market": "Sopore",
    "district": "Baramulla",
    "state": "Jammu and Kashmir",
    "lat": 34.2987,
    "lon": 74.4691
  },
  "180006": {
    "market": "Jammu",
    "district": "Jammu",
    "state": "Jammu and Kashmir",
    "lat": 32.7266,
    "lon": 74.857
  },
  "834001": {
    "market": "Ranchi",
    "district": "Ranchi",
    "state": "Jharkhand",
    "lat": 23.3441,
    "lon": 85.3096
  },
  "580020": {
    "market": "Hubballi",
    "district": "Dharwad",
    "state": "Karnataka",
    "lat": 15.3647,
    "lon": 75.124
  },
  "577002": {
    "market": "Davanagere",
    "district": "Davanagere",
    "state": "Karnataka",
    "lat": 14.4644,
    "lon": 75.9218
  },
  "678001": {
    "market": "Palakkad",
    "district": "Palakkad",
    "state": "Kerala",
    "lat": 10.7867,
    "lon": 76.6548
  },
  "682001": {
    "market": "Kochi",
    "district": "Ernakulam",
    "state": "Kerala",
    "lat": 9.9312,
    "lon": 76.2673
  },
  "795001": {
    "market": "Imphal",
    "district": "Imphal West",
    "state": "Manipur",
    "lat": 24.817,
    "lon": 93.9368
  },
  "793001": {
    "market": "Shillong",
    "district": "East Khasi Hills",
    "state": "Meghalaya",
    "lat": 25.5788,
    "lon": 91.8933
  },
  "796001": {
    "market": "Aizawl",
    "district": "Aizawl",
    "state": "Mizoram",
    "lat": 23.7271,
    "lon": 92.7176
  },
  "797112": {
    "market": "Dimapur",
    "district": "Dimapur",
    "state": "Nagaland",
    "lat": 25.9095,
    "lon": 93.7266
  },
  "768028": {
    "market": "Bargarh",
    "district": "Bargarh",
    "state": "Odisha",
    "lat": 21.333,
    "lon": 83.6219
  },
  "768001": {
    "market": "Sambalpur",
    "district": "Sambalpur",
    "state": "Odisha",
    "lat": 21.4669,
    "lon": 83.9812
  },
  "605001": {
    "market": "Puducherry",
    "district": "Puducherry",
    "state": "Puducherry",
    "lat": 11.9416,
    "lon": 79.8083
  },
  "737101": {
    "market": "Gangtok",
    "district": "East Sikkim",
    "state": "Sikkim",
    "lat": 27.3314,
    "lon": 88.6138
  },
  "638001": {
    "market": "Erode",
    "district": "Erode",
    "state": "Tamil Nadu",
    "lat": 11.341,
    "lon": 77.7172
  },
  "624001": {
    "market": "Dindigul",
    "district": "Dindigul",
    "state": "Tamil Nadu",
    "lat": 10.3673,
    "lon": 77.9803
  },
  "506002": {
    "market": "Warangal",
    "district": "Warangal",
    "state": "Telangana",
    "lat": 17.9784,
    "lon": 79.5941
  },
  "503001": {
    "market": "Nizamabad",
    "district": "Nizamabad",
    "state": "Telangana",
    "lat": 18.6725,
    "lon": 78.0941
  },
  "799001": {
    "market": "Agartala",
    "district": "West Tripura",
    "state": "Tripura",
    "lat": 23.8315,
    "lon": 91.2868
  },
  "263139": {
    "market": "Haldwani",
    "district": "Nainital",
    "state": "Uttarakhand",
    "lat": 29.2183,
    "lon": 79.513
  },
  "249401": {
    "market": "Haridwar",
    "district": "Haridwar",
    "state": "Uttarakhand",
    "lat": 29.9457,
    "lon": 78.1642
  },
  "713101": {
    "market": "Burdwan",
    "district": "Purba Bardhaman",
    "state": "West Bengal",
    "lat": 23.2324,
    "lon": 87.8615
  },
  "734001": {
    "market": "Siliguri",
    "district": "Darjeeling",
    "state": "West Bengal",
    "lat": 26.7271,
    "lon": 88.3953
  },
  "110": {
    "market": "Azadpur",
    "district": "North Delhi",
    "state": "Delhi",
    "lat": 28.7107,
    "lon": 77.1783
  },
  "160": {
    "market": "Chandigarh",
    "district": "Chandigarh",
    "state": "Chandigarh",
    "lat": 30.7333,
    "lon": 76.7794
  },
  "121": {
    "market": "Faridabad",
    "district": "Faridabad",
    "state": "Haryana",
    "lat": 28.4089,
    "lon": 77.3178
  },
  "122": {
    "market": "Gurugram",
    "district": "Gurugram",
    "state": "Haryana",
    "lat": 28.4595,
    "lon": 77.0266
  },
  "124": {
    "market": "Rohtak",
    "district": "Rohtak",
    "state": "Haryana",
    "lat": 28.8955,
    "lon": 76.6066
  },
  "125": {
    "market": "Hisar",
    "district": "Hisar",
    "state": "Haryana",
    "lat": 29.1492,
    "lon": 75.7217
  },
  "131": {
    "market": "Karnal",
    "district": "Sonipat",
    "state": "Haryana",
    "lat": 28.9931,
    "lon": 77.0151
  },
  "132": {
    "market": "Karnal",
    "district": "Karnal",
    "state": "Haryana",
    "lat": 29.6857,
    "lon": 76.9905
  },
  "134": {
    "market": "Ambala",
    "district": "Ambala",
    "state": "Haryana",
    "lat": 30.3782,
    "lon": 76.7767
  },
  "136": {
    "market": "Karnal",
    "district": "Kurukshetra",
    "state": "Haryana",
    "lat": 29.9695,
    "lon": 76.8783
  },
  "141": {
    "market": "Ludhiana",
    "district": "Ludhiana",
    "state": "Punjab",
    "lat": 30.901,
    "lon": 75.8573
  },
  "143": {
    "market": "Ludhiana",
    "district": "Amritsar",
    "state": "Punjab",
    "lat": 31.634,
    "lon": 74.8723
  },
  "144": {
    "market": "Ludhiana",
    "district": "Jalandhar",
    "state": "Punjab",
    "lat": 31.326,
    "lon": 75.5762
  },
  "147": {
    "market": "Khanna",
    "district": "Patiala",
    "state": "Punjab",
    "lat": 30.3398,
    "lon": 76.3869
  },
  "151": {
    "market": "Ludhiana",
    "district": "Bathinda",
    "state": "Punjab",
    "lat": 30.211,
    "lon": 74.9455
  },
  "171": {
    "market": "Shimla",
    "district": "Shimla",
    "state": "Himachal Pradesh",
    "lat": 31.1048,
    "lon": 77.1734
  },
  "173": {
    "market": "Solan",
    "district": "Solan",
    "state": "Himachal Pradesh",
    "lat": 30.9045,
    "lon": 77.0967
  },
  "175": {
    "market": "Shimla",
    "district": "Mandi",
    "state": "Himachal Pradesh",
    "lat": 31.7087,
    "lon": 76.932
  },
  "180": {
    "market": "Jammu",
    "district": "Jammu",
    "state": "Jammu and Kashmir",
    "lat": 32.7266,
    "lon": 74.857
  },
  "190": {
    "market": "Jammu",
    "district": "Srinagar",
    "state": "Jammu and Kashmir",
    "lat": 34.0837,
    "lon": 74.7973
  },
  "193": {
    "market": "Sopore",
    "district": "Baramulla",
    "state": "Jammu and Kashmir",
    "lat": 34.2987,
    "lon": 74.4691
  },
  "201": {
    "market": "Agra",
    "district": "Ghaziabad",
    "state": "Uttar Pradesh",
    "lat": 28.6692,
    "lon": 77.4538
  },
  "202": {
    "market": "Agra",
    "district": "Aligarh",
    "state": "Uttar Pradesh",
    "lat": 27.8974,
    "lon": 78.088
  },
  "208": {
    "market": "Kanpur",
    "district": "Kanpur Nagar",
    "state": "Uttar Pradesh",
    "lat": 26.4499,
    "lon": 80.3319
  },
  "221": {
    "market": "Varanasi",
    "district": "Varanasi",
    "state": "Uttar Pradesh",
    "lat": 25.3176,
    "lon": 82.9739
  },
  "226": {
    "market": "Lucknow",
    "district": "Lucknow",
    "state": "Uttar Pradesh",
    "lat": 26.8467,
    "lon": 80.9462
  },
  "243": {
    "market": "Agra",
    "district": "Bareilly",
    "state": "Uttar Pradesh",
    "lat": 28.367,
    "lon": 79.4304
  },
  "248": {
    "market": "Haridwar",
    "district": "Dehradun",
    "state": "Uttarakhand",
    "lat": 30.3165,
    "lon": 78.0322
  },
  "249": {
    "market": "Haridwar",
    "district": "Haridwar",
    "state": "Uttarakhand",
    "lat": 29.9457,
    "lon": 78.1642
  },
  "250": {
    "market": "Agra",
    "district": "Meerut",
    "state": "Uttar Pradesh",
    "lat": 28.9845,
    "lon": 77.7064
  },
  "263": {
    "market": "Haldwani",
    "district": "Nainital",
    "state": "Uttarakhand",
    "lat": 29.2183,
    "lon": 79.513
  },
  "273": {
    "market": "Kanpur",
    "district": "Gorakhpur",
    "state": "Uttar Pradesh",
    "lat": 26.7606,
    "lon": 83.3732
  },
  "281": {
    "market": "Agra",
    "district": "Mathura",
    "state": "Uttar Pradesh",
    "lat": 27.4924,
    "lon": 77.6737
  },
  "282": {
    "market": "Agra",
    "district": "Agra",
    "state": "Uttar Pradesh",
    "lat": 27.1767,
    "lon": 78.0081
  },
  "301": {
    "market": "Alwar",
    "district": "Alwar",
    "state": "Rajasthan",
    "lat": 27.553,
    "lon": 76.6346
  },
  "302": {
    "market": "Jaipur",
    "district": "Jaipur",
    "state": "Rajasthan",
    "lat": 26.9124,
    "lon": 75.7873
  },
  "305": {
    "market": "Jaipur",
    "district": "Ajmer",
    "state": "Rajasthan",
    "lat": 26.4499,
    "lon": 74.6399
  },
  "313": {
    "market": "Kota",
    "district": "Udaipur",
    "state": "Rajasthan",
    "lat": 24.5854,
    "lon": 73.7125
  },
  "324": {
    "market": "Kota",
    "district": "Kota",
    "state": "Rajasthan",
    "lat": 25.1328,
    "lon": 75.8458
  },
  "325": {
    "market": "Baran",
    "district": "Baran",
    "state": "Rajasthan",
    "lat": 25.1011,
    "lon": 76.5132
  },
  "334": {
    "market": "Bikaner",
    "district": "Bikaner",
    "state": "Rajasthan",
    "lat": 28.0229,
    "lon": 73.3119
  },
  "335": {
    "market": "Sri Ganganagar",
    "district": "Sri Ganganagar",
    "state": "Rajasthan",
    "lat": 29.9038,
    "lon": 73.8772
  },
  "341": {
    "market": "Nagaur",
    "district": "Nagaur",
    "state": "Rajasthan",
    "lat": 27.207,
    "lon": 73.7423
  },
  "342": {
    "market": "Jodhpur",
    "district": "Jodhpur",
    "state": "Rajasthan",
    "lat": 26.2389,
    "lon": 73.0243
  },
  "360": {
    "market": "Rajkot",
    "district": "Rajkot",
    "state": "Gujarat",
    "lat": 22.3486,
    "lon": 70.8122
  },
  "361": {
    "market": "Jamnagar",
    "district": "Jamnagar",
    "state": "Gujarat",
    "lat": 22.4707,
    "lon": 70.0577
  },
  "362": {
    "market": "Junagadh",
    "district": "Junagadh",
    "state": "Gujarat",
    "lat": 21.5222,
    "lon": 70.4579
  },
  "363": {
    "market": "Morbi",
    "district": "Morbi",
    "state": "Gujarat",
    "lat": 22.812,
    "lon": 70.8384
  },
  "365": {
    "market": "Amreli",
    "district": "Amreli",
    "state": "Gujarat",
    "lat": 21.6032,
    "lon": 71.2221
  },
  "370": {
    "market": "Rajkot",
    "district": "Kutch",
    "state": "Gujarat",
    "lat": 23.242,
    "lon": 69.6669
  },
  "380": {
    "market": "Ahmedabad",
    "district": "Ahmedabad",
    "state": "Gujarat",
    "lat": 23.0225,
    "lon": 72.5714
  },
  "384": {
    "market": "Unjha",
    "district": "Mehsana",
    "state": "Gujarat",
    "lat": 23.8042,
    "lon": 72.3962
  },
  "385": {
    "market": "Deesa",
    "district": "Banaskantha",
    "state": "Gujarat",
    "lat": 24.2584,
    "lon": 72.1812
  },
  "390": {
    "market": "Surat",
    "district": "Vadodara",
    "state": "Gujarat",
    "lat": 22.3072,
    "lon": 73.1812
  },
  "395": {
    "market": "Surat",
    "district": "Surat",
    "state": "Gujarat",
    "lat": 21.1702,
    "lon": 72.8311
  },
  "400": {
    "market": "Vashi",
    "district": "Thane",
    "state": "Maharashtra",
    "lat": 19.0771,
    "lon": 73.0039
  },
  "401": {
    "market": "Palghar",
    "district": "Palghar",
    "state": "Maharashtra",
    "lat": 19.6967,
    "lon": 72.7699
  },
  "402": {
    "market": "Panvel",
    "district": "Raigad",
    "state": "Maharashtra",
    "lat": 18.5158,
    "lon": 73.1822
  },
  "403": {
    "market": "Ponda",
    "district": "North Goa",
    "state": "Goa",
    "lat": 15.4026,
    "lon": 74.0151
  },
  "410": {
    "market": "Panvel",
    "district": "Raigad",
    "state": "Maharashtra",
    "lat": 18.9894,
    "lon": 73.1175
  },
  "411": {
    "market": "Pune",
    "district": "Pune",
    "state": "Maharashtra",
    "lat": 18.5204,
    "lon": 73.8567
  },
  "412": {
    "market": "Baramati",
    "district": "Pune",
    "state": "Maharashtra",
    "lat": 18.1511,
    "lon": 74.5772
  },
  "413": {
    "market": "Solapur",
    "district": "Solapur",
    "state": "Maharashtra",
    "lat": 17.6599,
    "lon": 75.9064
  },
  "4135": {
    "market": "Latur",
    "district": "Latur",
    "state": "Maharashtra",
    "lat": 18.4088,
    "lon": 76.5604
  },
  "414": {
    "market": "Ahmednagar",
    "district": "Ahmednagar",
    "state": "Maharashtra",
    "lat": 19.0952,
    "lon": 74.7496
  },
  "415": {
    "market": "Pune",
    "district": "Satara",
    "state": "Maharashtra",
    "lat": 17.6805,
    "lon": 73.9939
  },
  "416": {
    "market": "Sangli",
    "district": "Sangli",
    "state": "Maharashtra",
    "lat": 16.8524,
    "lon": 74.5815
  },
  "421": {
    "market": "Kalyan",
    "district": "Thane",
    "state": "Maharashtra",
    "lat": 19.2403,
    "lon": 73.1305
  },
  "422": {
    "market": "Nashik",
    "district": "Nashik",
    "state": "Maharashtra",
    "lat": 20.011,
    "lon": 73.7903
  },
  "423": {
    "market": "Nashik",
    "district": "Nashik",
    "state": "Maharashtra",
    "lat": 20.5539,
    "lon": 74.5288
  },
  "424": {
    "market": "Nashik",
    "district": "Dhule",
    "state": "Maharashtra",
    "lat": 20.9042,
    "lon": 74.7749
  },
  "425": {
    "market": "Jalgaon",
    "district": "Jalgaon",
    "state": "Maharashtra",
    "lat": 21.0077,
    "lon": 75.5626
  },
  "431": {
    "market": "Ahmednagar",
    "district": "Chhatrapati Sambhajinagar",
    "state": "Maharashtra",
    "lat": 19.8762,
    "lon": 75.3433
  },
  "440": {
    "market": "Nagpur",
    "district": "Nagpur",
    "state": "Maharashtra",
    "lat": 21.1458,
    "lon": 79.0882
  },
  "442": {
    "market": "Nagpur",
    "district": "Wardha",
    "state": "Maharashtra",
    "lat": 20.7453,
    "lon": 78.6022
  },
  "444": {
    "market": "Akola",
    "district": "Akola",
    "state": "Maharashtra",
    "lat": 20.7002,
    "lon": 77.0082
  },
  "445": {
    "market": "Akola",
    "district": "Yavatmal",
    "state": "Maharashtra",
    "lat": 20.3888,
    "lon": 78.1204
  },
  "450": {
    "market": "Khandwa",
    "district": "Khandwa",
    "state": "Madhya Pradesh",
    "lat": 21.8314,
    "lon": 76.3498
  },
  "451": {
    "market": "Khargone",
    "district": "Khargone",
    "state": "Madhya Pradesh",
    "lat": 21.8234,
    "lon": 75.6146
  },
  "452": {
    "market": "Indore",
    "district": "Indore",
    "state": "Madhya Pradesh",
    "lat": 22.6841,
    "lon": 75.8398
  },
  "455": {
    "market": "Dewas",
    "district": "Dewas",
    "state": "Madhya Pradesh",
    "lat": 22.9676,
    "lon": 76.0534
  },
  "456": {
    "market": "Ujjain",
    "district": "Ujjain",
    "state": "Madhya Pradesh",
    "lat": 23.1765,
    "lon": 75.7885
  },
  "457": {
    "market": "Ratlam",
    "district": "Ratlam",
    "state": "Madhya Pradesh",
    "lat": 23.3315,
    "lon": 75.0367
  },
  "458": {
    "market": "Mandsaur",
    "district": "Mandsaur",
    "state": "Madhya Pradesh",
    "lat": 24.0722,
    "lon": 75.0694
  },
  "461": {
    "market": "Harda",
    "district": "Harda",
    "state": "Madhya Pradesh",
    "lat": 22.3444,
    "lon": 77.0982
  },
  "462": {
    "market": "Sehore",
    "district": "Bhopal",
    "state": "Madhya Pradesh",
    "lat": 23.2599,
    "lon": 77.4126
  },
  "464": {
    "market": "Vidisha",
    "district": "Vidisha",
    "state": "Madhya Pradesh",
    "lat": 23.5251,
    "lon": 77.8081
  },
  "466": {
    "market": "Sehore",
    "district": "Sehore",
    "state": "Madhya Pradesh",
    "lat": 23.2032,
    "lon": 77.0844
  },
  "470": {
    "market": "Sagar",
    "district": "Sagar",
    "state": "Madhya Pradesh",
    "lat": 23.8388,
    "lon": 78.7378
  },
  "474": {
    "market": "Sagar",
    "district": "Gwalior",
    "state": "Madhya Pradesh",
    "lat": 26.2183,
    "lon": 78.1828
  },
  "482": {
    "market": "Jabalpur",
    "district": "Jabalpur",
    "state": "Madhya Pradesh",
    "lat": 23.1815,
    "lon": 79.9864
  },
  "491": {
    "market": "Rajnandgaon",
    "district": "Rajnandgaon",
    "state": "Chhattisgarh",
    "lat": 21.0974,
    "lon": 81.0375
  },
  "492": {
    "market": "Raipur",
    "district": "Raipur",
    "state": "Chhattisgarh",
    "lat": 21.2514,
    "lon": 81.6296
  },
  "495": {
    "market": "Raipur",
    "district": "Bilaspur",
    "state": "Chhattisgarh",
    "lat": 22.0797,
    "lon": 82.1409
  },
  "500": {
    "market": "Hyderabad",
    "district": "Hyderabad",
    "state": "Telangana",
    "lat": 17.385,
    "lon": 78.4867
  },
  "503": {
    "market": "Nizamabad",
    "district": "Nizamabad",
    "state": "Telangana",
    "lat": 18.6725,
    "lon": 78.0941
  },
  "505": {
    "market": "Warangal",
    "district": "Karimnagar",
    "state": "Telangana",
    "lat": 18.4386,
    "lon": 79.1288
  },
  "506": {
    "market": "Warangal",
    "district": "Warangal",
    "state": "Telangana",
    "lat": 17.9784,
    "lon": 79.5941
  },
  "517": {
    "market": "Guntur",
    "district": "Tirupati",
    "state": "Andhra Pradesh",
    "lat": 13.6288,
    "lon": 79.4192
  },
  "518": {
    "market": "Kurnool",
    "district": "Kurnool",
    "state": "Andhra Pradesh",
    "lat": 15.8281,
    "lon": 78.0373
  },
  "520": {
    "market": "Guntur",
    "district": "Vijayawada",
    "state": "Andhra Pradesh",
    "lat": 16.5062,
    "lon": 80.648
  },
  "522": {
    "market": "Guntur",
    "district": "Guntur",
    "state": "Andhra Pradesh",
    "lat": 16.3067,
    "lon": 80.4365
  },
  "530": {
    "market": "Guntur",
    "district": "Visakhapatnam",
    "state": "Andhra Pradesh",
    "lat": 17.6868,
    "lon": 83.2185
  },
  "560": {
    "market": "Bengaluru",
    "district": "Bengaluru Urban",
    "state": "Karnataka",
    "lat": 12.9716,
    "lon": 77.5946
  },
  "570": {
    "market": "Bengaluru",
    "district": "Mysuru",
    "state": "Karnataka",
    "lat": 12.2958,
    "lon": 76.6394
  },
  "575": {
    "market": "Hubballi",
    "district": "Dakshina Kannada",
    "state": "Karnataka",
    "lat": 12.9141,
    "lon": 74.856
  },
  "577": {
    "market": "Davanagere",
    "district": "Davanagere",
    "state": "Karnataka",
    "lat": 14.4644,
    "lon": 75.9218
  },
  "580": {
    "market": "Hubballi",
    "district": "Dharwad",
    "state": "Karnataka",
    "lat": 15.3647,
    "lon": 75.124
  },
  "583": {
    "market": "Davanagere",
    "district": "Bellary",
    "state": "Karnataka",
    "lat": 15.1394,
    "lon": 76.9214
  },
  "585": {
    "market": "Hubballi",
    "district": "Kalaburagi",
    "state": "Karnataka",
    "lat": 17.3297,
    "lon": 76.8343
  },
  "590": {
    "market": "Hubballi",
    "district": "Belagavi",
    "state": "Karnataka",
    "lat": 15.8497,
    "lon": 74.4977
  },
  "600": {
    "market": "Chennai",
    "district": "Chennai",
    "state": "Tamil Nadu",
    "lat": 13.0827,
    "lon": 80.2707
  },
  "605": {
    "market": "Puducherry",
    "district": "Puducherry",
    "state": "Puducherry",
    "lat": 11.9416,
    "lon": 79.8083
  },
  "620": {
    "market": "Dindigul",
    "district": "Tiruchirappalli",
    "state": "Tamil Nadu",
    "lat": 10.7905,
    "lon": 78.7047
  },
  "624": {
    "market": "Dindigul",
    "district": "Dindigul",
    "state": "Tamil Nadu",
    "lat": 10.3673,
    "lon": 77.9803
  },
  "625": {
    "market": "Dindigul",
    "district": "Madurai",
    "state": "Tamil Nadu",
    "lat": 9.9252,
    "lon": 78.1198
  },
  "627": {
    "market": "Dindigul",
    "district": "Tirunelveli",
    "state": "Tamil Nadu",
    "lat": 8.7139,
    "lon": 77.7567
  },
  "636": {
    "market": "Erode",
    "district": "Salem",
    "state": "Tamil Nadu",
    "lat": 11.6643,
    "lon": 78.146
  },
  "638": {
    "market": "Erode",
    "district": "Erode",
    "state": "Tamil Nadu",
    "lat": 11.341,
    "lon": 77.7172
  },
  "641": {
    "market": "Coimbatore",
    "district": "Coimbatore",
    "state": "Tamil Nadu",
    "lat": 11.0168,
    "lon": 76.9558
  },
  "670": {
    "market": "Palakkad",
    "district": "Kannur",
    "state": "Kerala",
    "lat": 11.8745,
    "lon": 75.3704
  },
  "673": {
    "market": "Palakkad",
    "district": "Kozhikode",
    "state": "Kerala",
    "lat": 11.2588,
    "lon": 75.7804
  },
  "678": {
    "market": "Palakkad",
    "district": "Palakkad",
    "state": "Kerala",
    "lat": 10.7867,
    "lon": 76.6548
  },
  "680": {
    "market": "Kochi",
    "district": "Thrissur",
    "state": "Kerala",
    "lat": 10.5276,
    "lon": 76.2144
  },
  "682": {
    "market": "Kochi",
    "district": "Ernakulam",
    "state": "Kerala",
    "lat": 9.9312,
    "lon": 76.2673
  },
  "686": {
    "market": "Kochi",
    "district": "Kottayam",
    "state": "Kerala",
    "lat": 9.5916,
    "lon": 76.5222
  },
  "695": {
    "market": "Kochi",
    "district": "Thiruvananthapuram",
    "state": "Kerala",
    "lat": 8.5241,
    "lon": 76.9366
  },
  "700": {
    "market": "Kolkata",
    "district": "Kolkata",
    "state": "West Bengal",
    "lat": 22.5726,
    "lon": 88.3639
  },
  "711": {
    "market": "Kolkata",
    "district": "Howrah",
    "state": "West Bengal",
    "lat": 22.5958,
    "lon": 88.2636
  },
  "713": {
    "market": "Burdwan",
    "district": "Purba Bardhaman",
    "state": "West Bengal",
    "lat": 23.2324,
    "lon": 87.8615
  },
  "721": {
    "market": "Burdwan",
    "district": "Paschim Medinipur",
    "state": "West Bengal",
    "lat": 22.4257,
    "lon": 87.3199
  },
  "734": {
    "market": "Siliguri",
    "district": "Darjeeling",
    "state": "West Bengal",
    "lat": 26.7271,
    "lon": 88.3953
  },
  "737": {
    "market": "Gangtok",
    "district": "East Sikkim",
    "state": "Sikkim",
    "lat": 27.3314,
    "lon": 88.6138
  },
  "751": {
    "market": "Bhubaneswar",
    "district": "Khordha",
    "state": "Odisha",
    "lat": 20.2961,
    "lon": 85.8245
  },
  "753": {
    "market": "Cuttack",
    "district": "Cuttack",
    "state": "Odisha",
    "lat": 20.4625,
    "lon": 85.8828
  },
  "768": {
    "market": "Bargarh",
    "district": "Bargarh",
    "state": "Odisha",
    "lat": 21.333,
    "lon": 83.6219
  },
  "769": {
    "market": "Sambalpur",
    "district": "Sambalpur",
    "state": "Odisha",
    "lat": 21.4669,
    "lon": 83.9812
  },
  "781": {
    "market": "Guwahati",
    "district": "Kamrup",
    "state": "Assam",
    "lat": 26.1445,
    "lon": 91.7362
  },
  "782": {
    "market": "Nagaon",
    "district": "Nagaon",
    "state": "Assam",
    "lat": 26.3468,
    "lon": 92.684
  },
  "786": {
    "market": "Guwahati",
    "district": "Dibrugarh",
    "state": "Assam",
    "lat": 27.4728,
    "lon": 94.912
  },
  "791": {
    "market": "Pasighat",
    "district": "East Siang",
    "state": "Arunachal Pradesh",
    "lat": 28.0668,
    "lon": 95.3268
  },
  "793": {
    "market": "Shillong",
    "district": "East Khasi Hills",
    "state": "Meghalaya",
    "lat": 25.5788,
    "lon": 91.8933
  },
  "795": {
    "market": "Imphal",
    "district": "Imphal West",
    "state": "Manipur",
    "lat": 24.817,
    "lon": 93.9368
  },
  "796": {
    "market": "Aizawl",
    "district": "Aizawl",
    "state": "Mizoram",
    "lat": 23.7271,
    "lon": 92.7176
  },
  "797": {
    "market": "Dimapur",
    "district": "Dimapur",
    "state": "Nagaland",
    "lat": 25.9095,
    "lon": 93.7266
  },
  "799": {
    "market": "Agartala",
    "district": "West Tripura",
    "state": "Tripura",
    "lat": 23.8315,
    "lon": 91.2868
  },
  "800": {
    "market": "Patna",
    "district": "Patna",
    "state": "Bihar",
    "lat": 25.5941,
    "lon": 85.1376
  },
  "823": {
    "market": "Patna",
    "district": "Gaya",
    "state": "Bihar",
    "lat": 24.7914,
    "lon": 85.0002
  },
  "826": {
    "market": "Ranchi",
    "district": "Dhanbad",
    "state": "Jharkhand",
    "lat": 23.7957,
    "lon": 86.4304
  },
  "831": {
    "market": "Ranchi",
    "district": "East Singhbhum",
    "state": "Jharkhand",
    "lat": 22.8046,
    "lon": 86.2029
  },
  "834": {
    "market": "Ranchi",
    "district": "Ranchi",
    "state": "Jharkhand",
    "lat": 23.3441,
    "lon": 85.3096
  },
  "842": {
    "market": "Patna",
    "district": "Muzaffarpur",
    "state": "Bihar",
    "lat": 26.1209,
    "lon": 85.3647
  },
  "854": {
    "market": "Gulabbagh",
    "district": "Purnea",
    "state": "Bihar",
    "lat": 25.7771,
    "lon": 87.5186
  }
}


class WeatherFetcher:

    @staticmethod
    def get_advisory(rain_prob, code, temp, wind):
        """
        Determines actionable farmer advisory and risk status based on:
        - Rain probability (%)
        - WMO weather code
        - Temperature (°C)
        - Wind speed (km/h)
        """
        # WMO Weather Interpretation Codes (WW):
        # 51, 53, 55: Drizzle
        # 56, 57: Freezing drizzle
        # 61, 63, 65: Rain
        # 66, 67: Freezing rain
        # 71, 73, 75, 77: Snow
        # 80, 81, 82: Rain showers
        # 85, 86: Snow showers
        # 95, 96, 99: Thunderstorm / Hail
        is_thunderstorm = code in [95, 96, 99]
        is_heavy_rain = code in [63, 65, 81, 82] or rain_prob >= 75
        is_rain = code in [51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82] or rain_prob >= 50

        if is_thunderstorm or is_heavy_rain:
            return {
                "status": "warning",
                "advisory_hi": "भारी बारिश / आंधी की चेतावनी। माल तिरपाल (ताड़पत्री) से अच्छी तरह ढकें व जलभराव से बचाएं।",
                "advisory_en": "High rain / storm warning. Keep crops securely covered with tarpaulin and protect from waterlogging.",
                "advisory_mr": "मुसळधार पाऊस / वादळाचा इशारा. शेतमाल ताडपत्रीने सुरक्षित झाकून ठेवा व पाणी साचू देऊ नका."
            }
        elif is_rain:
            return {
                "status": "caution",
                "advisory_hi": "बारिश की संभावना। मंडी ले जाते समय माल ढकने हेतु तिरपाल साथ अवश्य रखें।",
                "advisory_en": "Rain likely. Carry tarpaulin to cover produce while transporting and at the mandi.",
                "advisory_mr": "पावसाची शक्यता. शेतमाल बाजारात नेताना झाकण्यासाठी ताडपत्री सोबत अवश्य ठेवा."
            }
        elif temp >= 40:
            return {
                "status": "caution",
                "advisory_hi": "अत्यधिक गर्मी व तेज धूप। माल को छायादार स्थान पर रखें ताकि वजन व ताजगी बनी रहे।",
                "advisory_en": "Extreme heat and sun. Keep produce shaded to avoid dehydration and weight loss.",
                "advisory_mr": "तीव्र उष्णता व ऊन. शेतमाल सावलीत ठेवा जेणेकरून ओलावा व प्रत टिकून राहील."
            }
        else:
            return {
                "status": "safe",
                "advisory_hi": "मौसम साफ व अनुकूल है। मंडी में फसल लाने व सुखाने के लिए उत्तम समय।",
                "advisory_en": "Clear and favorable weather. Safe to bring crops to mandi yard.",
                "advisory_mr": "हवामान स्वच्छ व अनुकूल आहे. शेतमाल बाजारात आणण्यासाठी उत्तम वेळ."
            }

    @staticmethod
    def fetch_all_weather(batch_size=50, timeout=10):
        """
        Batch queries Open-Meteo for all unique APMC geo-coordinates.
        Returns a dict mapping lowercase mandi/district keys to weather data.
        """
        # Deduplicate coordinates into unique lat/lon pairs
        loc_map = {}
        for key, info in APMC_COORDINATES.items():
            lat = round(info['lat'], 3)
            lon = round(info['lon'], 3)
            loc_key = (lat, lon)
            if loc_key not in loc_map:
                loc_map[loc_key] = {
                    'lat': lat,
                    'lon': lon,
                    'entries': []
                }
            loc_map[loc_key]['entries'].append(info)

        unique_locs = list(loc_map.values())
        print(f"[WEATHER] Deduplicated into {len(unique_locs)} unique geographic coordinate clusters.")

        weather_by_key = {}
        successful_batches = 0

        for i in range(0, len(unique_locs), batch_size):
            batch = unique_locs[i:i + batch_size]
            lats = [b['lat'] for b in batch]
            lons = [b['lon'] for b in batch]

            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": lats,
                "longitude": lons,
                "current": ["temperature_2m", "relative_humidity_2m", "weather_code", "wind_speed_10m"],
                "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min", "precipitation_probability_max"],
                "timezone": "Asia/Kolkata",
                "forecast_days": 1
            }

            try:
                resp = requests.get(url, params=params, timeout=timeout)
                if resp.status_code != 200:
                    print(f"[WEATHER WARN] Open-Meteo returned status {resp.status_code} for batch {i // batch_size + 1}")
                    continue

                data = resp.json()
                items = data if isinstance(data, list) else [data]

                for idx, item in enumerate(items):
                    if idx >= len(batch):
                        break

                    curr = item.get("current", {})
                    daily = item.get("daily", {})

                    temp = round(curr.get("temperature_2m", 25.0))
                    max_t = round(daily.get("temperature_2m_max", [temp])[0])
                    min_t = round(daily.get("temperature_2m_min", [temp])[0])
                    humidity = round(curr.get("relative_humidity_2m", 50))
                    code = curr.get("weather_code", 0)
                    rain_prob = daily.get("precipitation_probability_max", [0])[0] or 0
                    wind = round(curr.get("wind_speed_10m", 0.0), 1)

                    advisory_info = WeatherFetcher.get_advisory(rain_prob, code, temp, wind)

                    weather_obj = {
                        "temp": temp,
                        "max_temp": max_t,
                        "min_temp": min_t,
                        "humidity": humidity,
                        "code": code,
                        "rain_prob": rain_prob,
                        "wind": wind,
                        "status": advisory_info["status"],
                        "advisory_hi": advisory_info["advisory_hi"],
                        "advisory_en": advisory_info["advisory_en"],
                        "advisory_mr": advisory_info["advisory_mr"]
                    }

                    for entry in batch[idx]['entries']:
                        m = entry.get('market', '').strip().lower()
                        d = entry.get('district', '').strip().lower()
                        if m:
                            weather_by_key[m] = weather_obj
                        if d:
                            weather_by_key[d] = weather_obj

                successful_batches += 1

            except Exception as e:
                print(f"[WEATHER ERROR] Batch {i // batch_size + 1} request failed: {e}")

        print(f"[WEATHER] Successfully fetched {successful_batches} batches, total {len(weather_by_key)} mapped keys.")
        return weather_by_key

    @staticmethod
    def fetch_and_save_weather(out_path=None):
        """
        Coordinates fetching and safely writing weather.json.
        Preserves existing weather.json if live fetch yields no records.
        """
        if out_path is None:
            out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "weather.json")

        existing_data = None
        if os.path.exists(out_path):
            try:
                with open(out_path, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
            except Exception:
                pass

        try:
            weather_map = WeatherFetcher.fetch_all_weather()
            if not weather_map:
                if existing_data:
                    print("[WEATHER] Fetch returned 0 records. Retaining existing cached weather.json.")
                    return True
                print("[WEATHER ERROR] No weather records fetched and no existing file.")
                return False

            payload = {
                "weather": weather_map,
                "generated_at": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                "total_locations": len(weather_map)
            }

            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, separators=(',', ':'))

            print(f"[WEATHER SUCCESS] Generated {out_path} with {len(weather_map)} locations.")
            return True

        except Exception as e:
            print(f"[WEATHER EXCEPTION] Failed to generate weather.json: {e}")
            if existing_data:
                print("[WEATHER] Retaining existing weather.json after exception.")
                return True
            return False


if __name__ == "__main__":
    WeatherFetcher.fetch_and_save_weather()
