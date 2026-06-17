import os
import tkinter as tk
from PIL import Image, ImageTk
import random

T      = 56          
COLS   = 14          
FILAS  = 11          
HUD_H  = 80          

ANCHO_CANVAS = COLS * T
ALTO_CANVAS  = FILAS * T + HUD_H

IMAGEN_CELDA = {
    "SUELO":       None,   
    "PARED":       None,
    "MESA":        None,
    "ENTREGA":     None,
    "BASURERO":    None,
    "COCINA":      None,
    "TABLA":       None,
    "FREIDORA":    None,
    "DESPENSA_1":  None,   
    "DESPENSA_2":  None,
    "DESPENSA_3":  None,
    "DESPENSA_4":  None,
    "DESPENSA_5":  None,
    "DESPENSA_6":  None,
    "DESPENSA_7":  None,
    "DESPENSA_8":  None,
    "DESPENSA_9":  None,
}

IMAGEN_CHEF_1 = None   
IMAGEN_CHEF_2 = None   

COLOR_CELDA = {
    "SUELO":      "#D6CCB4",   
    "PARED":      "#3E2B1A",   
    "MESA":       "#8B6530",   
    "ENTREGA":    "#3A8FD9",   
    "BASURERO":   "#555555",   
    "COCINA":     "#D96A25",   
    "TABLA":      "#8B5E3C",   
    "FREIDORA":   "#D4B800",   
    "DESPENSA_1": "#4CAF50",   
    "DESPENSA_2": "#8BC34A",   
    "DESPENSA_3": "#F44336",   
    "DESPENSA_4": "#FF9800",   
    "DESPENSA_5": "#9C27B0",   
    "DESPENSA_6": "#00BCD4",   
    "DESPENSA_7": "#E91E63",   
    "DESPENSA_8": "#795548",   
    "DESPENSA_9": "#607D8B",   
}

ETIQUETA_CELDA = {
    "MESA":       "MESA",
    "ENTREGA":    "ENT",
    "BASURERO":   "BAS",
    "COCINA":     "COCI",
    "TABLA":      "TBL",
    "FREIDORA":   "FRY",
    "DESPENSA_1": "D1",
    "DESPENSA_2": "D2",
    "DESPENSA_3": "D3",
    "DESPENSA_4": "D4",
    "DESPENSA_5": "D5",
    "DESPENSA_6": "D6",
    "DESPENSA_7": "D7",
    "DESPENSA_8": "D8",
    "DESPENSA_9": "D9",
}

def _ingrediente_despensa(numero: int):
    tabla = {
        1: lambda: Vegetal("Lechuga"),
        2: lambda: Vegetal("Tomate"),
        3: lambda: Proteina("Carne"),
        4: lambda: Proteina("Pollo"),
        5: lambda: Pan("Pan"),
        6: lambda: Pan("Tortilla"),
        7: lambda: Papa(),
        8: lambda: Vegetal("Cebolla"),
        9: lambda: Vegetal("Pepino"),
    }
    fabrica = tabla.get(numero)
    return fabrica() if fabrica else None

MAPA_RAW = [
    "PPPPPPPPPPPPPP",
    "P1 2 3MMMMMM P",  
    "P            P",  
    "P            P",  
    "P            P",  
    "P            P",  
    "P            P",  
    "P            P",  
    "P            P",  
    "PCTFB       EP",  
    "PPPPPPPPPPPPPP",
]

_SIMBOLO_A_TIPO = {
    "S": "SUELO",
    " ": "SUELO",   
    "P": "PARED",
    "M": "MESA",
    "E": "ENTREGA",
    "B": "BASURERO",
    "C": "COCINA",
    "T": "TABLA",
    "F": "FREIDORA",
    "1": "DESPENSA_1",
    "2": "DESPENSA_2",
    "3": "DESPENSA_3",
    "4": "DESPENSA_4",
    "5": "DESPENSA_5",
    "6": "DESPENSA_6",
    "7": "DESPENSA_7",
    "8": "DESPENSA_8",
    "9": "DESPENSA_9",
}

