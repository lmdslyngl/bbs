
import flask

from model.board import Board
from model.userinfo import UserInfo
from model.boardinfo import BoardInfo
import views.user
import views.auth
import views.boardlist
import views.board
from views.util import get_logined_user
from views.auth_deco import login_required
from views.template_functions import register_template_functions


app = flask.Flask(__name__, static_url_path="/static")


if __name__ == "__main__":
    register_template_functions(app)

    app.register_blueprint(views.board.module)
    app.register_blueprint(views.user.module)
    app.register_blueprint(views.auth.module)
    app.register_blueprint(views.boardlist.module)
    app.run(debug=True)

