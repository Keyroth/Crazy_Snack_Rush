import os
import tkinter as tk
from PIL import Image, ImageTk

directorio_actual = os.path.dirname(os.path.abspath(__file__))
ruta_imagen = os.path.join(directorio_actual, "Imagenes", "Fondo.png")

def accion_iniciar(event=None):
    pass

def accion_about(event=None):
    ventana_about = tk.Toplevel(ventana)
    ventana_about.title("About - Crazy Rush TEC")
    ventana_about.geometry("350x450")
    ventana_about.resizable(False, False)
    ventana_about.configure(bg="#FFF8EA") 
    
    ventana_about.transient(ventana)
    ventana_about.grab_set()

    titulo_about = tk.Label(
        ventana_about, 
        text="Crazy Rush TEC", 
        font=("Arial", 20, "bold"), 
        fg="#5F3A22", 
        bg="#FFF8EA"
    )
    titulo_about.pack(pady=20)

    texto_explicacion = (
        "¡Bienvenido a la versión didáctica!\n\n"
        "Crazy Rush TEC es un juego de agilidad "
        "y estrategia donde tendrás que gestionar "
        "la preparación de diferentes platillos "
        "en un tiempo determinado mientras haces" 
        "recetas bajo presion \n\n"
        "¡Organiza tus tareas, evita que la cocina "
        "colapse y demuestra tus habilidades "
        "de cocina en cada nivel!"
    )

    contenido_about = tk.Label(
        ventana_about, 
        text=texto_explicacion, 
        font=("Arial", 11), 
        fg="#7D5A44", 
        bg="#FFF8EA", 
        justify="center", 
        wraplength=300
    )
    contenido_about.pack(pady=10)

    boton_salir = tk.Button(
        ventana_about, 
        text="SALIR", 
        command=ventana_about.destroy, 
        font=("Arial", 12, "bold"), 
        fg="white", 
        bg="#D96A43", 
        activebackground="#B85332", 
        activeforeground="white", 
        bd=0, 
        relief="flat", 
        padx=20, 
        pady=8
    )
    boton_salir.pack(side="bottom", pady=30)

ventana = tk.Tk()
ventana.title("Crazy Rush TEC")

ANCHO_DESEADO = 400
ALTO_DESEADO = 650   

ventana.geometry(f"{ANCHO_DESEADO}x{ALTO_DESEADO}")
ventana.resizable(False, False)

canvas = tk.Canvas(ventana, width=ANCHO_DESEADO, height=ALTO_DESEADO, highlightthickness=0)
canvas.pack(fill="both", expand=True)

pil_image = Image.open(ruta_imagen)
pil_image_resised = pil_image.resize((ANCHO_DESEADO, ALTO_DESEADO), Image.Resampling.LANCZOS)
imagen_fondo_final = ImageTk.PhotoImage(pil_image_resised)

canvas.create_image(0, 0, image=imagen_fondo_final, anchor="nw")

datos_botones = [
    {"texto": "INICIAR", "comando": accion_iniciar},
    {"texto": "ABOUT", "comando": accion_about}
]

posicion_y = 280 

def cambiar_color_borde(tags_sombras, id_centro, color_centro):
    canvas.itemconfig(id_centro, fill=color_centro)

for boton_info in datos_botones:
    x = ANCHO_DESEADO // 2
    y = posicion_y
    texto = boton_info["texto"]
    fuente = ("Arial", 24, "bold")
    
    sombra_ids = []
    for dx, dy in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
        s_id = canvas.create_text(x + dx, y + dy, text=texto, font=fuente, fill="black")
        sombra_ids.append(s_id)
        
    id_texto = canvas.create_text(x, y, text=texto, font=fuente, fill="white")
    
    todos_los_ids = sombra_ids + [id_texto]
    
    for x_id in todos_los_ids:
        canvas.tag_bind(x_id, "<Button-1>", boton_info["comando"])
    
    canvas.tag_bind(id_texto, "<Enter>", lambda e, s_ids=sombra_ids, t_id=id_texto: cambiar_color_borde(s_ids, t_id, "#a0a0a0"))
    canvas.tag_bind(id_texto, "<Leave>", lambda e, s_ids=sombra_ids, t_id=id_texto: cambiar_color_borde(s_ids, t_id, "white"))
    
    posicion_y += 60

ventana.mainloop()