def _parsear_mapa(raw):
    return [[_SIMBOLO_A_TIPO.get(c, "SUELO") for c in fila] for fila in raw]

MAPA_ESC1 = _parsear_mapa(MAPA_RAW)

TIPOS_BLOQUEADOS = {
    "PARED", "MESA", "ENTREGA", "BASURERO",
    "COCINA", "TABLA", "FREIDORA",
    "DESPENSA_1","DESPENSA_2","DESPENSA_3",
    "DESPENSA_4","DESPENSA_5","DESPENSA_6",
    "DESPENSA_7","DESPENSA_8","DESPENSA_9",
}

class Ingrediente:
    def __init__(self, nombre: str):
        self._nombre = nombre
        self._estado = "crudo"

    @property
    def nombre(self): return self._nombre
    @property
    def estado(self): return self._estado

    def set_estado(self, e: str): self._estado = e

    def _preparar_recursivo(self, pasos: int):
        if pasos <= 0:
            self._estado = "preparado"
            return
        self._preparar_recursivo(pasos - 1)

    def __repr__(self):
        return f"{self._nombre}[{self._estado}]"


class Vegetal(Ingrediente):
    def __init__(self, nombre: str):
        super().__init__(nombre)
        self.estacion_requerida = "TABLA"

    def cortar(self):
        self._preparar_recursivo(3)


class Pan(Ingrediente):
    def __init__(self, nombre: str):
        super().__init__(nombre)
        self.estacion_requerida = None
        self._estado = "preparado"


class Proteina(Ingrediente):
    def __init__(self, nombre: str):
        super().__init__(nombre)
        self.__cocinada = False
        self.estacion_requerida = "COCINA"

    @property
    def cocinada(self): return self.__cocinada

    def cocinar(self):
        self.__cocinada = True
        self._preparar_recursivo(4)

    def quemar(self):
        self._estado = "quemado"


class Papa(Ingrediente):
    def __init__(self):
        super().__init__("Papa")
        self.estacion_requerida = "FREIDORA"

    def freir(self):
        self._preparar_recursivo(2)


