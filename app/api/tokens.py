#This is where the authentication sybsystem is going to be defined

#IMPORTS
from app import db
from app.api import bp
from app.api.auth import basic_auth

#IMPORTS - revoking tokens
from app.api.auth import token_auth

#get token function
@bp.route('/tokens', methods=['POST'])
@basic_auth.login_required
def get_token():
    token = basic_auth.current_user().get_token()
    db.session.commit()
    return {'token': token}

# revoke token function
@bp.route('/tokens', methods=['DELETE'])
@token_auth.login_required
def revoke_token():
    token_auth.current_user().revoke_token()
    db.session.commit()
    return '', 204