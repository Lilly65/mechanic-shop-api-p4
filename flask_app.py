from mechanic_shop import create_app

app = create_app()

with app.app_context():
    from mechanic_shop import db
    db.create_all()
    print("Tables created.")

if __name__ == '__main__':
    app.run(debug=True)