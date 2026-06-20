import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import random

# ══════════════════════════════════════════════════════════════════════
#  RUTAS DE IMÁGENES
# ══════════════════════════════════════════════════════════════════════
directorio_actual = os.path.dirname(os.path.abspath(__file__))
ruta_fondo = os.path.join(directorio_actual, "Imagenes", "Fondo.png")
ruta_mesa  = os.path.join(directorio_actual, "Imagenes", "Mesa.png")
ruta_tabla = os.path.join(directorio_actual, "Imagenes", "Tabla.png")

# ── Rutas de imágenes de estaciones ──
ruta_cocina    = os.path.join(directorio_actual, "Imagenes", "Cocina.png")
ruta_freidora  = os.path.join(directorio_actual, "Imagenes", "Freidora.png")
ruta_basurero  = os.path.join(directorio_actual, "Imagenes", "Basurero.png")

# ── Rutas de imágenes de cada despensa (mismo orden que INGREDIENTES_MAESTROS) ──
RUTAS_DESPENSA = {
    0: os.path.join(directorio_actual, "Imagenes", "Papa.png"),
    1: os.path.join(directorio_actual, "Imagenes", "Pan.png"),
    2: os.path.join(directorio_actual, "Imagenes", "Tomate.png"),
    3: os.path.join(directorio_actual, "Imagenes", "Lechuga.png"),
    4: os.path.join(directorio_actual, "Imagenes", "Pollo.png"),
    5: os.path.join(directorio_actual, "Imagenes", "Agua.png"),
    6: os.path.join(directorio_actual, "Imagenes", "Chuleta.png"),
    7: os.path.join(directorio_actual, "Imagenes", "Arroz.png"),
    8: os.path.join(directorio_actual, "Imagenes", "Pasta.png"),
    9: os.path.join(directorio_actual, "Imagenes", "Pescado.png"),
}

# ══════════════════════════════════════════════════════════════════════
#  ESTRUCTURA DE MEMORIA GLOBAL (HISTORIAL ACUMULATIVO)
# ══════════════════════════════════════════════════════════════════════
HISTORIAL_PUNTOS = {
    1: "-",  # McDonald's
    2: "-",  # La Soda
    3: "-"   # Hong Kong
}

HISTORIAL_ENTREGAS = {
    1: "-",
    2: "-",
    3: "-"
}

# ══════════════════════════════════════════════════════════════════════
#  CONFIGURACIÓN GLOBAL
# ══════════════════════════════════════════════════════════════════════
T      = 56          
COLS   = 14          
FILAS  = 11          
HUD_H  = 80          

ANCHO_CANVAS = COLS * T
ALTO_CANVAS  = FILAS * T + HUD_H

# ── Duración (en segundos) de cada acción que bloquea al chef ──
DURACION_ACCION = {
    "TABLA":    6,   # picar
    "COCINA":   5,   # cocinar
    "FREIDORA": 4,   # freír
    # DESPENSA, MESA, ENTREGA y BASURERO son inmediatas (no bloquean)
}

# Intervalo del loop rápido (para animar la barra de progreso), en milisegundos
INTERVALO_TICK_RAPIDO = 100

IMAGEN_CELDA = {
    "MESA":     None,
    "TABLA":    None,
    "COCINA":   None,
    "FREIDORA": None,
    "BASURERO": None,
    **{f"DESPENSA_{i}": None for i in range(10)}
}

COLOR_CELDA = {
    "SUELO":      "#DAAB76",   # Amarillo para el suelo plano
    "PARED":      "#3D2A0B",   # Rojo para las paredes
    "MESA":       "#8B6530",   
    "ENTREGA":    "#3A8FD9",   
    "BASURERO":   "#555555",   
    "COCINA":     "#D96A25",   
    "TABLA":      "#8B5E3C",   
    "FREIDORA":   "#D4B800",   
    "DESPENSA_0": "#795548",   # Papa
    "DESPENSA_1": "#FF9800",   # Pan
    "DESPENSA_2": "#F44336",   # Tomate
    "DESPENSA_3": "#4CAF50",   # Lechuga
    "DESPENSA_4": "#9C27B0",   # Pollo
    "DESPENSA_5": "#00BCD4",   # Agua
    "DESPENSA_6": "#E91E63",   # Chuleta
    "DESPENSA_7": "#9E9E9E",   # Arroz
    "DESPENSA_8": "#3F51B5",   # Pasta
    "DESPENSA_9": "#009688",   # Pescado
}

ETIQUETA_CELDA = {
    "MESA":       "MESA",
    "ENTREGA":    "ENT",
    "BASURERO":   "BAS",
    "COCINA":     "COCI",
    "TABLA":      "TBL",
    "FREIDORA":   "FRY",
    **{f"DESPENSA_{i}": f"D{i}" for i in range(10)}
}

INGREDIENTES_MAESTROS = {
    0: ("Papa", "crudo"),
    1: ("Pan", "listo"),
    2: ("Tomate", "crudo"),
    3: ("Lechuga", "crudo"),
    4: ("Pollo", "crudo"),
    5: ("Agua", "crudo"),
    6: ("Chuleta", "crudo"),
    7: ("Arroz", "crudo"),
    8: ("Pasta", "crudo"),
    9: ("Pescado", "crudo")
}

def _ingrediente_despensa(numero: int):
    if numero in INGREDIENTES_MAESTROS:
        nombre, estado = INGREDIENTES_MAESTROS[numero]
        if nombre == "Pan":
            return Pan(nombre)
        return Ingrediente(nombre, estado)
    return None

