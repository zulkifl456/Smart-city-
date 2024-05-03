from flask import Flask,request,jsonify
app=Flask(__name__)
recieved_data=[]
@app.route('/results',methods=['POST'])
def handle_requests():
    data=request.get_json()
    if data is None:
        return jsonify({"error":"no data recieved"}),400
    print("recieved data",data)
    recieved_data.append(data)
    return jsonify({"message":"Data recieved successfully"}),200
@app.route('/data',methods=['GET'])
def get_data():
    return jsonify(recieved_data)
if __name__=="__main__":
    app.run(host='127.0.0.1',port=5001,debug=True)