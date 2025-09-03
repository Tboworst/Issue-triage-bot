from app import create_app
# instance for the appo driver 
app = create_app()

if __name__ == "__main__":
    # run the Flask dev server
    app.run(host="0.0.0.0", port=5000, debug=True)
