from flask import Flask, request, jsonify, redirect, url_for, render_template
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, update
from sqlalchemy.inspection import inspect
from utils import findIndex, update_adjacency_matrix, createSubGraph, dijkstra, getDist
# from flask_executor import Executor
from flask_socketio import SocketIO
import time
import threading
import select as sel
import psycopg2
import psycopg2.extensions

# Initialize flask app and configure the socket and database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Postgres#1234@localhost:5432/SmartCityData'
db = SQLAlchemy(app)
CORS(app, resoures={r"/endpoint":{"origins":"*"}})
socketio = SocketIO(app)

# --------------------------------------------------------------------------------------------------------------------------------------------

# functions that interact with th database

def getTrashVansLocation():
    # Fetch data from the TrashVan table of the database
    return [{
        "lat": 27.902966567198106,
        "lng": 78.07626253349594
    }]

# function called whenever there is a change in the table WasteBin of the database
def background_task():
    with app.app_context():
        db.session.begin()
        print("Background Task")
        trashVans = getTrashVansLocation()
        stmt = select(WasteBin)
        results = db.session.execute(stmt.order_by(WasteBin.bin_id)).scalars().all()
        print(results[0].bin_id, results[0].fill_status)
        pickupBins = [bin.bin_id for bin in results if bin.fill_status > 50.00]
        print(pickupBins)
        subGraph = createSubGraph(pickupBins)
        print(subGraph)
        temp = []
        for van in trashVans:
            coords = [[van['lng'], van['lat']]]
            for i in range(len(pickupBins)):
                bin = results[pickupBins[i]-1]
                dist = getDist(van, {"lat": bin.latitude, "lng": bin.longitude})
                temp.append(dist)
                subGraph[i].append(dist)
            temp.append(0.0)
            subGraph.append(temp)
            print(subGraph)
            _, visit_order = dijkstra(subGraph, len(subGraph)-1)
            print(visit_order)
            visit_order.pop(0)
            for bin in visit_order:
                coords.append([results[bin-1].longitude, results[bin-1].latitude])
            socketio.emit('database_update', {'data': [result.to_dict() for result in results], 'coords': coords}, namespace='/')

# --------------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------------

# sqlalchemy classes corresponding to the database tables

class WasteBin(db.Model):
    __tablename__ = 'WasteBin'
    bin_id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    height = db.Column(db.Float)
    capacity = db.Column(db.Float)
    fill_status = db.Column(db.Float)
    
    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

# --------------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------------

# Server routes

@app.route('/new_connection', methods=['POST'])
def register_new_bin():
    data = request.json
    print(f"Received data: {data}")
    print(f"latitude: {data['latitude']}")
    print(f"longitude: {data['longitude']}")
    print(f"bin_height: {data['bin_height']}")
    print(f"bin_capacity: {data['bin_capacity']}")
    
    new_bin = WasteBin(
        latitude=data['latitude'],
        longitude=data['longitude'],
        height=data['bin_height'],
        capacity=data['bin_capacity'],
        fill_status=0.0
    )
    
    try:
        db.session.add(new_bin)
        db.session.commit()
        response_data = {
            'status': 'success',
            'message': 'Bin successfully added to the database',
            'bin_id': new_bin.bin_id
        }
        stmt = select(WasteBin.bin_id, WasteBin.latitude, WasteBin.longitude)
        results = db.session.execute(stmt.order_by(WasteBin.bin_id)).all()
        start_vertex = 0
        if results[new_bin.bin_id-1].bin_id == new_bin.bin_id:
            start_vertex = new_bin.bin_id
        else:
            start_vertex = findIndex(results, new_bin.bin_id)
        update_adjacency_matrix(results, start_vertex)
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        response_data = {
            'status': 'fail',
            'message': error
        }
    
    return jsonify(response_data)

@app.route('/data', methods=['POST'])
def receive_data():
    data = request.json
    print(f"Received data: {data}")
    stmt = (
        update(WasteBin).
        where(WasteBin.bin_id == data['bin_id']).
        values(fill_status = data['percent_fill'])
    )
    db.session.execute(stmt)
    db.session.commit()
    
    return "Data received"

@app.route('/waste_bins', methods=['GET'])
def waste_bins():
    stmt = select(WasteBin)
    with db.session.begin():
        results = db.session.execute(stmt.order_by(WasteBin.bin_id)).scalars().all()
    return render_template("waste_bins.html", content = results)

@app.route('/home', methods=['GET'])
@cross_origin()
def home():
    stmt = select(WasteBin.bin_id, WasteBin.latitude, WasteBin.longitude)
    with db.session.begin():
        results = db.session.execute(stmt.order_by(WasteBin.bin_id)).all()
    markers = [{'lng': bin.longitude, 'lat': bin.latitude} for bin in results]
    return render_template("index.html", content = markers)

# --------------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------------

# Thread runningly continuously in the background, listening to any update in the database

def listen_for_notifications():
    print("listen_for_notifications function called")
    with app.app_context():
        conn = psycopg2.connect(database="SmartCityData", user="postgres", password="Postgres#1234", host="localhost", port="5432")
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

        curs = conn.cursor()
        curs.execute("LISTEN db_event;")

        while True:
            if sel.select([conn], [], [], 5) == ([], [], []):
                print("Timeout")
            else:
                conn.poll()
                while conn.notifies:
                    notify = conn.notifies.pop(0)
                    print("Got NOTIFY:", notify.pid, notify.channel, notify.payload)
                    
                    # Call the background task for the waste bin
                    background_task()

thread = threading.Thread(target=listen_for_notifications)
thread.start()

# --------------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    
    with app.app_context():
        socketio.run(app, host='0.0.0.0', port=5000)