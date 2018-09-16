from flask import Flask, render_template, request
import requests
import json
import sqlite3
import get_hotels_airports as util

app = Flask(__name__)

db_name = 'DisasterRelief.db'

conn = sqlite3.connect(db_name)
conn.execute('''CREATE TABLE IF NOT EXISTS SUPPLIES
         (NAME TEXT NOT NULL,
         PHONE TEXT NOT NULL,
         LOCATION TEXT NOT NULL,
         SUPPLY TEXT NOT NULL);''')
             
conn.commit()
conn.close()

db2_name = 'Requests.db'

conn2 = sqlite3.connect(db2_name)
conn2.execute('''CREATE TABLE IF NOT EXISTS REQUESTS
         (NAME TEXT NOT NULL,
         PHONE TEXT NOT NULL,
         LOCATION TEXT NOT NULL,
         ITEM TEXT NOT NULL);''')
             
conn2.commit()
conn2.close()

@app.route("/")
def main():
    return render_template('index.html')

@app.route('/alerts')
def alerts():
    api_key = '9d2908c81003444ea908c81003b44ed4'

    base_url = 'https://api.weather.com/v2/stormreports'
    parameters = {'format': 'json', 'apiKey': api_key}

    response = requests.get(base_url, params = parameters)
    data = json.loads(response.content)
    stormreports = data['stormreports']
    
    s = ""
    
    for i in stormreports:
        if i['severity'] == 10:
            s += i['geo_name'] + ", " + i['location'] + ", " + i['state_code']
            s += '<br>' + i['event_type'] + ': ' + i['comments'] 
            s += '<br>' + "LATITUDE: " + str(i['latitude']) + ", LONGITUDE: " + str(i['longitude']) +'<br>' + '<br>'
    return render_template('alerts.html', data = s)

@app.route('/show_signup')
def show_signup():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup():
    # read the posted values from the UI
    if request.method == 'POST':
      try:
         nm = request.form['name']
         ph = request.form['phone']
         loc = request.form['location']
         sup = request.form['supply']
         
         with sqlite3.connect(db_name) as con:
            cur = con.cursor()
            cur.execute("INSERT INTO SUPPLIES (NAME,PHONE,LOCATION,SUPPLY) VALUES (?,?,?,?)",(nm,ph,loc,sup))
            
            con.commit()
            msg = "Successfully added! Thank you for your contribution! "
      except Exception as e:
         con.rollback()
         msg = "Error in insert operation: " + str(e)
      
      finally:
         return render_template("signup.html",msg = msg)
         con.close()
    
@app.route('/show_available_supplies')
def show_available_supplies():
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    
    cur = conn.cursor()
    cur.execute("SELECT * FROM SUPPLIES")
   
    rows = cur.fetchall(); 
    conn.close()
    return render_template('available.html', rows=rows)


@app.route('/search_result', methods=['POST'])
def search_result():
    requested = request.form['supply']
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    
    cur = conn.cursor()
    cur.execute("SELECT * FROM SUPPLIES WHERE SUPPLY=? ORDER BY LOCATION", (requested,))
    
    rows = cur.fetchall();
    conn.close()
    return render_template('search_result.html', rows = rows)

@app.route('/search_result2', methods=['POST'])
def search_result2():
    requested = request.form['item']
    conn = sqlite3.connect(db2_name)
    conn.row_factory = sqlite3.Row
    
    cur = conn.cursor()
    cur.execute("SELECT * FROM REQUESTS WHERE ITEM=? ORDER BY LOCATION", (requested,))
    
    rows = cur.fetchall();
    conn.close()
    return render_template('search_result2.html', rows = rows)

@app.route('/show_requests')
def show_requests():
    return render_template('request_supplies.html')

@app.route('/request_supplies', methods=['POST'])
def request_supplies():
    # read the posted values from the UI
    if request.method == 'POST':
      try:
         nm = request.form['name']
         ph = request.form['phone']
         loc = request.form['location']
         item = request.form['item']
         
         with sqlite3.connect(db2_name) as con:
            cur = con.cursor()
            cur.execute("INSERT INTO REQUESTS (NAME,PHONE,LOCATION,ITEM) VALUES (?,?,?,?)",(nm,ph,loc,item))
            
            con.commit()
            msg = "Successfully added!"
      except Exception as e:
         con.rollback()
         msg = "Error in insert operation: " + str(e)
      
      finally:
         return render_template("request_supplies.html",msg = msg)
         con.close()
    
@app.route('/see_requests')
def see_requests():
    conn = sqlite3.connect(db2_name)
    conn.row_factory = sqlite3.Row
    
    cur = conn.cursor()
    cur.execute("SELECT * FROM REQUESTS")
   
    rows = cur.fetchall(); 
    conn.close()
    return render_template('see_requests.html', rows=rows)

@app.route('/get_flights', methods=['POST'])
def get_flights():
    origin = request.form['origin']
    lat = request.form['latitude']
    long = request.form['longitude']
    s = util.find_nearby_flights(util.find_airports(lat, long), origin_airport=origin)
    return render_template('flight_results.html', data=s)

if __name__ == "__main__":
    app.run()
