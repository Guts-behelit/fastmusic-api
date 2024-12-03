from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.responses import StreamingResponse
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.background import BackgroundTasks
import os
from yt_dlp import YoutubeDL
import io
import tempfile
import uvicorn
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Usa el puerto definido por Render o 8000 por defecto
    uvicorn.run("main:app", host="0.0.0.0", port=port)

app = FastAPI()
# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite cualquier origen. Cambia esto por seguridad en producción.
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos los headers
)  

# directorio donde se almacena los archivos .mp3
MEDIA_DIR = './music'

#objecto que almacena los nombres de canciones
DATABASE_MUSIC ={
    "house":'house.mp3',
    'sunset':'sunset.mp3',
    'camisama':'camisama.mp3'
}
if not os.path.exists(MEDIA_DIR):
    os.makedirs(MEDIA_DIR)

# Función para descargar solo el audio de YouTube y guardarlo en la carpeta
def download_audio_youtube(idMudic):
    urlYoutube = f'https://youtube.com/watch?v={idMudic}'
    
    # Definir el nombre del archivo de salida con formato .mp3
    output_path = os.path.join(MEDIA_DIR, f'{idMudic}.mp3')
    
    # Configuración de yt-dlp
    ydl_opts = {
        'format': 'bestaudio/best',  # Descargar el mejor formato de audio
        'outtmpl': output_path,      # Guardar el archivo en la ruta especificada
        'postprocessors': [],        # No hacer conversiones post-descarga
        'quiet': True,               # Evitar demasiada salida en consola
        'progress_hooks': [],        # No es necesario seguimiento de progreso
    }

    # Descargar el audio
    with YoutubeDL(ydl_opts) as ydl:
        print(f"Descargando audio de {urlYoutube}...")
        ydl.download([urlYoutube])
        print("Descarga completada.")
    
    return output_path  # Devolver la ruta del archivo descargado

@app.get("/")
def read_root():
    return {"message": "Hello, Render!"}


@app.get('/audio/{audio_id}')
async def get_audio(audio_id: str):
    try:
        # Llamar a la función para descargar el audio y obtener la ruta del archivo
        file_path = download_audio_youtube(audio_id)

        # Verificar si el archivo existe antes de enviarlo
        if not os.path.isfile(file_path):
            raise HTTPException(status_code=404, detail="Archivo no encontrado")

        # Enviar el archivo como respuesta usando FileResponse
        return FileResponse(file_path, media_type='audio/webm', filename=os.path.basename(file_path))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/delete_all_files")
async def delete_all_files():
    try:
        # Verificar si el directorio existe
        if not os.path.exists(MEDIA_DIR):
            raise HTTPException(status_code=404, detail="Directorio no encontrado.")
        
        # Listar todos los archivos en la carpeta MEDIA_DIR
        files = os.listdir(MEDIA_DIR)

        # Eliminar todos los archivos
        for file_name in files:
            file_path = os.path.join(MEDIA_DIR, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Archivo {file_path} eliminado.")

        return JSONResponse(content={"message": "Todos los archivos han sido eliminados."}, status_code=200)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