CONFIG_ESCENARIOS = {
    1: {
        "nombre_local": "MCDONALD'S",
        "recetas": ["Hamburguesa", "Papas Fritas", "Pollo Frito"],
        "mapa_raw": [
            "PPPPPPPPPPPPPP",
            "P  FFPPPPCCCPP",  
            "P0   MMMM   MP",  
            "P1          MP",  
            "P2           P",  
            "P3   MMMM    E",  
            "P4   MMMM    P",  
            "P           MP",  
            "B           BP",  
            "PMTTTM   MCCPP",  
            "PPPPPPPPPPPPPP",
        ]
    },
    2: {
        "nombre_local": "LA SODA",
        "recetas": ["Sopa", "Ensalada", "Casado"],
        "mapa_raw": [
            "PPPPPPPPPPPPPP",
            "PMM   FF   MMP",  
            "P0           P",  
            "P2  MM  MM   P",  
            "P3  MM  MM   P",  
            "P5  MC  CM   P",  
            "P6  MT  TM   P",  
            "P7  MM  MM   P",  
            "P            P",  
            "PB          BP",  
            "PPPPPPPEPPPPPP",
        ]
    },
    3: {
        "nombre_local": "HONG KONG",
        "recetas": ["Sushi", "Ensalada", "Sopa de Pescado", "Chopsuy"],
        "mapa_raw": [
            "PPB2357890PPPP",
            "P            P",  
            "P MMMMMMMM P P",  
            "P          P P",  
            "P MMCCMMMM P P",  
            "P          P P",  
            "P MMFFMMMM P P",  
            "P          P P",  
            "P MMTTMMMM P P",  
            "P          P P",  
            "PPPPPPPPPPBPEP",
        ]
    }
}

def _parsear_mapa(raw):
    simbolos = {
        " ": "SUELO", "P": "PARED", "M": "MESA", "E": "ENTREGA",
        "B": "BASURERO", "C": "COCINA", "T": "TABLA", "F": "FREIDORA"
    }
    for i in range(10):
        simbolos[str(i)] = f"DESPENSA_{i}"
    return [[simbolos.get(c, "SUELO") for c in fila] for fila in raw]

TIPOS_BLOQUEADOS = {"PARED", "MESA", "ENTREGA", "BASURERO", "COCINA", "TABLA", "FREIDORA"}
for i in range(10):
    TIPOS_BLOQUEADOS.add(f"DESPENSA_{i}")

# ══════════════════════════════════════════════════════════════════════
#  LÓGICA DEL JUEGO (CLASES)
# ══════════════════════════════════════════════════════════════════════

class Ingrediente:
    def __init__(self, nombre: str, estado: str = "crudo"):
        self.nombre = nombre
        self.estado = estado

    def cortar(self):
        if self.estado == "crudo" and self.nombre in ["Tomate", "Lechuga", "Papa"]:
            self.estado = "picado"

    def cocinar(self):
        if self.nombre in ["Agua", "Arroz", "Chuleta", "Pasta", "Pescado"] and self.estado == "crudo":
            self.estado = "cocinado"
        elif self.nombre == "Pollo" and self.estado == "crudo":
            self.estado = "frito"

    def freir(self):
        if self.nombre == "Papa" and self.estado == "picado":
            self.estado = "frito"


class Pan(Ingrediente):
    def __init__(self, nombre: str):
        super().__init__(nombre, "listo")


class Platillo:
    def __init__(self, nombre: str):
        self.nombre = nombre
        self.estado = "Listo para entrega"


class Receta:
    # Puntos base según cantidad de ingredientes requeridos (más ingredientes = más puntos)
    PUNTOS_POR_INGREDIENTE = 50

    # Tiempo máximo de entrega: base fija + tiempo extra por cada ingrediente
    TIEMPO_BASE_SEGUNDOS       = 5    # segundos mínimos garantizados
    TIEMPO_EXTRA_POR_INGREDIENTE = 5  # segundos adicionales por cada ingrediente

    def __init__(self, nombre: str, requisitos: dict):
        self._nombre = nombre
        self._requisitos = requisitos

        cantidad_ingredientes = len(requisitos)

        # ── Puntos base: a más ingredientes, más puntos ──
        self._puntos_base = cantidad_ingredientes * self.PUNTOS_POR_INGREDIENTE
        self._puntos_actuales = self._puntos_base

        # ── Tiempo máximo de entrega: a más ingredientes, más tiempo ──
        self._tiempo_max = (self.TIEMPO_BASE_SEGUNDOS +
                             cantidad_ingredientes * self.TIEMPO_EXTRA_POR_INGREDIENTE)
        self._tiempo_transcurrido = 0

    @property
    def nombre(self): return self._nombre
    @property
    def requisitos(self): return self._requisitos
    @property
    def puntos_base(self): return self._puntos_base
    @property
    def puntos_actuales(self): return self._puntos_actuales
    @property
    def tiempo_max(self): return self._tiempo_max

    def tiempo_restante(self) -> float:
        """Segundos que quedan antes de que la puntuación se reduzca a la mitad otra vez."""
        return max(0.0, self._tiempo_max - self._tiempo_transcurrido)

    def tiempo_restante_fmt(self) -> str:
        t = int(self.tiempo_restante())
        return f"{t//60:02d}:{t%60:02d}" if t >= 60 else f"{t}s"

    def tick(self, dt: float = 1):
        """
        Avanza el cronómetro de la receta.
        Cada vez que se cumple tiempo_max desde el último corte,
        la puntuación se reduce a la mitad (hasta llegar a 0).
        """
        self._tiempo_transcurrido += dt
        if self._tiempo_transcurrido >= self._tiempo_max:
            self._puntos_actuales = self._puntos_actuales // 2
            self._tiempo_transcurrido = 0   # reinicia el ciclo de penalización

    def esta_agotada(self) -> bool:
        """True si la puntuación llegó a cero (la receta debe eliminarse)."""
        return self._puntos_actuales <= 0

    def comparar_con_lista(self, lista_elementos) -> bool:
        if len(lista_elementos) == 1 and isinstance(lista_elementos[0], Platillo):
            return lista_elementos[0].nombre == self._nombre

        if len(lista_elementos) != len(self._requisitos):
            return False
        
        items_temp = list(lista_elementos)
        for req_nombre, req_estado in self._requisitos.items():
            encontrado = False
            for ing in items_temp:
                if not isinstance(ing, Platillo) and ing.nombre == req_nombre and ing.estado == req_estado:
                    items_temp.remove(ing)
                    encontrado = True
                    break
            if not encontrado:
                return False
        return True

    @staticmethod
    def crear(nombre: str):
        catalogo = {
            "Papas Fritas":     lambda: Receta("Papas Fritas",     {"Papa": "frito"}),
            "Hamburguesa":      lambda: Receta("Hamburguesa",      {"Pan": "listo", "Tomate": "picado", "Lechuga": "picado"}),
            "Pollo Frito":      lambda: Receta("Pollo Frito",      {"Pollo": "frito"}),
            "Sopa":             lambda: Receta("Sopa",             {"Tomate": "picado", "Papa": "picado", "Agua": "cocinado"}),
            "Ensalada":         lambda: Receta("Ensalada",         {"Tomate": "picado", "Lechuga": "picado"}),
            "Casado":           lambda: Receta("Casado",           {"Arroz": "cocinado", "Chuleta": "cocinado", "Tomate": "picado"}),
            "Sushi":            lambda: Receta("Sushi",            {"Arroz": "cocinado", "Pescado": "cocinado"}),
            "Sopa de Pescado":  lambda: Receta("Sopa de Pescado",  {"Papa": "picado", "Agua": "cocinado", "Pescado": "cocinado"}),
            "Chopsuy":          lambda: Receta("Chopsuy",          {"Pasta": "cocinado", "Tomate": "picado"}),
        }
        return catalogo.get(nombre, lambda: Receta("Ensalada", {"Tomate": "picado", "Lechuga": "picado"}))()