class Receta:
    TIEMPO_BASE = 60

    def __init__(self, nombre: str, ingredientes: list):
        self._nombre = nombre
        self._ingredientes = ingredientes
        self._puntos_base = len(ingredientes) * 100
        self._puntos = self._puntos_base
        self._tiempo_max = self.TIEMPO_BASE + len(ingredientes) * 15
        self._timer = 0

    @property
    def nombre(self):          return self._nombre
    @property
    def puntos_base(self):     return self._puntos_base
    @property
    def puntos_actuales(self): return self._puntos
    @property
    def ingredientes(self):    return self._ingredientes

    def tick(self, seg: int = 1):
        self._timer += seg
        if self._timer >= self._tiempo_max:
            self._puntos = max(0, self._puntos // 2)
            self._timer = 0

    def tiempo_restante(self) -> int:
        return max(0, self._tiempo_max - self._timer)

    def tiempo_fmt(self) -> str:
        t = self.tiempo_restante()
        return f"{t//60:02d}:{t%60:02d}"

    def comparar(self, otra) -> bool:
        a = sorted(i.nombre for i in self._ingredientes)
        b = sorted(i.nombre for i in otra.ingredientes)
        return a == b

    @staticmethod
    def crear(nombre: str):
        catalogo = {
            "Hamburguesa":  lambda: Receta("Hamburguesa",  [Proteina("Carne"), Pan("Pan"), Vegetal("Lechuga")]),
            "Ensalada":     lambda: Receta("Ensalada",     [Vegetal("Lechuga"), Vegetal("Tomate")]),
            "Papas Fritas": lambda: Receta("Papas Fritas", [Papa(), Papa()]),
            "Wrap":         lambda: Receta("Wrap",         [Pan("Tortilla"), Proteina("Pollo"), Vegetal("Lechuga")]),
        }
        return catalogo.get(nombre, catalogo["Ensalada"])()


class Chef:
    def __init__(self, nombre: str, fila: int, col: int, color: str):
        self.__nombre    = nombre
        self.__fila      = fila
        self.__col       = col
        self.__color     = color
        self.__activo    = False
        self.__mano      = None      
        self.__direccion = "abajo"

    @property
    def nombre(self):    return self.__nombre
    @property
    def fila(self):      return self.__fila
    @property
    def col(self):       return self.__col
    @property
    def color(self):     return self.__color
    @property
    def activo(self):    return self.__activo
    @property
    def mano(self):      return self.__mano
    @property
    def direccion(self): return self.__direccion

    def activar(self):    self.__activo = True
    def desactivar(self): self.__activo = False

    def tomar(self, ing) -> bool:
        if self.__mano is None:
            self.__mano = ing
            return True
        return False

    def soltar(self):
        ing = self.__mano
        self.__mano = None
        return ing

    def mover(self, dir: str, mapa: list) -> bool:
        self.__direccion = dir
        d = {"arriba":(-1,0),"abajo":(1,0),"izquierda":(0,-1),"derecha":(0,1)}
        df, dc = d[dir]
        nf, nc = self.__fila + df, self.__col + dc
        if 0 <= nf < len(mapa) and 0 <= nc < len(mapa[0]):
            if mapa[nf][nc] not in TIPOS_BLOQUEADOS:
                self.__fila, self.__col = nf, nc
                return True
        return False

    def celda_frente(self) -> tuple:
        d = {"arriba":(-1,0),"abajo":(1,0),"izquierda":(0,-1),"derecha":(0,1)}
        df, dc = d[self.__direccion]
        return self.__fila + df, self.__col + dc


class Cocina:
    RECETAS_ESC     = {1: ["Hamburguesa","Ensalada","Papas Fritas","Wrap"]}
    TIEMPO_TOTAL    = {1: 180}
    INTERVALO_NUEVA = {1: 25}

    def __init__(self, escenario: int = 1):
        self.__esc       = escenario
        self.__mapa      = MAPA_ESC1
        self.__chefs     = []
        self.__ordenes   = []    
        self.__historial = []    
        self.__tiempo    = self.TIEMPO_TOTAL[escenario]
        self.__t_receta  = 0
        self.__puntos    = 0
        self.__activa    = False

    @property
    def mapa(self):    return self.__mapa
    @property
    def chefs(self):   return self.__chefs
    @property
    def ordenes(self): return self.__ordenes
    @property
    def tiempo(self):  return self.__tiempo
    @property
    def puntos(self):  return self.__puntos
    @property
    def activa(self):  return self.__activa

    def tipo(self, f, c): return self.__mapa[f][c]

    def agregar_chef(self, chef):
        if len(self.__chefs) < 2:
            self.__chefs.append(chef)

    def generar_receta(self):
        nombre = random.choice(self.RECETAS_ESC[self.__esc])
        r = Receta.crear(nombre)
        self.__ordenes.append(r)       
        return r

    def entregar_orden(self):
        if self.__ordenes:
            r = self.__ordenes.pop(0)  
            self.__puntos += r.puntos_actuales
            self._push_historial(("entrega", r.nombre, r.puntos_actuales))
            return r
        return None

    def _push_historial(self, accion):
        self.__historial.append(accion)   

    def ver_ultimo_historial(self):
        return self.__historial[-1] if self.__historial else None

    def iniciar(self):
        self.__activa = True
        self.generar_receta()

    def tick(self):
        if not self.__activa:
            return
        self.__tiempo  -= 1
        self.__t_receta += 1

        if self.__t_receta >= self.INTERVALO_NUEVA[self.__esc]:
            self.generar_receta()
            self.__t_receta = 0

        for r in list(self.__ordenes):
            r.tick(1)
            if r.puntos_actuales <= 0:
                self.__puntos = max(0, self.__puntos - r.puntos_base)
                self.__ordenes.remove(r)

        if self.__tiempo <= 0:
            self.__tiempo = 0
            self.__activa = False

    def tiempo_fmt(self):
        m, s = self.__tiempo // 60, self.__tiempo % 60
        return f"{m:02d}:{s:02d}"


class VistaJuego:
    COLOR_GRID = "#111111"
    COLOR_HUD  = "#181818"

    def __init__(self, padre: tk.Misc, escenario: int = 1):
        self.__win = tk.Toplevel(padre)
        self.__win.title("Crazy Snack Rush TEC")
        self.__win.resizable(False, False)
        self.__win.grab_set()

        self.__cocina = Cocina(escenario)

        self.__canvas = tk.Canvas(
            self.__win,
            width=ANCHO_CANVAS, height=ALTO_CANVAS,
            bg="#111111", highlightthickness=0
        )
        self.__canvas.pack()

        self.__img_celda = {}
        for tipo, ruta in IMAGEN_CELDA.items():
            if ruta and os.path.exists(ruta):
                try:
                    img = Image.open(ruta).resize((T, T), Image.Resampling.LANCZOS)
                    self.__img_celda[tipo] = ImageTk.PhotoImage(img)
                except Exception:
                    self.__img_celda[tipo] = None
            else:
                self.__img_celda[tipo] = None

        self.__img_chef = [None, None]
        for i, ruta in enumerate([IMAGEN_CHEF_1, IMAGEN_CHEF_2]):
            if ruta and os.path.exists(ruta):
                try:
                    img = Image.open(ruta).resize((T, T), Image.Resampling.LANCZOS)
                    self.__img_chef[i] = ImageTk.PhotoImage(img)
                except Exception:
                    pass

        suelos = [(f, c)
                  for f in range(FILAS) for c in range(COLS)
                  if self.__cocina.mapa[f][c] == "SUELO"]
        s1 = suelos[0]  if suelos          else (5, 1)
        s2 = suelos[-1] if len(suelos) > 1 else (5, 2)

        self.__chef1 = Chef("Chef Rojo", s1[0], s1[1], "#E53935")
        self.__chef2 = Chef("Chef Azul", s2[0], s2[1], "#1565C0")
        self.__cocina.agregar_chef(self.__chef1)
        self.__cocina.agregar_chef(self.__chef2)
        self.__idx_activo = 0
        self.__chef1.activar()

        self.__msg       = ""
        self.__msg_ticks = 0

        self.__canvas.focus_set()
        self.__canvas.bind("<KeyPress-Up>",    lambda e: self._mover("arriba"))
        self.__canvas.bind("<KeyPress-Down>",  lambda e: self._mover("abajo"))
        self.__canvas.bind("<KeyPress-Left>",  lambda e: self._mover("izquierda"))
        self.__canvas.bind("<KeyPress-Right>", lambda e: self._mover("derecha"))
        self.__canvas.bind("<Tab>",            self._cambiar_chef)
        self.__canvas.bind("<KeyPress-q>",     lambda e: self._interactuar())
        self.__canvas.bind("<KeyPress-Q>",     lambda e: self._interactuar())

        self.__cocina.iniciar()
        self._loop()

    def _activo(self) -> Chef:
        return self.__cocina.chefs[self.__idx_activo]

    def _msg(self, texto: str):
        self.__msg       = texto
        self.__msg_ticks = 2

    def _mover(self, dir: str):
        self._activo().mover(dir, self.__cocina.mapa)
        self._dibujar()

    def _cambiar_chef(self, event=None):
        self._activo().desactivar()
        self.__idx_activo = 1 - self.__idx_activo
        self._activo().activar()
        self._msg(f"Controlas: {self._activo().nombre}")
        self._dibujar()
        return "break"   

    def _interactuar(self):
        chef = self._activo()
        ff, fc = chef.celda_frente()
        if not (0 <= ff < FILAS and 0 <= fc < COLS):
            return
        tipo = self.__cocina.tipo(ff, fc)
        self._msg(self._accion(chef, tipo))
        self._dibujar()

    def _accion(self, chef: Chef, tipo: str) -> str:

        if tipo.startswith("DESPENSA_"):
            if chef.mano:
                return f"{chef.nombre} ya lleva {chef.mano.nombre}. Suéltalo primero."
            num = int(tipo.split("_")[1])
            ing = _ingrediente_despensa(num)
            if ing is None:
                return f"Despensa {num} sin ingrediente asignado."
            chef.tomar(ing)
            return f"{chef.nombre} tomó {ing.nombre}."

        if tipo == "TABLA":
            if chef.mano is None:
                return "No llevas ningún ingrediente."
            if isinstance(chef.mano, Vegetal):
                chef.mano.cortar()
                return f"{chef.nombre} picó {chef.mano.nombre}. ✓ Listo."
            return f"{chef.mano.nombre} no se puede picar aquí."

        if tipo == "COCINA":
            if chef.mano is None:
                return "No llevas ningún ingrediente."
            if isinstance(chef.mano, Proteina):
                chef.mano.cocinar()
                return f"{chef.nombre} cocinó {chef.mano.nombre}. ✓ Listo."
            return f"{chef.mano.nombre} no va en la cocina (solo carnes)."

        if tipo == "FREIDORA":
            if chef.mano is None:
                return "No llevas ningún ingrediente."
            if isinstance(chef.mano, Papa):
                chef.mano.freir()
                return f"{chef.nombre} frió {chef.mano.nombre}. ✓ Listo."
            return f"{chef.mano.nombre} no va en la freidora (solo papas)."

        if tipo == "ENTREGA":
            r = self.__cocina.entregar_orden()
            if r:
                return f"¡Entregado! +{r.puntos_actuales} pts  [{r.nombre}]"
            return "No hay órdenes en cola."

        if tipo == "BASURERO":
            if chef.mano:
                nombre = chef.mano.nombre
                chef.soltar()
                return f"{chef.nombre} tiró {nombre} al basurero."
            return "No llevas nada."

        if tipo == "MESA":
            return f"{chef.nombre} interactuó con la mesa."

        return f"'{tipo}' sin acción."

    def _loop(self):
        self.__cocina.tick()
        if self.__msg_ticks > 0:
            self.__msg_ticks -= 1
        self._dibujar()
        if self.__cocina.activa:
            self.__win.after(1000, self._loop)
        else:
            self._pantalla_fin()

    def _dibujar(self):
        self.__canvas.delete("all")
        self._d_hud()
        self._d_celdas()
        self._d_grid()      
        self._d_chefs()
        self._d_mensaje()

    def _d_hud(self):
        cv = self.__canvas
        cv.create_rectangle(0, 0, ANCHO_CANVAS, HUD_H,
                             fill=self.COLOR_HUD, outline="")

        cv.create_text(ANCHO_CANVAS//2, 26,
                       text=f"⏱  {self.__cocina.tiempo_fmt()}",
                       font=("Arial", 22, "bold"), fill="#FFD600")

        cv.create_text(ANCHO_CANVAS - 10, 26,
                       text=f"★ {self.__cocina.puntos}",
                       font=("Arial", 14, "bold"), fill="white", anchor="e")

        ch = self._activo()
        cv.create_text(10, 26,
                       text=f"▶ {ch.nombre}",
                       font=("Arial", 13, "bold"), fill=ch.color, anchor="w")

        if ch.mano:
            cv.create_text(10, 50,
                           text=f"Mano: {ch.mano.nombre} [{ch.mano.estado}]",
                           font=("Arial", 10), fill="#FFD600", anchor="w")

        ords = self.__cocina.ordenes
        if ords:
            txt = "  |  ".join(f"{r.nombre} {r.tiempo_fmt()}" for r in ords[:4])
        else:
            txt = "Sin órdenes activas"
        cv.create_text(ANCHO_CANVAS//2, 62,
                       text=txt, font=("Arial", 9), fill="#FFC880")

        cv.create_line(0, HUD_H, ANCHO_CANVAS, HUD_H,
                       fill="#333333", width=2)

    def _d_celdas(self):
        for f in range(FILAS):
            for c in range(COLS):
                tipo = self.__cocina.mapa[f][c]
                x0, y0 = c * T, f * T + HUD_H

                img = self.__img_celda.get(tipo)
                if img:
                    self.__canvas.create_image(x0, y0, image=img, anchor="nw")
                else:
                    color = COLOR_CELDA.get(tipo, "#444444")
                    self.__canvas.create_rectangle(
                        x0, y0, x0+T, y0+T,
                        fill=color, outline=""
                    )
                    etq = ETIQUETA_CELDA.get(tipo)
                    if etq:
                        self.__canvas.create_text(
                            x0 + T//2, y0 + T//2,
                            text=etq, font=("Arial", 9, "bold"),
                            fill="#000000"
                        )

    def _d_grid(self):
        for c in range(COLS + 1):
            x = c * T
            self.__canvas.create_line(x, HUD_H, x, ALTO_CANVAS,
                                      fill=self.COLOR_GRID, width=1)
        for f in range(FILAS + 1):
            y = f * T + HUD_H
            self.__canvas.create_line(0, y, ANCHO_CANVAS, y,
                                      fill=self.COLOR_GRID, width=1)

    def _d_chefs(self):
        R = T // 2 - 4

        for i, chef in enumerate(self.__cocina.chefs):
            x0 = chef.col * T + 4
            y0 = chef.fila * T + HUD_H + 4
            x1 = x0 + T - 8
            y1 = y0 + T - 8

            img = self.__img_chef[i]
            if img:
                self.__canvas.create_image(
                    chef.col * T, chef.fila * T + HUD_H,
                    image=img, anchor="nw"
                )
            else:
                borde  = "#FFD600" if chef.activo else "#000000"
                grosor = 3         if chef.activo else 1
                
                self.__canvas.create_rectangle(
                    x0, y0, x1, y1,
                    fill=chef.color, outline=borde, width=grosor
                )
                
                cx = chef.col  * T + T // 2
                cy = chef.fila * T + T // 2 + HUD_H
                self.__canvas.create_text(
                    cx, cy,
                    text=str(i + 1),   
                    font=("Arial", 14, "bold"), fill="white"
                )

            cx = chef.col  * T + T // 2
            cy = chef.fila * T + T // 2 + HUD_H
            d = {
                "arriba":    [cx, cy-R-6, cx-5, cy-R, cx+5, cy-R],
                "abajo":     [cx, cy+R+6, cx-5, cy+R, cx+5, cy+R],
                "izquierda": [cx-R-6, cy, cx-R, cy-5, cx-R, cy+5],
                "derecha":   [cx+R+6, cy, cx+R, cy-5, cx+R, cy+5],
            }.get(chef.direccion)
            if d:
                self.__canvas.create_polygon(d, fill=chef.color, outline="")

            if chef.mano:
                self.__canvas.create_oval(
                    cx+R-7, cy-R-3, cx+R+7, cy-R+11,
                    fill="#FF9800", outline="white", width=1
                )
                self.__canvas.create_text(
                    cx+R, cy-R+4,
                    text=chef.mano.nombre[0],
                    font=("Arial", 7, "bold"), fill="white"
                )

    def _d_mensaje(self):
        if self.__msg_ticks > 0 and self.__msg:
            mx, my = ANCHO_CANVAS // 2, HUD_H + 28
            w = min(len(self.__msg) * 7 + 20, ANCHO_CANVAS - 20)
            self.__canvas.create_rectangle(
                mx-w//2, my-13, mx+w//2, my+13,
                fill="#1A1A1A", outline="#FFD600", width=1
            )
            self.__canvas.create_text(
                mx, my, text=self.__msg,
                font=("Arial", 11, "bold"), fill="#FFD600"
            )

    def _pantalla_fin(self):
        mx, my = ANCHO_CANVAS // 2, ALTO_CANVAS // 2
        self.__canvas.create_rectangle(
            mx-200, my-70, mx+200, my+70,
            fill="#1A1A1A", outline="#FFD600", width=3
        )
        self.__canvas.create_text(mx, my-30,
                                   text="¡TIEMPO AGOTADO!",
                                   font=("Arial", 26, "bold"), fill="#FFD600")
        self.__canvas.create_text(mx, my+15,
                                   text=f"Puntuación final: {self.__cocina.puntos} pts",
                                   font=("Arial", 17), fill="white")


def abrir_about(padre: tk.Tk):
    v = tk.Toplevel(padre)
    v.title("About - Crazy Snack Rush TEC")
    v.geometry("370x480")
    v.resizable(False, False)
    v.configure(bg="#FFF8EA")
    v.transient(padre)
    v.grab_set()

    tk.Label(v, text="Crazy Snack Rush TEC",
             font=("Arial", 20, "bold"), fg="#5F3A22", bg="#FFF8EA").pack(pady=18)

    texto = (
        "¡Bienvenido a la versión didáctica!\n\n"
        "Gestiona la cocina, prepara platillos\n"
        "y entrega las órdenes antes de que\n"
        "se acabe el tiempo.\n\n"
        "─── Controles ───\n"
        "↑ ↓ ← →    Mover chef activo\n"
        "Tab           Cambiar de chef\n"
        "Q              Interactuar con estación"
    )
    tk.Label(v, text=texto, font=("Arial", 11), fg="#7D5A44",
             bg="#FFF8EA", justify="center", wraplength=320).pack(pady=8)

    tk.Button(v, text="CERRAR", command=v.destroy,
              font=("Arial", 12, "bold"), fg="white", bg="#D96A43",
              activebackground="#B85332", activeforeground="white",
              bd=0, relief="flat", padx=20, pady=8).pack(side="bottom", pady=28)


directorio_actual = os.path.dirname(os.path.abspath(__file__))
ruta_fondo = os.path.join(directorio_actual, "Imagenes", "Fondo.png")

ANCHO_INI = 400
ALTO_INI  = 650

ventana = tk.Tk()
ventana.title("Crazy Snack Rush TEC")
ventana.geometry(f"{ANCHO_INI}x{ALTO_INI}")
ventana.resizable(False, False)

canvas_ini = tk.Canvas(ventana, width=ANCHO_INI, height=ALTO_INI,
                        highlightthickness=0)
canvas_ini.pack(fill="both", expand=True)

if os.path.exists(ruta_fondo):
    _pil = Image.open(ruta_fondo).resize((ANCHO_INI, ALTO_INI), Image.Resampling.LANCZOS)
    _img_fondo = ImageTk.PhotoImage(_pil)
    canvas_ini.create_image(0, 0, image=_img_fondo, anchor="nw")
else:
    canvas_ini.configure(bg="#2B1B11")
    canvas_ini.create_text(ANCHO_INI//2, 180,
                            text="Crazy Snack Rush TEC",
                            font=("Arial", 26, "bold"), fill="white")
    _img_fondo = None

def _set_color(item_id, color):
    canvas_ini.itemconfig(item_id, fill=color)

_botones = [
    {"texto": "INICIAR", "cmd": lambda: VistaJuego(ventana, 1)},
    {"texto": "ABOUT",   "cmd": lambda: abrir_about(ventana)},
]

_y = 310
for _b in _botones:
    _x   = ANCHO_INI // 2
    _fnt = ("Arial", 24, "bold")
    _sombras = []
    for _dx, _dy in [(-2,-2),(-2,2),(2,-2),(2,2)]:
        _sid = canvas_ini.create_text(_x+_dx, _y+_dy,
                                       text=_b["texto"], font=_fnt, fill="black")
        _sombras.append(_sid)
    _tid = canvas_ini.create_text(_x, _y, text=_b["texto"],
                                   font=_fnt, fill="white")
    for _xid in _sombras + [_tid]:
        canvas_ini.tag_bind(_xid, "<Button-1>",
                             lambda e, c=_b["cmd"]: c())
    canvas_ini.tag_bind(_tid, "<Enter>",
                         lambda e, t=_tid: _set_color(t, "#b0b0b0"))
    canvas_ini.tag_bind(_tid, "<Leave>",
                         lambda e, t=_tid: _set_color(t, "white"))
    _y += 70

ventana.mainloop()