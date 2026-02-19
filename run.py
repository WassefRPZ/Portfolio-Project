from app import create_app

app = create_app()

if __name__ == '__main__':
    print("Board Game Meetup API")
    print("http://127.0.0.1:5000")
    print("Routes disponibles sur /api/v1/")
    app.run(debug=True, port=5000)












