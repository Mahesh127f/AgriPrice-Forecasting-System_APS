CROPS = {
    "veg": [
        "Onion","Tomato","Potato","Brinjal","Cabbage","Cauliflower","Carrot",
        "Radish","Spinach","Peas","Capsicum","Lady Finger (Bhindi)",
        "Bitter Gourd (Karela)","Bottle Gourd","Ridge Gourd","Pumpkin",
        "Green Chilli","Ginger","Garlic","Beetroot","Cucumber","Drumstick",
        "Tinda","Parwal","Turnip","Methi","Coriander Leaves","Mint"
    ],
    "fruit": [
        "Banana","Mango","Apple","Grapes","Orange","Papaya","Guava",
        "Watermelon","Muskmelon","Pomegranate","Pineapple","Litchi",
        "Sapota (Chiku)","Jackfruit","Coconut","Amla","Jamun","Pear",
        "Plum","Peach","Strawberry","Fig","Dates","Lemon","Mosambi"
    ],
    "pulse": [
        "Arhar Dal (Tur)","Chana (Chickpea)","Moong Dal","Masoor Dal",
        "Urad Dal","Rajma","Lobiya","Moth Bean","Horse Gram",
        "Green Peas","Field Peas","Lentil","Soybean","Groundnut"
    ],
    "spice": [
        "Turmeric","Red Chilli","Coriander Seed","Cumin (Jeera)",
        "Fennel (Saunf)","Fenugreek Seed","Black Pepper","Cardamom",
        "Clove","Mustard Seed","Dry Ginger","Dry Garlic","Ajwain",
        "Asafoetida (Hing)"
    ],
    "cereal": [
        "Wheat","Rice (Paddy)","Maize","Jowar","Bajra","Ragi","Barley",
        "Oats","Sunflower Seed","Mustard","Sesame (Til)","Linseed",
        "Castor Seed","Cotton"
    ]
}

ALL_CROPS = [c for crops in CROPS.values() for c in crops]

BASE_PRICES = {
    "Onion":2340,"Tomato":1820,"Potato":1150,"Brinjal":980,"Cabbage":720,
    "Cauliflower":850,"Carrot":1200,"Radish":480,"Spinach":560,"Peas":2800,
    "Capsicum":1800,"Lady Finger (Bhindi)":1100,"Bitter Gourd (Karela)":1400,
    "Bottle Gourd":620,"Ridge Gourd":750,"Pumpkin":540,"Green Chilli":2200,
    "Ginger":5400,"Garlic":6200,"Beetroot":880,"Cucumber":640,
    "Drumstick":3200,"Tinda":760,"Parwal":1100,"Turnip":520,"Methi":680,
    "Coriander Leaves":1800,"Mint":1200,
    "Banana":1200,"Mango":3800,"Apple":7200,"Grapes":4500,"Orange":2800,
    "Papaya":1100,"Guava":1500,"Watermelon":680,"Muskmelon":920,
    "Pomegranate":6800,"Pineapple":2200,"Litchi":5500,"Sapota (Chiku)":1800,
    "Jackfruit":1400,"Coconut":2200,"Amla":1800,"Jamun":3200,"Pear":3800,
    "Plum":4200,"Peach":4800,"Strawberry":8500,"Fig":6200,"Dates":12000,
    "Lemon":3200,"Mosambi":2400,
    "Arhar Dal (Tur)":7200,"Chana (Chickpea)":5800,"Moong Dal":8200,
    "Masoor Dal":6400,"Urad Dal":8800,"Rajma":9500,"Lobiya":6200,
    "Moth Bean":5800,"Horse Gram":5200,"Green Peas":3800,"Field Peas":3200,
    "Lentil":6800,"Soybean":4200,"Groundnut":5600,
    "Turmeric":8400,"Red Chilli":12000,"Coriander Seed":7200,
    "Cumin (Jeera)":22000,"Fennel (Saunf)":8800,"Fenugreek Seed":5200,
    "Black Pepper":38000,"Cardamom":95000,"Clove":62000,"Mustard Seed":5800,
    "Dry Ginger":18000,"Dry Garlic":14000,"Ajwain":12000,
    "Asafoetida (Hing)":45000,
    "Wheat":2200,"Rice (Paddy)":2100,"Maize":1900,"Jowar":2800,"Bajra":2200,
    "Ragi":3200,"Barley":1800,"Oats":2800,"Sunflower Seed":5200,
    "Mustard":5400,"Sesame (Til)":12000,"Linseed":5800,"Castor Seed":5600,
    "Cotton":7200
}

MSP_2024_25 = {
    "Wheat":2275,"Rice (Paddy)":2183,"Maize":2090,"Jowar":3180,
    "Bajra":2500,"Ragi":3846,"Arhar Dal (Tur)":7000,"Chana (Chickpea)":5440,
    "Moong Dal":8558,"Masoor Dal":6425,"Urad Dal":6950,"Soybean":4600,
    "Groundnut":6377,"Sunflower Seed":6760,"Mustard":5650,
    "Sesame (Til)":8635,"Cotton":6620,"Castor Seed":6170
}

