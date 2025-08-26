#Main Application Module

#Imports
from app import db, create_app
import sqlalchemy.orm as so
import sqlalchemy as sa
from app.models import User, Posts, Message, Notification, Task

app = create_app()

#create shell
@app.shell_context_processor
def make_shell_context():
     return {'sa': sa, 'so': so, 'db': db, 'User': User, 'Posts': Posts,
             'Message': Message, 'Notification': Notification, 'Task': Task} 