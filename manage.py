# Set the path
# import os, sys
# from flask_script import Manager, Server
# from insidelogs import app
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#
#
# manager = Manager(app)
#
# # Turn on debugger by default and reloader
# manager.add_command("runserver", Server(
#     use_debugger=True,
#     use_reloader=True,
#     host='127.0.0.1')
#                     )
#
# if __name__ == "__main__":
#     manager.run()

from insidelogs import app
app.run(debug=True)