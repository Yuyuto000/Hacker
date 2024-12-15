from flask import jsonify

dashboard_data = {
    "active_connections": 0,
    "vpn_status": "inactive",
    "proxy_status": "inactive",
    "logs": []
}

def update_dashboard(key, value):
    dashboard_data[key] = value

def get_dashboard_data():
    return dashboard_data

def init_dashboard(app):
    @app.route('/dashboard', methods=['GET'])
    def serve_dashboard():
        return jsonify(get_dashboard_data()), 200
