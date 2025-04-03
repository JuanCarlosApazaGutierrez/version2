from PIL import Image
import os

# Función para expandir la imagen hacia arriba y abajo hasta que sea cuadrada
def expandir_a_cuadrada_con_fondo(imagen):
    ancho, alto = imagen.size
    if ancho > alto:
        # Calcular el relleno necesario
        diferencia = ancho - alto
        espacio_arriba = diferencia // 2
        espacio_abajo = diferencia - espacio_arriba

        # Crear una nueva imagen con fondo blanco y tamaño cuadrado
        tamaño_final = ancho  # El tamaño final será el ancho original (más grande que el alto)
        imagen_con_fondo = Image.new("RGBA", (tamaño_final, tamaño_final), (255, 255, 255, 255))  # Fondo blanco

        # Pegar la imagen original en el centro de la nueva imagen
        imagen_con_fondo.paste(imagen, (0, espacio_arriba), imagen)
        
        return imagen_con_fondo
    else:
        # Si la imagen ya es cuadrada o la altura es mayor, no hacer nada
        return imagen

# Función para guardar la imagen en varios tamaños en formato WebP
def guardar_imagen_webp(imagen, ruta_salida, tamaños):
    for tamaño in tamaños:
        imagen_redimensionada = imagen.resize((tamaño, tamaño))
        nombre_archivo = f"{ruta_salida}_{tamaño}px.webp"
        imagen_redimensionada.save(nombre_archivo, "WEBP")
        print(f"Imagen guardada en {nombre_archivo}")

# Ruta de la imagen PNG original
ruta_imagen = "logo2.png"
# Cargar la imagen
imagen = Image.open(ruta_imagen)

# Expandir la imagen hacia arriba y abajo para hacerla cuadrada con fondo blanco
imagen_cuadrada_con_fondo = expandir_a_cuadrada_con_fondo(imagen)
imagen_cuadrada_con_fondo.save("logo_sd.png", "PNG")
# Definir los tamaños en los que quieres guardar la imagen (en píxeles)
tamaños = [162, 108, 216, 324, 432]  # Puedes ajustar esta lista según tus necesidades

# Ruta de salida base
ruta_salida = "imagen_recortada"

# Guardar la imagen en los diferentes tamaños en formato WebP
#guardar_imagen_webp(imagen_cuadrada_con_fondo, ruta_salida, tamaños)

