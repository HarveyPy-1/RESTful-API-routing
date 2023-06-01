import random
from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired
import secrets

app = Flask(__name__)
secret = secrets.token_hex(16)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)


# class AddNewForm(FlaskForm):
#     name = StringField(validators=[DataRequired()])
#     map_url = StringField(validators=[DataRequired()])
#     img_url = StringField(validators=[DataRequired()])
#     location = StringField(validators=[DataRequired()])
#     has_sockets = BooleanField(validators=[DataRequired()])
#     has_toilet = BooleanField(validators=[DataRequired()])
#     has_wifi = BooleanField(validators=[DataRequired()])
#     can_take_calls = BooleanField(validators=[DataRequired()])
#     seats = StringField(validators=[DataRequired()])
#     coffee_price = StringField(validators=[DataRequired()])


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.get('/random')
def get_random():
    with app.app_context():
        db.create_all()
        all_cafes = Cafe.query.all()
        random_cafe = random.choice(all_cafes)
        cafe_dict = dict(random_cafe.__dict__)  # Turn that record object into a dictionary
        del cafe_dict['_sa_instance_state']  # Delete the "sa_instance_state" element because it is not iterable
        return jsonify(cafe=cafe_dict)

        # YOU CAN ALSO DECIDE TO WRITE IT OUT BELOW, SO YOU CAN EASILY OMIT SOME DETAILS YOU WAN'T TO HIDE, AS WELL
        # AS CREATE A SUB CATEGORY, SUCH AS 'AMENITIES' BEFORE THE HAS_TOILET, ETC SIDE
        # return jsonify(cafe={
        #     "id": random_cafe.id,
        #     "name": random_cafe.name,
        #     "map_url": random_cafe.map_url,
        #     "img_url": random_cafe.img_url,
        #     "location": random_cafe.location,
        #     "seats": random_cafe.seats,
        #     "has_toilet": random_cafe.has_toilet,
        #     "has_wifi": random_cafe.has_wifi,
        #     "has_sockets": random_cafe.has_sockets,
        #     "can_take_calls": random_cafe.can_take_calls,
        #     "coffee_price": random_cafe.coffee_price,
        # })

        # ANOTHER WAY
        # def to_dict(self):
        #     # Method 1.
        #     dictionary = {}
        #     # Loop through each column in the data record
        #     for column in self.__table__.columns:
        #         # Create a new dictionary entry;
        #         # where the key is the name of the column
        #         # and the value is the value of the column
        #         dictionary[column.name] = getattr(self, column.name)
        #     return dictionary

        # ANOTHER WAY
        # Method 2. Altenatively use Dictionary Comprehension to do the same thing.
        # return {column.name: getattr(self, column.name) for column in self.__table__.columns


@app.get('/all')
def get_all():
    with app.app_context():
        db.create_all()
        all_cafes = Cafe.query.all()
        cafes = []
        for cafe in all_cafes:
            del cafe.__dict__["_sa_instance_state"]
            cafes.append(cafe.__dict__)
        return jsonify(all_cafes=cafes)


@app.get('/search')
def search():
    with app.app_context():
        db.create_all()
        searched_location = request.args.get('loc')
        cafes = Cafe.query.filter_by(location=searched_location).all()
        print(cafes)
        if cafes:
            chosen_cafes = []
            for cafe in cafes:
                del cafe.__dict__["_sa_instance_state"]
                chosen_cafes.append(cafe.__dict__)
            return jsonify(cafes_in_the_area=chosen_cafes)
        else:
            return jsonify(
                error={
                    'Not Found': 'Sorry, we do not have a cafe at that location'
                }
            )


# HTTP POST - Create Record
def str_to_bool(arg_from_url):
    """Checks some common boolean representations and returns Bool"""
    if arg_from_url in ['True', ' true', 'T', 't', 'Yes', 'yes', 'y', '1']:
        return True
    else:
        return False


@app.post('/add')  # I'm adding new post through an app called Postman
def post_new_cafe():
    with app.app_context():
        db.create_all()
        new_cafe = Cafe(name=request.form.get("name"),
                        map_url=request.form.get("map_url"),
                        img_url=request.form.get("img_url"),
                        location=request.form.get("location"),
                        seats=request.form.get("seats"),
                        has_toilet=str_to_bool(request.form.get("has_toilet")),
                        has_wifi=str_to_bool(request.form.get("has_wifi")),
                        has_sockets=str_to_bool(request.form.get("has_sockets")),
                        can_take_calls=str_to_bool(request.form.get("can_take_calls")),
                        coffee_price=request.form.get("coffee_price")
                        )
        db.session.add(new_cafe)
        db.session.commit()
        return jsonify(response={"success": "Successfully added the new cafe."})


# HTTP PUT/PATCH - Update Record
@app.patch('/update-price/<cafe_id>')  # You can do methods = ['PATCH'] if you want. change to @app.route before doing
def update_price(cafe_id):
    with app.app_context():
        db.create_all()
        new_price = request.args.get('new_price')
        cafe_price_to_update = db.session.get(Cafe, cafe_id)
        if cafe_price_to_update:
            cafe_price_to_update.coffee_price = new_price
            db.session.commit()
            return jsonify(response={"success": "Successfully added the new cafe."}), 200  # Add response code
        else:
            return jsonify(response={"error": "Sorry, a cafe with that id was not found in the database"}), 404


# HTTP DELETE - Delete Record
@app.delete('/report-closed/<cafe_id>')
def delete_cafe(cafe_id):
    API_KEY = '876dju8ne90ijj2ioo)(32uhh4j4op45'
    user_api_key = request.args.get('api_key')
    if user_api_key == API_KEY:
        with app.app_context():
            db.create_all()
            cafe_to_delete = db.session.get(Cafe, cafe_id)
            if cafe_to_delete:
                db.session.delete(cafe_to_delete)
                db.session.commit()
                return jsonify(response={"success": "Successfully deleted the cafe."}), 200
            else:
                return jsonify(response={'NotFound': 'Sorry, a cafe with that id was not found in the database.'}), 404
    else:
        return jsonify(response={'error': 'Unauthorized access! Please make sure you have the correct api_key'}), 403


if __name__ == '__main__':
    app.run(debug=True)