class Chef:
    def __init__(self, nombre: str, fila: int, col: int, color: str):
        self.__nombre    = nombre
        self.__fila      = fila
        self.__col       = col
        self.__color     = color
        self.__activo    = False
        self.__mano      = None      
        self.__direccion = "abajo"

        # ── Bloqueo por acción en curso (cocinar, picar, freír) ──
        self.__ocupado          = False   # True mientras está haciendo una acción
        self.__tiempo_accion    = 0.0     # cuánto dura la acción total (segundos)
        self.__tiempo_restante  = 0.0     # cuánto le queda (segundos)
        self.__accion_celda     = None    # (fila, col) de la estación donde está trabajando
        self.__accion_tipo      = None    # "TABLA" | "COCINA" | "FREIDORA"

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

    @property
    def ocupado(self):         return self.__ocupado
    @property
    def tiempo_accion(self):   return self.__tiempo_accion
    @property
    def tiempo_restante(self): return self.__tiempo_restante
    @property
    def accion_celda(self):    return self.__accion_celda
    @property
    def accion_tipo(self):     return self.__accion_tipo

    def progreso_accion(self) -> float:
        """Retorna 0.0 a 1.0 — qué tan avanzada está la acción (para la barra)."""
        if self.__tiempo_accion <= 0:
            return 1.0
        avance = (self.__tiempo_accion - self.__tiempo_restante) / self.__tiempo_accion
        return max(0.0, min(1.0, avance))

    def iniciar_accion(self, duracion: float, celda: tuple, tipo_estacion: str):
        """Bloquea al chef durante 'duracion' segundos en la celda indicada."""
        self.__ocupado         = True
        self.__tiempo_accion   = duracion
        self.__tiempo_restante = duracion
        self.__accion_celda    = celda
        self.__accion_tipo     = tipo_estacion

    def avanzar_accion(self, dt: float) -> bool:
        """
        Descuenta tiempo de la acción en curso.
        Retorna True si la acción TERMINÓ en este tick (para ejecutar su efecto).
        """
        if not self.__ocupado:
            return False
        self.__tiempo_restante -= dt
        if self.__tiempo_restante <= 1e-6:   # tolerancia por error de punto flotante
            self.__tiempo_restante = 0
            self.__ocupado = False
            return True
        return False

    def cancelar_accion(self):
        """Libera al chef sin completar la acción (por si se necesita en el futuro)."""
        self.__ocupado         = False
        self.__tiempo_accion   = 0.0
        self.__tiempo_restante = 0.0
        self.__accion_celda    = None
        self.__accion_tipo     = None

    def activar(self):    self.__activo = True
    def desactivar(self): self.__activo = False

    def tomar(self, item) -> bool:
        if self.__mano is None:
            self.__mano = item
            return True
        return False

    def soltar(self):
        item = self.__mano
        self.__mano = None
        return item

    def mover(self, dir: str, mapa: list) -> bool:
        if self.__ocupado:
            return False   # no se puede mover mientras está cocinando/picando/friendo
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
    # ─── CONFIGURACIÓN DE TIEMPO ───
    TIEMPO_TOTAL    = 120 
    INTERVALO_NUEVA = 25  

    def __init__(self, id_escenario=1):
        self.id_escenario = id_escenario
        cfg = CONFIG_ESCENARIOS[id_escenario]
        
        self.__nombre_local = cfg["nombre_local"]
        self.__recetas_pool = cfg["recetas"]
        self.__mapa         = _parsear_mapa(cfg["mapa_raw"])
        
        self.__chefs              = []
        self.__ordenes            = []    
        self.__tiempo             = self.TIEMPO_TOTAL
        self.__t_receta           = 0
        self.__puntos             = 0      
        self.__pedidos_entregados = 0      
        self.__activa             = False
        self.__mesas_items        = {}

    @property
    def nombre_local(self): return self.__nombre_local
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
    def pedidos_entregados(self): return self.__pedidos_entregados
    @property
    def activa(self):  return self.__activa
    @property
    def mesas_items(self): return self.__mesas_items

    def tipo(self, f, c): return self.__mapa[f][c]

    def agregar_chef(self, chef):
        if len(self.__chefs) < 2:
            self.__chefs.append(chef)

    def generar_receta(self):
        nombre = random.choice(self.__recetas_pool)
        r = Receta.crear(nombre)
        self.__ordenes.append(r)       
        return r

    def procesar_entrega(self, lista_elementos) -> tuple:
        if not self.__ordenes:
            return False, "No hay órdenes pendientes."
        
        for i, receta in enumerate(self.__ordenes):
            if receta.comparar_con_lista(lista_elementos):
                self.__ordenes.pop(i)
                puntos_ganados = receta.puntos_actuales
                self.__puntos += puntos_ganados
                self.__pedidos_entregados += 1
                
                if len(self.__ordenes) == 0:
                    self.generar_receta()
                
                return True, f"¡Éxito! Entregado [{receta.nombre}] +{puntos_ganados} pts"
        
        return False, "Los ingredientes no corresponden a ninguna orden activa."

    def iniciar(self):
        self.__activa = True
        self.generar_receta()  

    def tick(self):
        if not self.__activa:
            return
        self.__tiempo  -= 1
        self.__t_receta += 1

        if self.__t_receta >= self.INTERVALO_NUEVA:
            self.generar_receta()
            self.__t_receta = 0

        # ── Avanzar el cronómetro de cada receta y aplicar penalizaciones ──
        for receta in list(self.__ordenes):
            receta.tick(1)
            if receta.esta_agotada():
                # La receta caducó por completo: se elimina y se descuenta
                # del puntaje el valor ORIGINAL de la receta (puntos_base).
                self.__puntos = max(0, self.__puntos - receta.puntos_base)
                self.__ordenes.remove(receta)

        if self.__tiempo <= 0:
            self.__tiempo = 0
            self.__activa = False
            HISTORIAL_PUNTOS[self.id_escenario] = self.__puntos
            HISTORIAL_ENTREGAS[self.id_escenario] = self.__pedidos_entregados

    def tiempo_fmt(self):
        m, s = self.__tiempo // 60, self.__tiempo % 60
        return f"{m:02d}:{s:02d}"