STATES_MANDIS = {
    "Andhra Pradesh": ["Kurnool","Vijayawada","Guntur","Tirupati","Rajahmundry","Vizag","Nellore","Kadapa"],
    "Arunachal Pradesh": ["Itanagar","Naharlagun"],
    "Assam": ["Guwahati","Dibrugarh","Jorhat","Silchar","Tezpur"],
    "Bihar": ["Patna","Muzaffarpur","Gaya","Bhagalpur","Darbhanga","Hajipur","Chapra"],
    "Chhattisgarh": ["Raipur","Bilaspur","Durg","Jagdalpur","Korba"],
    "Goa": ["Panaji","Margao","Vasco","Mapusa"],
    "Gujarat": ["Ahmedabad","Rajkot","Surat","Vadodara","Junagadh","Gondal","Unjha","Deesa","Anand"],
    "Haryana": ["Karnal","Hisar","Rohtak","Ambala","Sirsa","Faridabad","Kurukshetra","Panipat"],
    "Himachal Pradesh": ["Shimla","Solan","Kullu","Mandi","Kangra","Dharamsala"],
    "Jharkhand": ["Ranchi","Jamshedpur","Dhanbad","Bokaro","Hazaribagh","Dumka"],
    "Karnataka": ["Bengaluru","Hubli","Mysuru","Davangere","Belgaum","Tumkur","Hassan","Udupi","Shivamogga"],
    "Kerala": ["Kochi","Thiruvananthapuram","Kozhikode","Thrissur","Palakkad","Kannur","Alappuzha"],
    "Madhya Pradesh": ["Indore","Bhopal","Jabalpur","Gwalior","Ujjain","Sagar","Ratlam","Mandsaur","Khandwa"],
    "Maharashtra": ["Nashik","Pune","Mumbai","Nagpur","Kolhapur","Solapur","Aurangabad","Nanded","Latur","Satara"],
    "Manipur": ["Imphal","Churachandpur"],
    "Meghalaya": ["Shillong","Tura","Jowai"],
    "Mizoram": ["Aizawl","Lunglei"],
    "Nagaland": ["Dimapur","Kohima","Mokokchung"],
    "Odisha": ["Bhubaneswar","Cuttack","Sambalpur","Berhampur","Rourkela","Balasore","Baripada"],
    "Punjab": ["Amritsar","Ludhiana","Jalandhar","Patiala","Bathinda","Khanna","Moga","Barnala"],
    "Rajasthan": ["Jaipur","Jodhpur","Kota","Udaipur","Ajmer","Alwar","Bikaner","Sikar","Nagaur"],
    "Sikkim": ["Gangtok","Namchi"],
    "Tamil Nadu": ["Chennai","Coimbatore","Madurai","Salem","Tiruchirapalli","Tirunelveli","Vellore","Erode","Dindigul","Hosur"],
    "Telangana": ["Hyderabad","Warangal","Nizamabad","Khammam","Karimnagar","Nalgonda","Adilabad"],
    "Tripura": ["Agartala","Udaipur"],
    "Uttar Pradesh": ["Agra","Lucknow","Kanpur","Varanasi","Allahabad","Meerut","Mathura","Aligarh","Gorakhpur","Moradabad","Bareilly","Jhansi"],
    "Uttarakhand": ["Dehradun","Haridwar","Haldwani","Roorkee","Rudrapur","Kashipur"],
    "West Bengal": ["Kolkata","Howrah","Siliguri","Asansol","Durgapur","Krishnanagar","Coochbehar","Medinipur"],
    "Delhi": ["Azadpur","Ghazipur","Okhla","Keshopur"],
    "Jammu & Kashmir": ["Jammu","Srinagar","Sopore","Anantnag","Baramulla"],
    "Ladakh": ["Leh","Kargil"],
    "Puducherry": ["Puducherry","Karaikal"],
    "Chandigarh": ["Chandigarh"],
    "Andaman & Nicobar": ["Port Blair"],
    "Dadra & Nagar Haveli": ["Silvassa"],
    "Lakshadweep": ["Kavaratti"]
}

MANDI_COORDS = {
    "Azadpur":     {"lat":28.74,"lng":77.17},
    "Agra":        {"lat":27.17,"lng":78.01},
    "Nashik":      {"lat":19.99,"lng":73.79},
    "Pune":        {"lat":18.52,"lng":73.86},
    "Hubli":       {"lat":15.36,"lng":75.12},
    "Bengaluru":   {"lat":12.97,"lng":77.59},
    "Hyderabad":   {"lat":17.38,"lng":78.47},
    "Chennai":     {"lat":13.08,"lng":80.27},
    "Kolkata":     {"lat":22.57,"lng":88.36},
    "Patna":       {"lat":25.59,"lng":85.13},
    "Lucknow":     {"lat":26.85,"lng":80.95},
    "Jaipur":      {"lat":26.91,"lng":75.79},
    "Surat":       {"lat":21.17,"lng":72.83},
    "Ahmedabad":   {"lat":23.03,"lng":72.58},
    "Indore":      {"lat":22.72,"lng":75.86},
    "Kochi":       {"lat":9.93,"lng":76.26},
    "Coimbatore":  {"lat":11.01,"lng":76.96},
    "Nagpur":      {"lat":21.15,"lng":79.09},
    "Amritsar":    {"lat":31.63,"lng":74.87},
    "Guwahati":    {"lat":26.14,"lng":91.74},
    "Bhopal":      {"lat":23.25,"lng":77.40},
    "Kanpur":      {"lat":26.46,"lng":80.33},
    "Varanasi":    {"lat":25.32,"lng":82.97},
    "Kurnool":     {"lat":15.83,"lng":78.04},
    "Vijayawada":  {"lat":16.51,"lng":80.64},
}

CATEGORY_MAP = {}
for cat, crops in CROPS.items():
    for crop in crops:
        CATEGORY_MAP[crop] = cat
