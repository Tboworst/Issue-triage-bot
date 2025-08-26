from app import app, create_app

# Initialize the application
create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)