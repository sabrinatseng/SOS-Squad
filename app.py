from flask import Flask, render_template, request
import requests
import json
import sqlite3

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
            s += '<br>' + i['event_type'] + ': ' + i['comments'] + '<br>' + '<br>'
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
            msg = "Record successfully added"
      except Exception as e:
         con.rollback()
         msg = "error in insert operation: " + str(e)
      
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

if __name__ == "__main__":
    app.run()
