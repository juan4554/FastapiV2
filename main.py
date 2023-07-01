from fastapi import FastAPI, Body, Path, Query, Request, HTTPException, Depends
from fastapi.security import HTTPBearer

from fastapi.responses import HTMLResponse,JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel,Field
from typing import Optional

from Config.base_de_datos import sesion,motor,base
from modelos.ventas import Ventas as VentasModelo
from jwt_config import dame_token, valida_token

#Creamos una instacia de fastapi
app = FastAPI()
app.tittle = 'Aplicacion de ventas'
app.version = '1.0.1'
base.metadata.create_all(bind=motor)

#Clase/modelo usuario
class Usuario(BaseModel):
    email:str
    clave:str





#Creamos el modelo

class Ventas(BaseModel):
    #id: int = Field(ge=0,le=20)
    id: Optional[int]=None
    fecha: str
    tienda: str = Field(default="Tienda01",min_length=4,max_length=10)
    importe: float

# Portador token
class Portador(HTTPBearer):
    async def __call__(self, request: Request) :
        autorizacion = await super().__call__(request)
        dato = valida_token(autorizacion.credentials)
        if dato['email'] != 'josecodetech@gmail.com':
            raise HTTPException(status_code=403, detail='No autorizado')


#Creamos un punto de entrada o endpoint
@app.get('/', tags=['Inicio'])#Cambio de etiqueta en la documentacion
async def mensaje():
    return HTMLResponse('<h2>Titulo HTML desde FasTAPI</h2>')

#Creamos otra ruta para las ventas
@app.get('/ventas', tags=['Ventas'],response_model= list[Ventas],status_code=200,dependencies=[Depends(Portador())])
def dame_ventas()-> list[Ventas]:
    db = sesion()
    resultado = db.query(VentasModelo).all()
    return JSONResponse(status_code= 200,content=jsonable_encoder(resultado))

#Creamos otra ruta para las ventas pero ahora con parametro
@app.get('/ventas/{id}', tags=['Ventas'], response_model= Ventas)
def dame_ventas(id:int=Path(ge=1,le=1000))-> Ventas:
    db = sesion()
    resultado = db.query(VentasModelo).filter(VentasModelo.id == id).first()
    if not resultado:
        return JSONResponse(status_code=404,content={'mensaje':'No se encontro ese identificador'})
    
    
    return JSONResponse(status_code= 200, content=jsonable_encoder(resultado))
#Le cambia el parametro ahora te pedira un string tienda01,tienda02...Tipo Query
@app.get('/ventas/',tags=['Ventas'],response_model= list[Ventas])#Si ponemos una segunda barra despues de ventas 
                                    #evitamos que sobrescriba el anterior enlace llamado ventas
def dame_ventas_por_tienda(tienda:str=Query(min_length=4,max_length=20))-> list[Ventas]:
    #return tienda
    db = sesion()
    resultado = db.query(VentasModelo).filter(VentasModelo.tienda == tienda).all()
    if not resultado:
        return JSONResponse(status_code=404,content={'mensaje':'No se encontro esa tienda'})
    return JSONResponse(content= jsonable_encoder(resultado))
   

#Añadir registro de datos a la API
@app.post('/ventas',tags=['Ventas'], response_model= dict)
def crea_venta(venta:Ventas)-> dict:
    db = sesion()
    #extraemos atributos y los pasamos como parametros
    nueva_venta = VentasModelo(**venta.dict())
    #añdimos a la bd y hacemos commit para actualizardatos
    db.add(nueva_venta)
    db.commit()
   
    return JSONResponse(content={'mensaje':'Venta Registrada'})

#Modificar un registro buscando por id
@app.put('/ventas/{id}', tags=['Ventas'], response_model= dict)
def actualiza_ventas(id:int,venta:Ventas)-> dict:
    db = sesion()
    resultado = db.query(VentasModelo).filter(VentasModelo.id == id).first()
    if not resultado:
        return JSONResponse(status_code=404,content={'mensaje':'No se ha podido actualizar'})
    resultado.fecha = venta.fecha
    resultado.tienda = venta.tienda
    resultado.importe = venta.importe
    db.commit()

    #vamos a recorrer los elementos de la lista
    for elem in ventas:
        if elem['id'] == id:
            elem['fecha'] = venta.fecha
            elem['tienda'] = venta.tienda
            elem['importe'] = venta.importe
    return JSONResponse(content={'mensaje':'Venta Actualizada'})

# Eliminar un registro
@app.delete('/ventas/{id}', tags=['Ventas'], response_model= dict)
def borra_venta(id:int)->dict:
    db = sesion()
    resultado = db.query(VentasModelo).filter(VentasModelo.id == id).first()
    if not resultado:
        return JSONResponse(status_code=404,content={'mensaje':'No se ha podido borrar'})
    
    db.delete(resultado)
    db.commit()
    return JSONResponse(status_code=200,content={'mensaje':'Se ha borrado el registro'})


#####################################

#Creamos ruta para login modelo usuario
@app.post('/login',tags=['autenticacion'])
def login(usuario:Usuario):
    if usuario.email =='josecodetech@gmail.com' and usuario.clave=='1234':
        ###obtenemos el token con la función pasandole el diccionario deusuario
        token: str = dame_token(usuario.dict())
        return JSONResponse(status_code=200,content=token)
    else:
        return JSONResponse(content={'mensaje':'Acceso denegado'},status_code=404)