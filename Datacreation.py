import pandas as pd
import random
from datetime import datetime, timedelta

# 1. Hospital Locations (Tamil Nadu)
hospitals = [
    {"name": "Govt Hospital Srivilliputhur", "city": "Srivilliputhur", "lat": 9.5105, "lon": 77.6330},
    {"name": "Madurai Medical College", "city": "Madurai", "lat": 9.9252, "lon": 78.1198},
    {"name": "Rajiv Gandhi Govt General Hospital", "city": "Chennai", "lat": 13.0827, "lon": 80.2707},
    {"name": "Coimbatore Medical College", "city": "Coimbatore", "lat": 11.0168, "lon": 76.9558},
    {"name": "Tirunelveli Medical College", "city": "Tirunelveli", "lat": 8.7139, "lon": 77.7567},
    {"name": "Apollo Speciality Hospitals", "city": "Trichy", "lat": 10.7905, "lon": 78.7047},
    {"name": "Salem Govt Hospital", "city": "Salem", "lat": 11.6643, "lon": 78.1460},
    {"name": "Thanjavur Medical College", "city": "Thanjavur", "lat": 10.7870, "lon": 79.1378},
]

# 2. Critical Supplies
supplies = [
    {"item": "Oxygen Cylinder (B-Type)", "category": "Respiratory", "min": 50},
    {"item": "Remdesivir Injection", "category": "Medicine", "min": 100},
    {"item": "Blood Bag (O+ Positive)", "category": "Blood Bank", "min": 20},
    {"item": "Surgical Gloves (Sterile)", "category": "Consumables", "min": 500},
    {"item": "Ventilator Circuit", "category": "Equipment", "min": 15},
    {"item": "N95 Masks", "category": "PPE", "min": 300},
    {"item": "Paracetamol IV", "category": "Medicine", "min": 200},
    {"item": "Insulin Vials", "category": "Medicine", "min": 150},
]

data = []

# 3. Generate 1000 Rows
for i in range(1000):
    hospital = random.choice(hospitals)
    supply = random.choice(supplies)
    
    # 15% chance of CRITICAL shortage
    if random.random() < 0.15:
        qty = random.randint(0, supply['min'] - 1)
        status = "CRITICAL"
    else:
        qty = random.randint(supply['min'], supply['min'] * 5)
        status = "Normal"

    # Expiry Date
    expiry = datetime.now() + timedelta(days=random.randint(5, 700))
    
    data.append({
        "Hospital_ID": f"HOSP-{1000+i}",
        "Hospital_Name": hospital["name"],
        "City": hospital["city"],
        "Latitude": hospital["lat"],
        "Longitude": hospital["lon"],
        "Item_Name": supply["item"],
        "Category": supply["category"],
        "Quantity_Available": qty,
        "Minimum_Required": supply['min'],
        "Status": status,
        "Expiry_Date": expiry.strftime("%Y-%m-%d")
    })

# 4. Save
df = pd.DataFrame(data)
df.to_csv("hospital_inventory.csv", index=False)
print("File 'hospital_inventory.csv' created successfully!")