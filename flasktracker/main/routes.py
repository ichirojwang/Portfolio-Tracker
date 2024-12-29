from flask import Blueprint, render_template

main = Blueprint('main', __name__)


@main.route('/welcome')
def welcome():
    return render_template("welcome.html")
