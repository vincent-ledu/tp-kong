from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/launcher/banana")
def banana():
    return "🍌"

@app.route("/launcher/cucumber")
def cucumber():
    return "🥒"

@app.route("/api/servers")
def getServersList():
    servers = [{"hostname": "host1", "ip": "10.1.1.1"}, {"hostname": "host2", "ip": "10.1.1.2"}]
    return jsonify(servers)