# ══════════════════════════════════════════════════════════════════════
#  INTERFAZ GRÁFICA DEL JUEGO
# ══════════════════════════════════════════════════════════════════════

class VistaJuego:
    COLOR_HUD  = "#181818"

    def __init__(self, padre: tk.Misc, id_escenario=1):
        self.__padre = padre
        self.__id_escenario = id_escenario
        self.__win = tk.Toplevel(padre)
        self.__win.title(f"Crazy Snack Rush TEC - Nivel {id_escenario}")
        self.__win.resizable(False, False)
        self.__win.grab_set()

        self.__cocina = Cocina(id_escenario)

        # Cargar imágenes de Mesa y Tabla si existen
        if os.path.exists(ruta_mesa):
            _pil_mesa = Image.open(ruta_mesa).resize((T, T), Image.Resampling.LANCZOS)
            IMAGEN_CELDA["MESA"] = ImageTk.PhotoImage(_pil_mesa)
            
        if os.path.exists(ruta_tabla):
            _pil_tabla = Image.open(ruta_tabla).resize((T, T), Image.Resampling.LANCZOS)
            IMAGEN_CELDA["TABLA"] = ImageTk.PhotoImage(_pil_tabla)

        # Cargar imágenes de Cocina, Freidora y Basurero si existen
        if os.path.exists(ruta_cocina):
            _pil_cocina = Image.open(ruta_cocina).resize((T, T), Image.Resampling.LANCZOS)
            IMAGEN_CELDA["COCINA"] = ImageTk.PhotoImage(_pil_cocina)

        if os.path.exists(ruta_freidora):
            _pil_freidora = Image.open(ruta_freidora).resize((T, T), Image.Resampling.LANCZOS)
            IMAGEN_CELDA["FREIDORA"] = ImageTk.PhotoImage(_pil_freidora)

        if os.path.exists(ruta_basurero):
            _pil_basurero = Image.open(ruta_basurero).resize((T, T), Image.Resampling.LANCZOS)
            IMAGEN_CELDA["BASURERO"] = ImageTk.PhotoImage(_pil_basurero)

        # Cargar imagen de cada despensa (0-9) si existe su archivo
        for _num, _ruta_desp in RUTAS_DESPENSA.items():
            if os.path.exists(_ruta_desp):
                _pil_desp = Image.open(_ruta_desp).resize((T, T), Image.Resampling.LANCZOS)
                IMAGEN_CELDA[f"DESPENSA_{_num}"] = ImageTk.PhotoImage(_pil_desp)

        self.__canvas = tk.Canvas(
            self.__win,
            width=ANCHO_CANVAS, height=ALTO_CANVAS,
            bg="#111111", highlightthickness=0
        )
        self.__canvas.pack()

        suelos = [(f, c) for f in range(FILAS) for c in range(COLS) if self.__cocina.mapa[f][c] == "SUELO"]
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
        self._loop_rapido()

    def _activo(self) -> Chef:
        return self.__cocina.chefs[self.__idx_activo]

    def _msg(self, texto: str):
        self.__msg       = texto
        self.__msg_ticks = 3

    def _mover(self, dir: str):
        if not self.__cocina.activa: return
        self._activo().mover(dir, self.__cocina.mapa)
        self._dibujar()

    def _cambiar_chef(self, event=None):
        if not self.__cocina.activa: return "break"
        self._activo().desactivar()
        self.__idx_activo = 1 - self.__idx_activo
        self._activo().activar()
        self._msg(f"Controlas: {self._activo().nombre}")
        self._dibujar()
        return "break"   

    def _interactuar(self):
        if not self.__cocina.activa: return
        chef = self._activo()
        if chef.ocupado:
            return   # no puede iniciar otra acción mientras está ocupado
        ff, fc = chef.celda_frente()
        if not (0 <= ff < FILAS and 0 <= fc < COLS):
            return
        tipo = self.__cocina.tipo(ff, fc)
        self._msg(self._accion(chef, ff, fc, tipo))
        self._dibujar()

    def _verificar_ensamblado_automatico(self, lista_mesa):
        for nombre_platillo in ["Hamburguesa", "Sopa", "Ensalada", "Casado", "Sushi", "Sopa de Pescado", "Chopsuy"]:
            receta = Receta.crear(nombre_platillo)
            if receta.comparar_con_lista(lista_mesa):
                lista_mesa.clear()
                lista_mesa.append(Platillo(nombre_platillo))
                return True, nombre_platillo
        return False, ""

    def _accion(self, chef: Chef, f: int, c: int, tipo: str) -> str:
        if tipo.startswith("DESPENSA_"):
            if chef.mano:
                return f"{chef.nombre} ya lleva {chef.mano.nombre}."
            num = int(tipo.split("_")[1])
            ing = _ingrediente_despensa(num)
            if ing is None:
                return f"Despensa {num} vacía."
            chef.tomar(ing)
            return f"{chef.nombre} tomó {ing.nombre} ({ing.estado})."

        if tipo == "MESA":
            pos = (f, c)
            if pos not in self.__cocina.mesas_items:
                self.__cocina.mesas_items[pos] = []

            lista_mesa = self.__cocina.mesas_items[pos]

            if chef.mano:
                if isinstance(chef.mano, Platillo):
                    item_mano = chef.soltar()
                    lista_mesa.append(item_mano)
                    return f"Dejaste {item_mano.nombre} en la mesa."

                if chef.mano.nombre in ["Tomate", "Lechuga", "Papa"] and chef.mano.estado == "crudo":
                    return f"¡No puedes dejar {chef.mano.nombre} sin picar!"
                
                ing_mano = chef.soltar()
                lista_mesa.append(ing_mano)
                
                exito, nombre_p = self._verificar_ensamblado_automatico(lista_mesa)
                if exito:
                    return f"¡Combinación Perfecta! Armaste: {nombre_p} 🎉"

                nombres = "+".join(f"{i.nombre}({i.estado})" for i in lista_mesa)
                return f"En mesa: {nombres}"
            else:
                if lista_mesa:
                    item_tomado = lista_mesa.pop()
                    chef.tomar(item_tomado)
                    return f"Recogiste {item_tomado.nombre}."
                return "Mesa vacía."

        if tipo == "TABLA":
            if chef.mano is None: return "No llevas nada."
            if isinstance(chef.mano, Platillo): return "¡Ya es un platillo!"
            if chef.mano.nombre in ["Tomate", "Lechuga", "Papa"]:
                if chef.mano.estado == "crudo":
                    chef.iniciar_accion(DURACION_ACCION["TABLA"], (f, c), "TABLA")
                    return f"{chef.nombre} está picando {chef.mano.nombre}..."
                return f"{chef.mano.nombre} ya está picado."
            return f"{chef.mano.nombre} no se pica."

        if tipo == "COCINA":
            if chef.mano is None: return "No llevas nada."
            if isinstance(chef.mano, Platillo): return "¡Ya está terminado!"
            if chef.mano.nombre in ["Agua", "Arroz", "Chuleta", "Pollo", "Pasta", "Pescado"]:
                if chef.mano.estado == "crudo":
                    chef.iniciar_accion(DURACION_ACCION["COCINA"], (f, c), "COCINA")
                    return f"{chef.nombre} está cocinando {chef.mano.nombre}..."
                return f"{chef.mano.nombre} ya se cocinó."
            return "Eso no se cocina aquí."

        if tipo == "FREIDORA":
            if chef.mano is None: return "No llevas nada."
            if chef.mano.nombre == "Papa":
                if chef.mano.estado == "picado":
                    chef.iniciar_accion(DURACION_ACCION["FREIDORA"], (f, c), "FREIDORA")
                    return f"{chef.nombre} está friendo papas..."
                return "¡Picalas antes de freír!"
            return "Solo se fríen papas aquí."

        if tipo == "ENTREGA":
            ingredientes_a_entregar = []
            fuente = ""
            if chef.mano:
                ingredientes_a_entregar = [chef.mano]
                fuente = "mano"
            else:
                frente_f, frente_c = chef.celda_frente()
                mesas_adyacentes = [(frente_f, frente_c), (chef.fila, chef.col)]
                for pos_mesa in mesas_adyacentes:
                    if pos_mesa in self.__cocina.mesas_items and self.__cocina.mesas_items[pos_mesa]:
                        ingredientes_a_entregar = self.__cocina.mesas_items[pos_mesa]
                        fuente = pos_mesa
                        break

            if not ingredientes_a_entregar: return "No tienes comida para entregar."
            exito, mensaje = self.__cocina.procesar_entrega(ingredientes_a_entregar)
            if exito:
                if fuente == "mano": chef.soltar() 
                else: self.__cocina.mesas_items[fuente] = [] 
            return mensaje

        if tipo == "BASURERO":
            if chef.mano:
                nombre = chef.mano.nombre
                chef.soltar()
                return f"Tiraste {nombre}."
            return "No llevas nada."

        return f"'{tipo}' sin acción."

    def _loop(self):
        self.__cocina.tick()
        if self.__msg_ticks > 0: self.__msg_ticks -= 1
        self._dibujar()
        if self.__cocina.activa:
            self.__win.after(1000, self._loop)
        else:
            self._pantalla_fin()

    def _loop_rapido(self):
        """
        Corre cada INTERVALO_TICK_RAPIDO ms (más rápido que el tick de 1 seg).
        Avanza el progreso de cualquier chef ocupado y aplica el efecto
        de la estación apenas el tiempo llegue a cero.
        """
        if self.__cocina.activa:
            dt = INTERVALO_TICK_RAPIDO / 1000.0   # a segundos
            for chef in self.__cocina.chefs:
                if chef.ocupado:
                    termino = chef.avanzar_accion(dt)
                    if termino:
                        msg = self._completar_accion(chef)
                        self._msg(msg)
            self._dibujar()
            self.__win.after(INTERVALO_TICK_RAPIDO, self._loop_rapido)

    def _completar_accion(self, chef: Chef) -> str:
        """Se ejecuta justo cuando termina el tiempo de picar/cocinar/freír."""
        tipo = chef.accion_tipo

        if tipo == "TABLA":
            chef.mano.cortar()
            return f"{chef.mano.nombre} picado ✓"

        if tipo == "COCINA":
            nombre_previo = chef.mano.nombre
            chef.mano.cocinar()
            if nombre_previo == "Pollo":
                chef.soltar()
                chef.tomar(Platillo("Pollo Frito"))
            return f"{nombre_previo} cocinado con éxito ✓"

        if tipo == "FREIDORA":
            chef.mano.freir()
            chef.soltar()
            chef.tomar(Platillo("Papas Fritas"))
            return "Papas fritas listas ✓"

        return ""

    def _dibujar(self):
        self.__canvas.delete("all")
        self._d_hud()
        self._d_celdas()
        self._d_grid()      
        self._d_barras_progreso()
        self._d_chefs()
        self._d_mensaje()

    def _d_hud(self):
        cv = self.__canvas
        cv.create_rectangle(0, 0, ANCHO_CANVAS, HUD_H, fill=self.COLOR_HUD, outline="")

        cv.create_text(ANCHO_CANVAS//2, 16, text=self.__cocina.nombre_local, font=("Arial", 11, "bold"), fill="#FFD600")
        cv.create_text(ANCHO_CANVAS//2, 38, text=f"⏱  {self.__cocina.tiempo_fmt()}", font=("Arial", 20, "bold"), fill="white")
        
        cv.create_text(ANCHO_CANVAS - 10, 26, text=f"★ {self.__cocina.puntos}", font=("Arial", 14, "bold"), fill="white", anchor="e")

        ch = self._activo()
        cv.create_text(10, 26, text=f"▶ {ch.nombre}", font=("Arial", 13, "bold"), fill=ch.color, anchor="w")
        if ch.ocupado:
            cv.create_text(10, 50, text=f"⏳ Ocupado ({ch.accion_tipo})... ¡cambia con Tab!",
                           font=("Arial", 9, "bold"), fill="#FF7043", anchor="w")
        elif ch.mano:
            txt_estado = ch.mano.estado if isinstance(ch.mano, Platillo) else f"[{ch.mano.estado}]"
            cv.create_text(10, 50, text=f"Mano: {ch.mano.nombre} {txt_estado}", font=("Arial", 10), fill="#FFD600", anchor="w")

        ords = self.__cocina.ordenes
        if ords:
            partes = []
            for r in ords:
                partes.append(f"{r.nombre} [{r.puntos_actuales}pts·{r.tiempo_restante_fmt()}]")
            txt = "PEDIDOS: " + "  |  ".join(partes)
        else:
            txt = "Sin órdenes activas"
        cv.create_text(ANCHO_CANVAS//2, 64, text=txt, font=("Arial", 9, "bold"), fill="#FFC880")
        cv.create_line(0, HUD_H, ANCHO_CANVAS, HUD_H, fill="#333333", width=2)

    def _d_celdas(self):
        for f in range(FILAS):
            for c in range(COLS):
                tipo = self.__cocina.mapa[f][c]
                x0, y0 = c * T, f * T + HUD_H
                
                # Renderizado condicional: si hay imagen cargada para este tipo, se usa esa imagen
                img_celda = IMAGEN_CELDA.get(tipo)
                if img_celda is not None:
                    self.__canvas.create_image(x0, y0, image=img_celda, anchor="nw")
                else:
                    color = COLOR_CELDA.get(tipo, "#444444")
                    self.__canvas.create_rectangle(x0, y0, x0+T, y0+T, fill=color, outline=color)
                
                if tipo == "MESA" and (f, c) in self.__cocina.mesas_items and self.__cocina.mesas_items[(f, c)]:
                    items = self.__cocina.mesas_items[(f, c)]
                    etq = "+".join(i.nombre[0:3] for i in items)
                else:
                    etq = ETIQUETA_CELDA.get(tipo)

                # Evita pintar texto plano sobre celdas que ya tienen imagen, o sobre el suelo uniforme
                if etq and tipo != "SUELO" and IMAGEN_CELDA.get(tipo) is None:
                    self.__canvas.create_text(x0 + T//2, y0 + T//2, text=etq, font=("Arial", 8, "bold"), fill="#000000")
                elif tipo == "MESA" and (f, c) in self.__cocina.mesas_items and self.__cocina.mesas_items[(f, c)]:
                    # Si la mesa tiene comida encima, se dibuja la etiqueta flotante sobre el PNG
                    self.__canvas.create_text(x0 + T//2, y0 + T//2, text=etq, font=("Arial", 8, "bold"), fill="#FFFFFF")

    def _d_grid(self):
        pass

    def _d_barras_progreso(self):
        """
        Dibuja, sobre la celda de la estación, una barra de progreso
        estilo Overcooked mientras un chef está picando/cocinando/friendo.
        La barra se llena de izquierda a derecha conforme avanza el tiempo.
        """
        for chef in self.__cocina.chefs:
            if not chef.ocupado or chef.accion_celda is None:
                continue

            f_celda, c_celda = chef.accion_celda
            x0 = c_celda * T
            y0 = f_celda * T + HUD_H

            margen = 6
            alto_barra = 8
            bx0 = x0 + margen
            bx1 = x0 + T - margen
            by0 = y0 + T - alto_barra - 5
            by1 = y0 + T - 5

            progreso = chef.progreso_accion()   # 0.0 a 1.0
            ancho_relleno = (bx1 - bx0) * progreso

            # Fondo de la barra (vacío)
            self.__canvas.create_rectangle(
                bx0, by0, bx1, by1,
                fill="#2B2B2B", outline="#000000", width=1
            )
            # Relleno de la barra (progreso actual) — color del chef que la está usando
            if ancho_relleno > 0:
                self.__canvas.create_rectangle(
                    bx0, by0, bx0 + ancho_relleno, by1,
                    fill=chef.color, outline=""
                )

    def _d_chefs(self):
        R = T // 2 - 4
        for i, chef in enumerate(self.__cocina.chefs):
            x0, y0 = chef.col * T + 4, chef.fila * T + HUD_H + 4
            x1, y1 = x0 + T - 8, y0 + T - 8
            borde  = "#FFD600" if chef.activo else "#000000"
            grosor = 3         if chef.activo else 1
            
            self.__canvas.create_rectangle(x0, y0, x1, y1, fill=chef.color, outline=borde, width=grosor)
            cx = chef.col  * T + T // 2
            cy = chef.fila * T + T // 2 + HUD_H
            self.__canvas.create_text(cx, cy, text=str(i + 1), font=("Arial", 14, "bold"), fill="white")

            d = {
                "arriba":    [cx, cy-R-6, cx-5, cy-R, cx+5, cy-R],
                "abajo":     [cx, cy+R+6, cx-5, cy+R, cx+5, cy+R],
                "izquierda": [cx-R-6, cy, cx-R, cy-5, cx-R, cy+5],
                "derecha":   [cx+R+6, cy, cx+R, cy-5, cx+R, cy+5],
            }.get(chef.direccion)
            if d: self.__canvas.create_polygon(d, fill=chef.color, outline="")

            if chef.mano:
                self.__canvas.create_oval(cx+R-7, cy-R-3, cx+R+7, cy-R+11, fill="#FF9800", outline="white", width=1)
                self.__canvas.create_text(cx+R, cy-R+4, text=chef.mano.nombre[0], font=("Arial", 7, "bold"), fill="white")

    def _d_mensaje(self):
        if self.__msg_ticks > 0 and self.__msg:
            mx, my = ANCHO_CANVAS // 2, HUD_H + 28
            w = min(len(self.__msg) * 7 + 40, ANCHO_CANVAS - 20)
            self.__canvas.create_rectangle(mx-w//2, my-13, mx+w//2, my+13, fill="#1A1A1A", outline="#FFD600", width=1)
            self.__canvas.create_text(mx, my, text=self.__msg, font=("Arial", 11, "bold"), fill="#FFD600")

    def _pantalla_fin(self):
        self.__canvas.unbind("<KeyPress-Up>")
        self.__canvas.unbind("<KeyPress-Down>")
        self.__canvas.unbind("<KeyPress-Left>")
        self.__canvas.unbind("<KeyPress-Right>")
        self.__canvas.unbind("<Tab>")

        fin_win = tk.Toplevel(self.__win)
        fin_win.title("Marcador Global de Locales")
        fin_win.geometry("400x380")
        fin_win.resizable(False, False)
        fin_win.configure(bg="#1A1A1A")
        fin_win.transient(self.__win)
        fin_win.grab_set()

        tk.Label(fin_win, text="¡FIN DEL TURNO!", font=("Arial", 16, "bold"), fg="#FFD600", bg="#1A1A1A").pack(pady=10)
        
        f_mc = tk.LabelFrame(fin_win, text=" McDonald's ", font=("Arial", 10, "bold"), fg="white", bg="#262626", bd=1, relief="groove")
        f_mc.pack(fill="x", padx=20, pady=5)
        tk.Label(f_mc, text=f"Puntos: {HISTORIAL_PUNTOS[1]}   |   Entregas: {HISTORIAL_ENTREGAS[1]}", font=("Arial", 11), fg="#FFEB3B", bg="#262626").pack(pady=4)

        f_soda = tk.LabelFrame(fin_win, text=" La Soda ", font=("Arial", 10, "bold"), fg="white", bg="#262626", bd=1, relief="groove")
        f_soda.pack(fill="x", padx=20, pady=5)
        tk.Label(f_soda, text=f"Puntos: {HISTORIAL_PUNTOS[2]}   |   Entregas: {HISTORIAL_ENTREGAS[2]}", font=("Arial", 11), fg="#4CAF50", bg="#262626").pack(pady=4)

        f_hk = tk.LabelFrame(fin_win, text=" Hong Kong ", font=("Arial", 10, "bold"), fg="white", bg="#262626", bd=1, relief="groove")
        f_hk.pack(fill="x", padx=20, pady=5)
        tk.Label(f_hk, text=f"Puntos: {HISTORIAL_PUNTOS[3]}   |   Entregas: {HISTORIAL_ENTREGAS[3]}", font=("Arial", 11), fg="#00BCD4", bg="#262626").pack(pady=4)

        def avanzar():
            fin_win.destroy()
            self.__win.destroy()
            
            if self.__id_escenario == 1:
                VistaJuego(self.__padre, id_escenario=2)
            elif self.__id_escenario == 2:
                VistaJuego(self.__padre, id_escenario=3)
            elif self.__id_escenario == 3:
                total_pts = int(HISTORIAL_PUNTOS[1]) + int(HISTORIAL_PUNTOS[2]) + int(HISTORIAL_PUNTOS[3])
                total_ent = int(HISTORIAL_ENTREGAS[1]) + int(HISTORIAL_ENTREGAS[2]) + int(HISTORIAL_ENTREGAS[3])
                
                res_win = tk.Toplevel(self.__padre)
                res_win.title("🏆 Victoria Absoluta 🏆")
                res_win.geometry("320x220")
                res_win.configure(bg="#2E0854")
                res_win.grab_set()
                
                tk.Label(res_win, text="SUMA TOTAL DE JUEGO", font=("Arial", 14, "bold"), fg="#FFD600", bg="#2E0854").pack(pady=15)
                tk.Label(res_win, text=f"Puntos Totales: {total_pts} pts", font=("Arial", 12, "bold"), fg="white", bg="#2E0854").pack(pady=5)
                tk.Label(res_win, text=f"Entregas Totales: {total_ent}", font=("Arial", 12, "bold"), fg="#80FFF0", bg="#2E0854").pack(pady=5)
                
                tk.Button(res_win, text="FINALIZAR", font=("Arial", 10, "bold"), bg="#FFD600", command=res_win.destroy).pack(pady=20)

        btn_siguiente = tk.Button(
            fin_win, text="SIGUIENTE", font=("Arial", 11, "bold"),
            fg="black", bg="#FFD600", activebackground="#CCA600",
            bd=0, relief="flat", padx=25, pady=8, command=avanzar
        )
        btn_siguiente.pack(pady=20)


def abrir_about(padre: tk.Tk):
    v = tk.Toplevel(padre)
    v.title("About - Crazy Snack Rush TEC")
    v.geometry("370x480")
    v.resizable(False, False)
    v.configure(bg="#FFF8EA")
    v.transient(padre)
    v.grab_set()

    tk.Label(v, text="Crazy Snack Rush TEC", font=("Arial", 20, "bold"), fg="#5F3A22", bg="#FFF8EA").pack(pady=18)
    texto = (
        "¡Bienvenido a la versión didáctica!\n\n"
        "Gestiona la cocina, prepara platillos\n"
        "y entrega las órdenes antes de que\n"
        "se acabe el tiempo.\n\n"
        "─── Controles ───\n"
        "↑ ↓ ← →    Mover chef activo\n"
        "Tab           Cambiar de chef\n"
        "Q              Interactuar con estación\n\n"
        " Locales Disponibles:\n"
        "1. McDonald's  |  2. La Soda  |  3. Hong Kong"
    )
    tk.Label(v, text=texto, font=("Arial", 11), fg="#7D5A44", bg="#FFF8EA", justify="center").pack(pady=8)
    tk.Button(v, text="CERRAR", command=v.destroy, font=("Arial", 12, "bold"), fg="white", bg="#D96A43", bd=0, relief="flat", padx=20, pady=8).pack(side="bottom", pady=28)


# ══════════════════════════════════════════════════════════════════════
#  VENTANA PRINCIPAL / MENÚ DE INICIO (CON FONDO ORIGINAL)
# ══════════════════════════════════════════════════════════════════════
ANCHO_INI = 400
ALTO_INI  = 650

ventana = tk.Tk()
ventana.title("Crazy Snack Rush TEC")
ventana.geometry(f"{ANCHO_INI}x{ALTO_INI}")
ventana.resizable(False, False)

canvas_ini = tk.Canvas(ventana, width=ANCHO_INI, height=ALTO_INI, highlightthickness=0)
canvas_ini.pack(fill="both", expand=True)

if os.path.exists(ruta_fondo):
    _pil = Image.open(ruta_fondo).resize((ANCHO_INI, ALTO_INI), Image.Resampling.LANCZOS)
    _img_fondo = ImageTk.PhotoImage(_pil)
    canvas_ini.create_image(0, 0, image=_img_fondo, anchor="nw")
else:
    canvas_ini.configure(bg="#2B1B11")
    canvas_ini.create_text(ANCHO_INI//2, 180, text="Crazy Snack Rush TEC", font=("Arial", 26, "bold"), fill="white")
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
        _sid = canvas_ini.create_text(_x+_dx, _y+_dy, text=_b["texto"], font=_fnt, fill="black")
        _sombras.append(_sid)
    _tid = canvas_ini.create_text(_x, _y, text=_b["texto"], font=_fnt, fill="white")
    for _xid in _sombras + [_tid]:
        canvas_ini.tag_bind(_xid, "<Button-1>", lambda e, c=_b["cmd"]: c())
    canvas_ini.tag_bind(_tid, "<Enter>", lambda e, t=_tid: _set_color(t, "#b0b0b0"))
    canvas_ini.tag_bind(_tid, "<Leave>", lambda e, t=_tid: _set_color(t, "white"))
    _y += 70

ventana.mainloop()