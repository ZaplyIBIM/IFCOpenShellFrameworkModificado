"""

Código que crea la aplicación Flask y la ejecuta en un puerto en modo Debug

"""

#Imports
from app import create_app

#Crea la app y la ejecuta
app = create_app();
app.run(port = 6969, debug=True);


