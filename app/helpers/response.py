from flask import jsonify

class ResponseHelper:
    @staticmethod
    def success_response(message, data):
        return jsonify({
            'status': 'success',
            'message': message,
            'data': data
        }), 200

    @staticmethod
    def failure_response(message, status_code=500):
        return jsonify({
            'status': 'failed',
            'message': message
        }), status_code
