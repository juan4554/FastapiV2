import os
from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

fichero = "../datos.sqlite"

#leemos el directorio actual del alchivo de bd
directorio = os.path.dirname(os.path.realpath(__file__))

#direccion de la bd uniendo las dos variables anteriores
ruta = "sqlite:/// {os.path.join(directorio,fichero)}"

#creamos el motor
motor = create_engine(ruta,echo=True)

#creamos una sesion pasandole el motor
sesion = sessionmaker(bind=motor)

# crear base para manejar las tablas
base= declarative_base()

