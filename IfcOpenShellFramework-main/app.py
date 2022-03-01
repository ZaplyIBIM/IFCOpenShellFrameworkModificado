

from app import create_app


""" Creamos la API con Flask """
app = create_app();
app.run(port = 6969, debug=True);


