"""
juego.py  —  Crazy Snack Rush TEC
Todo en un solo archivo. Vista top-down 2D (estilo Bomberman).

SÍMBOLOS DEL MAPA:
  S = Suelo     (zona caminable)
  P = Pared     (bloqueada)
  M = Mesa      (superficie, no caminable)
  E = Entrega   (única por escenario)
  B = Basurero  (tira lo que llevas)
  C = Cocina    (fríe carnes/proteínas)
  T = Tabla     (pica vegetales)
  F = Freidora  (solo papas fritas)
  1..9 = Despensas individuales (cada número dispensa un ingrediente distinto)
"""

import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import random

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

IMAGEN_CELDA = {
    "SUELO":       None,   
    "PARED":       None,
    "MESA":        None,
    "ENTREGA":     None,
    "BASURERO":    None,
    "COCINA":      None,
    "TABLA":       None,
    "FREIDORA":    None,
    **{f"DESPENSA_{i}": None for i in range(10)}
}

COLOR_CELDA = {
    "SUELO":      "#D6CCB4",   
    "PARED":      "#3E2B1A",   
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
            "P0 1 2 3 4MM M",  
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
    },
    2: {
        "nombre_local": "LA SODA",
        "recetas": ["Sopa", "Ensalada", "Casado"],
        "mapa_raw": [
            "PPPPPPPPPPPPPP",
            "P2 0 5 3 6 7MM",  
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
    },
    3: {
        "nombre_local": "HONG KONG",
        "recetas": ["Sushi", "Ensalada", "Sopa de Pescado", "Chopsuy"],
        "mapa_raw": [
            "PPPPPPPPPPPPPP",
            "P2 7 9 8 0 5MM",  
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
    def __init__(self, nombre: str, requisitos: dict):
        self._nombre = nombre
        self._requisitos = requisitos 

    @property
    def nombre(self): return self._nombre

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
            "Sopa de Pescado":  lambda: Receta("Sopa de Pescado",  {"Tomate": "picado", "Papa": "picado", "Agua": "cocinado", "Pescado": "cocinado"}),
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
    # NUEVO TIEMPO ACTUALIZADO: 2 Minutos (120 segundos)
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
                self.__puntos += 100
                self.__pedidos_entregados += 1
                
                if len(self.__ordenes) == 0:
                    self.generar_receta()
                
                return True, f"¡Éxito! Entregado [{receta.nombre}] +100 pts"
        
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
    COLOR_GRID = "#111111"
    COLOR_HUD  = "#181818"

    def __init__(self, padre: tk.Misc, id_escenario=1):
        self.__padre = padre
        self.__id_escenario = id_escenario
        self.__win = tk.Toplevel(padre)
        self.__win.title(f"Crazy Snack Rush TEC - Nivel {id_escenario}")
        self.__win.resizable(False, False)
        self.__win.grab_set()

        self.__cocina = Cocina(id_escenario)

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
                    chef.mano.cortar()
                    return f"{chef.mano.nombre} picado ✓"
                return f"{chef.mano.nombre} ya está picado."
            return f"{chef.mano.nombre} no se pica."

        if tipo == "COCINA":
            if chef.mano is None: return "No llevas nada."
            if isinstance(chef.mano, Platillo): return "¡Ya está terminado!"
            if chef.mano.nombre in ["Agua", "Arroz", "Chuleta", "Pollo", "Pasta", "Pescado"]:
                if chef.mano.estado == "crudo":
                    chef.mano.cocinar()
                    if chef.mano.nombre == "Pollo":
                        chef.soltar()
                        chef.tomar(Platillo("Pollo Frito"))
                    return f"{chef.mano.nombre} cocinado con éxito ✓"
                return f"{chef.mano.nombre} ya se cocinó."
            return "Eso no se cocina aquí."

        if tipo == "FREIDORA":
            if chef.mano is None: return "No llevas nada."
            if chef.mano.nombre == "Papa":
                if chef.mano.estado == "picado":
                    chef.mano.freir()
                    chef.soltar()
                    chef.tomar(Platillo("Papas Fritas"))
                    return "Papas fritas listas ✓"
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

    def _dibujar(self):
        self.__canvas.delete("all")
        self._d_hud()
        self._d_celdas()
        self._d_grid()      
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
        if ch.mano:
            txt_estado = ch.mano.estado if isinstance(ch.mano, Platillo) else f"[{ch.mano.estado}]"
            cv.create_text(10, 50, text=f"Mano: {ch.mano.nombre} {txt_estado}", font=("Arial", 10), fill="#FFD600", anchor="w")

        ords = self.__cocina.ordenes
        if ords:
            txt = "PEDIDOS PENDIENTES: " + "  |  ".join(r.nombre for r in ords)
        else:
            txt = "Sin órdenes activas"
        cv.create_text(ANCHO_CANVAS//2, 64, text=txt, font=("Arial", 10, "bold"), fill="#FFC880")
        cv.create_line(0, HUD_H, ANCHO_CANVAS, HUD_H, fill="#333333", width=2)

    def _d_celdas(self):
        for f in range(FILAS):
            for c in range(COLS):
                tipo = self.__cocina.mapa[f][c]
                x0, y0 = c * T, f * T + HUD_H
                color = COLOR_CELDA.get(tipo, "#444444")
                self.__canvas.create_rectangle(x0, y0, x0+T, y0+T, fill=color, outline="")
                
                if tipo == "MESA" and (f, c) in self.__cocina.mesas_items and self.__cocina.mesas_items[(f, c)]:
                    items = self.__cocina.mesas_items[(f, c)]
                    etq = "+".join(i.nombre[0:3] for i in items)
                else:
                    etq = ETIQUETA_CELDA.get(tipo)

                if etq:
                    self.__canvas.create_text(x0 + T//2, y0 + T//2, text=etq, font=("Arial", 8, "bold"), fill="#000000")

    def _d_grid(self):
        for c in range(COLS + 1):
            self.__canvas.create_line(c * T, HUD_H, c * T, ALTO_CANVAS, fill=self.COLOR_GRID, width=1)
        for f in range(FILAS + 1):
            self.__canvas.create_line(0, f * T + HUD_H, ANCHO_CANVAS, f * T + HUD_H, fill=self.COLOR_GRID, width=1)

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
        "🍟 Locales Disponibles:\n"
        "1. McDonald's  |  2. La Soda  |  3. Hong Kong"
    )
    tk.Label(v, text=texto, font=("Arial", 11), fg="#7D5A44", bg="#FFF8EA", justify="center").pack(pady=8)
    tk.Button(v, text="CERRAR", command=v.destroy, font=("Arial", 12, "bold"), fg="white", bg="#D96A43", bd=0, relief="flat", padx=20, pady=8).pack(side="bottom", pady=28)


# ══════════════════════════════════════════════════════════════════════
#  VENTANA PRINCIPAL / MENÚ DE INICIO ORIGINAL (¡CON TU FONDO!)
# ══════════════════════════════════════════════════════════════════════
directorio_actual = os.path.dirname(os.path.abspath(__file__))
ruta_fondo = os.path.join(directorio_actual, "Imagenes", "Fondo.png")

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