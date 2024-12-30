from flask import Blueprint, render_template

errors = Blueprint('errors', __name__)


@errors.app_errorhandler(Exception)
def error_all(error):
    errno = getattr(error, "code", 500)
    if errno != 500:
        errno = 404
    msg = "Internal server error." if errno == 500 else "Not Found."
    return render_template("error.html", errno=errno, msg=msg), errno
