from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import os


app = FastAPI()
# directorio donde se almacena los archivos .mp3
MEDIA_DIR = './music'

#objecto que almacena los nombres de canciones
DATABASE_MUSIC ={
    "house":'house.mp3',
    'sunset':'sunset.mp3',
    'camisama':'camisama.mp3'
}

#comenzamos con la ejecucion de la api
@app.get('/audio/{audio_id}')
async def get_audio(audio_id:str):
    #busca el archivo asociado al ID
    filename = DATABASE_MUSIC.get(audio_id)
    
    if not filename:
       raise HTTPException(status_code = 404,detail ='cancion ID no encontrado')
    
    file_path = os.path.join(MEDIA_DIR,filename)

    #verificamos si la ruta es correcta y se encontro el archivo
    if not os.path.isfile(file_path):
        raise HTTPException(status_code = 404,detail ='cancion ID no encontrado')
    
    return FileResponse(file_path,media_type='audio/mp3',filename=filename)