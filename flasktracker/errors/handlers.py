from flask import Blueprint, render_template

errors = Blueprint('errors', __name__)


@errors.app_errorhandler(Exception)
def error_all(error):
    errno = getattr(error, "code", 500)
    msg = "Internal server error." if errno == 500 else "Not Found."
    errno_display = 404 if errno != 500 else 500
    return render_template("error.html", errno=errno_display, msg=msg), errno
