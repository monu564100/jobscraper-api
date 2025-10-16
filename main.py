from app import create_app

app = create_app()

if __name__ == "__main__":
    # Listen on all interfaces (0.0.0.0) so mobile devices can access it
    app.run(host='0.0.0.0', port=5000, debug=False)
