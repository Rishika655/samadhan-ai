import folium
import sqlite3
import requests
import time
from folium.plugins import HeatMap

def get_coordinates(location_text):
    try:
        # using OpenStreetMap Nominatim - completely free, no API key needed
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': location_text + ', India',
            'format': 'json',
            'limit': 1
        }
        headers = {
            'User-Agent': 'ComplaintPlatform/1.0'
        }
        response = requests.get(url, params=params, headers=headers, timeout=5)
        data = response.json()
        
        if data:
            lat = float(data[0]['lat'])
            lng = float(data[0]['lon'])
            return [lat, lng]
        else:
            # default to Bankura if location not found
            return [23.2324, 87.0753]
    except:
        return [23.2324, 87.0753]

def generate_map():
    conn = sqlite3.connect('database/complaints.db')
    c = conn.cursor()
    c.execute("SELECT complaint, location, category, priority_score FROM complaints")
    complaints = c.fetchall()
    conn.close()

    # center map on India
    m = folium.Map(location=[20.5937, 78.9629], zoom_start=5)

    heat_data = []

    for complaint in complaints:
        text, location, category, score = complaint
        if score is None:
            score = 50

        # auto get coordinates from location name
        coords = get_coordinates(location)
        time.sleep(1)  # Nominatim requires 1 second delay between requests

        lat, lng = coords[0], coords[1]

        # color based on priority
        if score >= 80:
            color = 'red'
        elif score >= 50:
            color = 'orange'
        else:
            color = 'green'

        # add marker with popup
        folium.CircleMarker(
            location=[lat, lng],
            radius=8,
            color=color,
            fill=True,
            fill_opacity=0.7,
            popup=folium.Popup(
                f"<b>{category}</b><br>{text[:60]}...<br>📍 {location}<br>Priority: {score}/100",
                max_width=200
            )
        ).add_to(m)

        heat_data.append([lat, lng, score/100])

    # add heatmap layer
    if heat_data:
        HeatMap(heat_data, radius=25).add_to(m)

    # add legend
    legend_html = '''
    <div style="position: fixed; bottom: 30px; left: 30px; z-index: 1000;
                background: white; padding: 15px; border-radius: 8px;
                border: 2px solid grey; font-size: 14px;">
        <b>Priority Legend</b><br>
        🔴 High Priority (80+)<br>
        🟠 Medium Priority (50-79)<br>
        🟢 Low Priority (below 50)
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))

    m.save('templates/map.html')
    return True