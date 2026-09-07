from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

import json
import os
from datetime import datetime


# =====================================
# CONFIGURACIÓN
# =====================================

TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = 8979299763


ARCHIVO_USUARIOS = "usuarios.json"
ARCHIVO_PRODUCTOS = "productos.json"
ARCHIVO_KEYS = "keys.json"
ARCHIVO_SALDOS = "saldos.json"
ARCHIVO_COMPRAS = "compras.json"
ARCHIVO_RECARGAS = "recargas.json"



# =====================================
# MANEJO DE ARCHIVOS
# =====================================


def cargar(nombre):

    if not os.path.exists(nombre):
        return {}

    with open(nombre, "r", encoding="utf-8") as archivo:
        return json.load(archivo)



def guardar(nombre, datos):

    with open(nombre, "w", encoding="utf-8") as archivo:
        json.dump(
            datos,
            archivo,
            indent=4,
            ensure_ascii=False
        )



def fecha():

    return datetime.now().strftime("%d/%m/%Y")



# =====================================
# USUARIOS
# =====================================


def usuarios():

    return cargar(ARCHIVO_USUARIOS)



def guardar_usuarios(datos):

    guardar(
        ARCHIVO_USUARIOS,
        datos
    )



def crear_usuario(nombre, password):

    datos = usuarios()


    if nombre in datos:
        return False


    datos[nombre] = {

        "password": password,
        "fecha": fecha()

    }


    guardar_usuarios(datos)


    return True



def validar_usuario(nombre, password):

    datos = usuarios()


    if nombre not in datos:
        return False


    if datos[nombre]["password"] != password:
        return False


    return True



# =====================================
# SALDOS
# =====================================


def saldo_usuario(nombre):

    datos = cargar(
        ARCHIVO_SALDOS
    )

    return datos.get(nombre,0)



def agregar_saldo(nombre,monto):

    datos = cargar(
        ARCHIVO_SALDOS
    )


    if nombre not in datos:
        datos[nombre]=0


    datos[nombre]+=monto


    guardar(
        ARCHIVO_SALDOS,
        datos
    )



def quitar_saldo(nombre,monto):

    datos = cargar(
        ARCHIVO_SALDOS
    )


    if nombre not in datos:
        return False


    if datos[nombre] < monto:
        return False


    datos[nombre]-=monto


    guardar(
        ARCHIVO_SALDOS,
        datos
    )


    return True



# =====================================
# RECARGAS
# =====================================


def guardar_recarga(nombre,monto):

    datos = cargar(
        ARCHIVO_RECARGAS
    )


    if nombre not in datos:
        datos[nombre]=[]


    datos[nombre].append({

        "monto":monto,
        "fecha":fecha()

    })


    guardar(
        ARCHIVO_RECARGAS,
        datos
    )



# =====================================
# PRODUCTOS
# =====================================


def productos():

    return cargar(
        ARCHIVO_PRODUCTOS
    )



# =====================================
# KEYS
# =====================================


def keys():

    return cargar(
        ARCHIVO_KEYS
    )



def obtener_key(producto,plan):

    datos = keys()


    if producto not in datos:
        return None


    if plan not in datos[producto]:
        return None


    lista = datos[producto][plan]


    if len(lista)==0:
        return None


    key = lista.pop(0)


    guardar(
        ARCHIVO_KEYS,
        datos
    )


    return key



# =====================================
# COMPRAS
# =====================================


def compras():

    return cargar(
        ARCHIVO_COMPRAS
    )



def registrar_compra(nombre,producto,plan,precio,key):

    datos = compras()


    if nombre not in datos:
        datos[nombre]=[]


    datos[nombre].append({

        "producto":producto,
        "plan":plan,
        "precio":precio,
        "key":key,
        "fecha":fecha()

    })


    guardar(
        ARCHIVO_COMPRAS,
        datos
    )



def realizar_compra(nombre,producto,plan):

    lista_productos = productos()


    if producto not in lista_productos:
        return None



    precio = lista_productos[producto][plan]


    if saldo_usuario(nombre) < precio:
        return "SALDO"



    key = obtener_key(
        producto,
        plan
    )


    if key is None:
        return "KEY"



    quitar_saldo(
        nombre,
        precio
    )


    registrar_compra(
        nombre,
        producto,
        plan,
        precio,
        key
    )


    return {

        "producto":producto,
        "plan":plan,
        "precio":precio,
        "key":key

    }



# =====================================
# SESIONES TEMPORALES
# =====================================


SESIONES = {}



# =====================================
# CREAR ADMIN AUTOMÁTICO
# =====================================


def crear_admin():

    datos = usuarios()


    if "Gusber Mods" not in datos:

        datos["Gusber Mods"]={

            "password":"Gusber@18",
            "fecha":fecha()

        }


        guardar_usuarios(datos)



crear_admin()


# =====================================
# INICIO DEL BOT
# =====================================


async def inicio(update: Update, context: ContextTypes.DEFAULT_TYPE):

    telegram_id = str(update.message.from_user.id)


    botones = [

        [
            InlineKeyboardButton(
                "🔑 Iniciar sesión",
                callback_data="login"
            )
        ],

        [
            InlineKeyboardButton(
                "🛠 Soporte",
                callback_data="soporte"
            )
        ]

    ]


    await update.message.reply_text(
    "👑 BIENVENIDO A GUSBER MODS\n"
    "       Tu mejor opción ❤️\n\n"
    "Selecciona una opción:",
    reply_markup=InlineKeyboardMarkup(botones)
)


# =====================================
# PEDIR LOGIN
# =====================================


async def pedir_usuario(update, context):

    telegram_id = str(
        update.callback_query.from_user.id
    )

    SESIONES[telegram_id] = {
        "estado": "usuario"
    }

    botones = [
        [
            InlineKeyboardButton(
                "⬅️ Regresar",
                callback_data="inicio"
            )
        ]
    ]

    await update.callback_query.edit_message_text(
        "🔑 Ingresa tu nombre de usuario:",
        reply_markup=InlineKeyboardMarkup(botones)
    )


# ==========================================
# RECIBIR MENSAJES
# ==========================================

async def recibir_texto(update: Update, context: ContextTypes.DEFAULT_TYPE):

    telegram_id = str(update.message.from_user.id)
    texto = update.message.text

    print("MENSAJE RECIBIDO:", texto)
    print("SESION ACTUAL:",
 SESIONES.get(telegram_id))

    if telegram_id not in SESIONES:
        return

    estado = SESIONES[telegram_id].get("estado")


    # ==========================
    # CREAR USUARIO ADMIN
    # ==========================

    if estado == "crear_usuario":

        nuevo_usuario = texto

        SESIONES[telegram_id]["nuevo_usuario"] = nuevo_usuario
        SESIONES[telegram_id]["estado"] = "crear_password"

        await update.message.reply_text(
            "🔐 Ahora ingresa la contraseña del usuario:"
        )

        return


    # ==========================
    # CREAR PASSWORD USUARIO
    # ==========================

    if estado == "crear_password":

        password = texto

        usuario = SESIONES[telegram_id]["nuevo_usuario"]

        datos = usuarios()

        datos[usuario] = {
            "password": password,
            "fecha_registro": fecha(),
            "compras": 0,
            "recargas": 0
        }

        guardar_usuarios(datos)

        await update.message.reply_text(
    f"✅ Usuario registrado correctamente\n\n"
    f"👤 Usuario: {usuario}\n"
    f"🔑 Contraseña: {password}",
    reply_markup=InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "⬅️ Volver al administrador",
                callback_data="admin"
            )
        ]
    ])
)

        return

# ==========================
# AGREGAR PRODUCTO ADMIN
# ==========================

    if estado == "agregar_producto":

        producto = texto

        SESIONES[telegram_id]["producto_nuevo"] = producto
        SESIONES[telegram_id]["estado"] = "agregar_planes"


        await update.message.reply_text(

            "📦 PRODUCTO AGREGADO\n\n"
            f"Producto: {producto}\n\n"
            "✍️ Ahora escribe los planes separados por línea:\n\n"
            "Ejemplo:\n"
            "1 mes\n"
            "3 meses\n"
            "12 meses",

            reply_markup=InlineKeyboardMarkup([

                [

                    InlineKeyboardButton(
                        "⬅️ Volver a productos",
                        callback_data="admin_keys"
                    )

                ]

            ])

        )

        return

# =====================================
# AGREGAR PLANES PRODUCTO
# =====================================

    if estado == "agregar_planes":

        producto = SESIONES[telegram_id]["producto_nuevo"]


        planes = texto.split("\n")


        planes = [
            plan.strip()
            for plan in planes
            if plan.strip()
        ]


        SESIONES[telegram_id]["planes_nuevos"] = planes

        SESIONES[telegram_id]["estado"] = "agregar_precios"


        await update.message.reply_text(

            f"💵 AGREGAR PRECIOS\n\n"
            f"📦 Producto: {producto}\n\n"
            "Ahora escribe los precios separados por línea:\n\n"
            "Ejemplo:\n"
            "5\n"
            "6\n"
            "7",

            reply_markup=InlineKeyboardMarkup([

                [

                    InlineKeyboardButton(
                        "⬅️ Volver a productos",
                        callback_data="admin_keys"
                    )

                ]

            ])

        )

        return


# =====================================
# AGREGAR PRECIOS PRODUCTO
# =====================================

    if estado == "agregar_precios":

        producto = SESIONES[telegram_id]["producto_nuevo"]

        planes = SESIONES[telegram_id]["planes_nuevos"]


        precios = texto.split("\n")


        precios = [
            precio.strip()
            for precio in precios
            if precio.strip()
        ]


        if len(planes) != len(precios):

            await update.message.reply_text(

                "❌ La cantidad de planes y precios no coincide.\n\n"
                f"📋 Planes: {len(planes)}\n"
                f"💵 Precios: {len(precios)}\n\n"
                "Escribe nuevamente los precios separados por línea."

            )

            return


        datos = productos()


        datos[producto] = {}


        for i in range(len(planes)):

            datos[producto][planes[i]] = float(precios[i])


        guardar(
            ARCHIVO_PRODUCTOS,
            datos
        )


        SESIONES.pop(
            telegram_id,
            None
        )


        await update.message.reply_text(

            "✅ PRODUCTO AGREGADO CORRECTAMENTE\n\n"
            f"📦 Producto: {producto}\n\n"
            "📋 Planes agregados:\n\n"
            +
            "\n".join(
                f"🔹 {planes[i]} ➜ {precios[i]} USD"
                for i in range(len(planes))
            ),

            reply_markup=InlineKeyboardMarkup([

                [

                    InlineKeyboardButton(
                        "📦 Volver a productos",
                        callback_data="admin_keys"
                    )

                ]

            ])

        )

        return


    # ==========================
    # LOGIN USUARIO
    # ==========================

    if estado == "usuario":

        if texto not in usuarios():

            botones = [
                [
                    InlineKeyboardButton(
                        "⬅️ Regresar",
                        callback_data="inicio"
                    )
                ]
            ]

            await update.message.reply_text(
                "❌ Usuario incorrecto",
                reply_markup=InlineKeyboardMarkup(botones)
            )

            SESIONES.pop(telegram_id)

            return


        SESIONES[telegram_id] = {
            "estado": "password",
            "usuario": texto
        }


        await update.message.reply_text(
            "🔑 Usuario recibido.\n\nAhora ingresa tu contraseña:",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "⬅️ Volver al inicio",
                        callback_data="inicio"
                    )
                ]
            ])
        )

        return

    # ==========================
    # VALIDAR PASSWORD
    # ==========================

    if estado == "password":

        usuario = SESIONES[telegram_id]["usuario"]


        if usuarios()[usuario]["password"] != texto:

            await update.message.reply_text(
                "❌ Contraseña incorrecta",
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(
                            "⬅️ Volver al inicio",
                            callback_data="inicio"
                        )
                    ]
                ])
            )

            SESIONES.pop(
                telegram_id
            )

            return


        SESIONES[telegram_id] = {
            "estado": "activo",
            "usuario": usuario
        }


        await update.message.reply_text(
            "✅ Inicio de sesión exitoso"
        )


        await mostrar_menu(
            update,
            context
        )

        return

# ================================
# MODIFICAR SALDO ADMIN
# ================================

    if estado == "monto_saldo":

        try:
            monto = float(texto)

        except ValueError:

            await update.message.reply_text(
                "❌ Ingresa solamente números"
            )

            return


        usuario = SESIONES[telegram_id].get(
            "usuario_saldo"
        )


        tipo = SESIONES[telegram_id].get(
            "tipo_saldo",
            "sumar"
        )


        if tipo == "sumar":

            agregar_saldo(
                usuario,
                monto
            )

            guardar_recarga(
                usuario,
                monto
            )

            saldo_actual = saldo_usuario(usuario)


            mensaje = (
                "✅ SALDO AGREGADO CORRECTAMENTE\n\n"
                f"👤 Usuario: {usuario}\n"
                f"💰 Saldo agregado: {monto} USD\n"
                f"💵 Saldo actual: {saldo_actual} USD"
            )


        elif tipo == "restar":

            saldo_actual = saldo_usuario(usuario)


            if saldo_actual >= monto:

                quitar_saldo(
                    usuario,
                    monto
                )

                saldo_actual = saldo_usuario(usuario)


                mensaje = (
                    "✅ SALDO DESCONTADO CORRECTAMENTE\n\n"
                    f"👤 Usuario: {usuario}\n"
                    f"💰 Saldo descontado: {monto} USD\n"
                    f"💵 Saldo actual: {saldo_actual} USD"
                )

            else:

                mensaje = (
                    "❌ El usuario no tiene saldo suficiente"
                )


        await update.message.reply_text(

            mensaje,

            reply_markup=InlineKeyboardMarkup([

            [

            InlineKeyboardButton(
                "↩️ Volver al administrador",
                callback_data="admin"
            )

        ]

    ])

)

        SESIONES.pop(
            telegram_id,
            None
        )

        return


# =====================================
# ADMIN AGREGAR KEYS
# =====================================

    if estado == "agregar_keys":

        print("ENTRO A GUARDAR KEYS")

        producto = SESIONES[telegram_id]["producto_keys"]

        plan = SESIONES[telegram_id]["plan_keys"]

        lista = texto.split("\n")

        lista = [
            key.strip()
            for key in lista
            if key.strip()
        ]

        guardar_keys_nuevas(
            producto,
            plan,
            lista
        )


        stock_actual = len(
            keys()
            .get(producto,{})
            .get(plan,[])
        )


        await update.message.reply_text(

            "✅ KEYS AGREGADAS CORRECTAMENTE\n\n"
            f"📦 Producto: {producto}\n"
            f"🔑 Plan: {plan}\n\n"
            f"➕ Keys agregadas: {len(lista)}\n"
            f"📊 Stock actual: {stock_actual}",

            reply_markup=InlineKeyboardMarkup([

                [
                    InlineKeyboardButton(
                        "📦 Volver a productos",
                        callback_data="admin_keys"
                    )
                ],

                [
                    InlineKeyboardButton(
                        "⚙️ Panel administrador",
                        callback_data="admin"
                    )
                ]

            ])

        )


        SESIONES.pop(
            telegram_id,
            None
        )

        return


# =====================================
# MENÚ PRINCIPAL CLIENTE
# =====================================


async def mostrar_menu(update,context):

    if update.callback_query:
        telegram_id = str(update.callback_query.from_user.id)
    else:
        telegram_id = str(update.message.from_user.id)

    usuario = SESIONES[telegram_id]["usuario"]

    botones = [

        [
            InlineKeyboardButton(
                "🛒 Comprar",
                callback_data="productos"
            )
        ],

        [
            InlineKeyboardButton(
                "👤 Perfil",
                callback_data="perfil"
            )
        ],

        [
            InlineKeyboardButton(
                "➕ Agregar saldo",
                callback_data="saldo"
            )
        ],

        [
            InlineKeyboardButton(
                "🚪 Salir",
                callback_data="salir"
            )
        ]

    ]


    if telegram_id == str(ADMIN_ID):

        botones.append(

            [
                InlineKeyboardButton(
                    "⚙️ Administrador",
                    callback_data="admin"
                )
            ]

        )


    await update.message.reply_text(
    "👑 BIENVENIDO A GUSBER MODS\n"
    "        Tu mejor opción ❤️\n\n"
    f"👤 Usuario: {usuario}\n\n"
    f"💰 Saldo actual: {saldo_usuario(usuario)} USD",
    reply_markup=InlineKeyboardMarkup(botones)
)

    return


# =====================================
# MOSTRAR PERFIL
# =====================================

async def mostrar_perfil(query, usuario):

    datos_usuarios = usuarios()

    compras_usuario = compras().get(
        usuario,
        []
    )

    recargas_usuario = cargar(
        ARCHIVO_RECARGAS
    ).get(
        usuario,
        []
    )

    datos_usuario = datos_usuarios.get(usuario, {})

    fecha_registro = datos_usuario.get(
        "fecha",
        datos_usuario.get(
            "fecha_registro",
            "No disponible"
        )
    )

    texto = (
        "👤 PERFIL\n\n"
        f"👤 Usuario: {usuario}\n"
        f"💰 Saldo actual: {saldo_usuario(usuario)} USD\n"
        f"📅 Registro: {fecha_registro}\n"
        f"🔄 Recargas: {len(recargas_usuario)}\n"
        f"🛒 Compras: {len(compras_usuario)}"
    )

    await query.edit_message_text(
        texto,
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "⬅️ Regresar",
                    callback_data="menu"
                )
            ]
        ])
    )



# =====================================
# PRODUCTOS
# =====================================


async def mostrar_productos(query):


    datos=productos()


    botones=[]


    for producto in datos:


        botones.append([

            InlineKeyboardButton(

                f"📦 {producto}",

                callback_data=f"producto|{producto}"

            )

        ])



    botones.append([

        InlineKeyboardButton(

            "⬅️ Regresar",

            callback_data="menu"

        )

    ])



    await query.edit_message_text(

        "🛒 PRODUCTOS DISPONIBLES",

        reply_markup=InlineKeyboardMarkup(botones)

    )



# =====================================
# PLANES PRODUCTO
# =====================================


async def mostrar_planes(query,producto):


    datos=productos()
    
    telegram_id = str(query.from_user.id)

    usuario = SESIONES.get(telegram_id, 
{}).get("usuario")


    botones=[]


    for plan,precio in datos[producto].items():

        disponibles = len(
            keys().get(producto, {}).get(plan, [])
        )  

        if disponibles == 0 and usuario != "Gusber Mods":
           continue

        botones.append([

            InlineKeyboardButton(

                f"🔑 {plan} ➜ {precio} USD | Stock: {disponibles}",

                callback_data=f"plan|{producto}|{plan}"

            )

        ])



    botones.append([

        InlineKeyboardButton(

            "⬅️ Regresar",

            callback_data="productos"

        )

    ])



    await query.edit_message_text(

        f"📦 {producto}\n\n"
        "Selecciona tu Key:",

        reply_markup=InlineKeyboardMarkup(botones)

    )


# =====================================
# MANEJO DE BOTONES
# =====================================

async def botones(update,context):

    query=update.callback_query 

    print("ENTRO AL CONTROLADOR DE BOTONES")

    await query.answer()

    telegram_id=str(
        query.from_user.id
    )

    data=query.data 

    print("BOTON PRESIONADO:", data)


    if data=="admin_keys":

        SESIONES.pop(
            telegram_id,
            None
        )

        await mostrar_productos_keys(query)

        return
 
# =================================
# ELIMINAR PRODUCTO
# =================================

    if data=="eliminar_producto":

        await query.edit_message_text(
            "❌ Selecciona el producto que deseas eliminar:"
        )

        await mostrar_productos_eliminar(query)

        return


    if data.startswith("eliminar_producto_confirmar|"):

        producto = data.split("|")[1]

        await confirmar_eliminar_producto(
            query,
            producto
        )

        return


    if data.startswith("confirmar_eliminar_producto|"):

        producto = data.split("|")[1]

        eliminar_producto(producto)

        await query.edit_message_text(

            "✅ PRODUCTO ELIMINADO CORRECTAMENTE",

            reply_markup=InlineKeyboardMarkup([

                [

                    InlineKeyboardButton(
                        "⬅️ Volver a productos",
                        callback_data="admin_keys"
                    )

                ]

            ])

        )

        return

  
    # =================================
    # SELECCIONAR USUARIO PARA SALDO
    # =================================

    if data.startswith("saldo_usuario|"):

        usuario = data.split("|")[1]

        SESIONES[telegram_id] = {
            "estado": "monto_saldo",
            "usuario_saldo": usuario,
            "tipo_saldo": context.user_data.get("tipo_saldo", "sumar")
        }

        await query.edit_message_text(
            f"💰 MODIFICAR SALDO\n\n"
            f"👤 Usuario seleccionado: {usuario}\n\n"
            "✍️ Escribe el monto que deseas agregar:",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "↩️ Volver al administrador",
                        callback_data="admin"
                    )
                ]
            ])
        )

        return


    # ADMIN - FUNCIONES

    if data=="crear_usuario":

        SESIONES[telegram_id]={
            "estado":"crear_usuario"
        }

        await query.edit_message_text(
            "🔑 Escribe el nombre del nuevo usuario:",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "↩️ Volver al administrador",
                        callback_data="admin"
                    )
                ]
            ])
        )

        return

    if data=="agregar_producto":

        SESIONES[telegram_id] = {
            "estado": "agregar_producto"
        }

        await query.edit_message_text(
            "📦 AGREGAR PRODUCTO\n\n"
            "Escribe el nombre del nuevo producto:",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "⬅️ Volver a productos",
                        callback_data="admin_keys"
                    )
                ]
            ])
        )

        return


    if data=="admin_saldo":

        botones=[
            [
                InlineKeyboardButton(
                    "➕ Sumar saldo",
                    callback_data="sumar_saldo"
                )
            ],
            [
                InlineKeyboardButton(
                    "➖ Restar saldo",
                    callback_data="restar_saldo"
                )
            ],
            [
                InlineKeyboardButton(
                    "↩️ Volver al administrador",
                    callback_data="admin"
                )
            ]
        ]

        await query.edit_message_text(
            "💰 CENTRO DE RECARGAS\n\n"
            "Selecciona una opción:",
            reply_markup=InlineKeyboardMarkup(botones)
        )

        return


    if data=="sumar_saldo":

        await lista_usuarios_saldo(query)

        context.user_data["tipo_saldo"]="sumar"

        return


    if data=="restar_saldo":

        await lista_usuarios_saldo(query)

        context.user_data["tipo_saldo"]="restar"

        return


    if data=="admin_keys":

        await query.edit_message_text(
            "🔑 Selecciona producto:"
        )

        await mostrar_productos_keys(query)

        return

    if data=="eliminar_producto":

        await mostrar_productos_eliminar(query)

        return


    if data=="usuarios_admin":

        await mostrar_usuarios_admin(query)

        return

    if data=="historial_compras":

        await mostrar_usuarios_historial(query)

        return

    if data.startswith("ver_historial_usuario|"):

        usuario = data.split("|")[1]

        await mostrar_historial_usuario(
            query,
            usuario
        )

        return


# =================================
# ELIMINAR COMPRA DIRECTAMENTE
# =================================

    if data.startswith("eliminar_compra|"):

        partes = data.split("|")

        usuario = partes[1]
        indice = int(partes[2])


        datos = compras()


        compra = None


        if usuario in datos:

            if indice < len(datos[usuario]):

                compra = datos[usuario].pop(indice)

                guardar(
                    ARCHIVO_COMPRAS,
                    datos
                )


        if compra:

            await query.edit_message_text(

                "✅ COMPRA ELIMINADA CORRECTAMENTE\n\n"
                f"👤 Usuario: {usuario}\n"
                f"🧾 Compra eliminada: #{indice+1}\n\n"
                f"📦 Producto: {compra['producto']}\n"
                f"🔑 Plan: {compra['plan']}",

                reply_markup=InlineKeyboardMarkup([

                    [

                        InlineKeyboardButton(
                            "🧾 Ver historial nuevamente",
                            callback_data=f"ver_historial_usuario|{usuario}"
                        )

                    ],

                    [

                        InlineKeyboardButton(
                            "⚙️ Administrador",
                            callback_data="admin"
                        )

                    ]

                ])

            )

        else:

            await query.edit_message_text(

                "❌ No se pudo encontrar la compra.",

                reply_markup=InlineKeyboardMarkup([

                    [

                        InlineKeyboardButton(
                            "🧾 Volver historial",
                            callback_data=f"ver_historial_usuario|{usuario}"
                        )

                    ]

                ])

            )


        return


# =================================
# ADMIN KEYS - SELECCIONAR PRODUCTO
# =================================

    if data.startswith("keys_producto|"):

        producto = data.split("|")[1]

        await mostrar_planes_keys(
            query,
            producto
        )

        return


# =================================
# ADMIN KEYS - SELECCIONAR PLAN
# =================================

    if data.startswith("keys_plan|"):

        partes = data.split("|")

        producto = partes[1]
        plan = partes[2]

        await pedir_keys(
            query,
            telegram_id,
            producto,
            plan
        )

        return


# VER INFORMACIÓN DE USUARIO ADMIN

    if data.startswith("ver_usuario_admin|"):

        nombre = data.split("|")[1]

        await detalle_usuario_admin(
            query,
            nombre
        )

        return


    # CONFIRMAR ELIMINACIÓN DE USUARIO

    if data.startswith("eliminar_usuario|"):

        nombre = data.split("|")[1]

        botones = [

            [
                InlineKeyboardButton(
                    "✅ Confirmar eliminación",
                    callback_data=f"confirmar_eliminar|{nombre}"
                )
            ],

            [
                InlineKeyboardButton(
                    "⬅️ Atrás",
                    callback_data=f"ver_usuario_admin|{nombre}"
                )
            ]

        ]


        await query.edit_message_text(

            "⚠️ ¿ESTÁS SEGURO QUE DESEAS ELIMINAR ESTE USUARIO?\n\n"
            f"👤 Usuario: {nombre}\n\n"
            "Esta acción no se puede deshacer.",

            reply_markup=InlineKeyboardMarkup(botones)

        )

        return


    # CONFIRMAR ELIMINACIÓN

    if data.startswith("confirmar_eliminar|"):

        nombre = data.split("|")[1]


        eliminar_usuario(nombre)


        await query.edit_message_text(

            "✅ USUARIO ELIMINADO CORRECTAMENTE",

            reply_markup=InlineKeyboardMarkup([

                [
                    InlineKeyboardButton(
                        "👥 Volver a usuarios registrados",
                        callback_data="usuarios_admin"
                    )
                ]

            ])

        )

        return


    # VOLVER INICIO

    if data=="inicio":

        await query.edit_message_text(
            "👑 BIENVENIDO A GUSBER MODS\n"
            "         Tu mejor opción ❤️\n\n"
            "Selecciona una opción:",
            reply_markup=InlineKeyboardMarkup([

                [
                    InlineKeyboardButton(
                        "🔑 Iniciar sesión",
                        callback_data="login"
                    )
                ],

                [
                    InlineKeyboardButton(
                        "🛠 Soporte",
                        callback_data="soporte"
                    )
                ]

            ])
        )

        return



    # LOGIN

    if data=="login":

        await pedir_usuario(
            update,
            context
        )

        return



    # SOPORTE

    if data=="soporte":

        await query.edit_message_text(

            "🛠 SOPORTE\n\n"
            "Para ayudarte con tu inicio de sesión "
            "comunícate por WhatsApp.",

            reply_markup=InlineKeyboardMarkup([

                [

                    InlineKeyboardButton(
                        "⬅️ Regresar",
                        callback_data="inicio"
                    )

                ]

            ])

        )

        return



    # MENU

    if data=="menu":

        usuario = SESIONES.get(telegram_id, {}).get("usuario")

        if not usuario:

            if telegram_id == str(ADMIN_ID):

                usuario = "Gusber Mods"

            else:

                await query.edit_message_text(
                    "❌ Sesión no encontrada. Inicia sesión nuevamente."
                )

                return


        botones=[

            [
                InlineKeyboardButton(
                    "🛒 Comprar",
                    callback_data="productos"
                )
            ],

            [
                InlineKeyboardButton(
                    "👤 Perfil",
                    callback_data="perfil"
                )
            ],

            [
                InlineKeyboardButton(
                    "➕ Agregar saldo",
                    callback_data="saldo"
                )
            ],

            [
                InlineKeyboardButton(
                    "🚪 Salir",
                    callback_data="salir"
                )
            ]

        ]

        if telegram_id == str(ADMIN_ID):
            botones.append(
              [

               InlineKeyboardButton(
                "⚙️ Administrador",
                callback_data="admin"
              )
           ]
        )

        await query.edit_message_text(
    "👑 BIENVENIDO A GUSBER MODS\n"
    "Tu mejor opción ❤️\n\n"
    f"👤 Usuario: {usuario}\n\n"
    f"💰 Saldo actual: {saldo_usuario(usuario)} USD",
    reply_markup=InlineKeyboardMarkup(botones)
)
        return



    # PERFIL

    if data=="perfil":

        usuario = SESIONES.get(telegram_id, {}).get("usuario")


        if not usuario and telegram_id == str(ADMIN_ID):

            usuario = "Gusber Mods"


        await mostrar_perfil(
            query,
            usuario
        )

        return


    # AGREGAR SALDO CLIENTE

    if data=="saldo":

        await query.edit_message_text(

            "➕ AGREGAR SALDO\n\n"
            "Para recargar saldo comunícate "
            "con el administrador por WhatsApp.",

            reply_markup=InlineKeyboardMarkup([

                [

                    InlineKeyboardButton(
                        "⬅️ Regresar",
                        callback_data="menu"
                    )

                ]

            ])

        )

        return



    # PRODUCTOS

    if data=="productos":

        await mostrar_productos(
            query
        )

        return



    # PRODUCTO SELECCIONADO

    if data.startswith("producto|"):

        producto=data.split("|")[1]

        await mostrar_planes(
            query,
            producto
        )

        return



    # PLAN SELECCIONADO

    if data.startswith("plan|"):

        partes=data.split("|")

        producto=partes[1]

        plan=partes[2]

        precio=productos()[producto][plan]


        botones=[

            [

                InlineKeyboardButton(
                    "✅ Confirmar compra",
                    callback_data=f"comprar|{producto}|{plan}"
                )

            ],

            [

                InlineKeyboardButton(
                    "⬅️ Regresar",
                    callback_data="productos"
                )

            ]

        ]


        await query.edit_message_text(

            "🧾 CONFIRMAR COMPRA\n\n"
            f"📦 Producto: {producto}\n"
            f"🔑 Plan: {plan}\n"
            f"💵 Precio: {precio} USD\n\n"
            "¿Deseas comprar?",

            reply_markup=InlineKeyboardMarkup(botones)

        )

        return



    # COMPRAR

    if data.startswith("comprar|"):

        partes=data.split("|")

        producto=partes[1]

        plan=partes[2]

        usuario = SESIONES.get(telegram_id, {}).get("usuario")


        if not usuario and telegram_id == str(ADMIN_ID):
           usuario = "Gusber Mods"

        resultado=realizar_compra(
            usuario,
            producto,
            plan
        )


        if resultado=="SALDO":

            await query.edit_message_text(

                "❌ Saldo insuficiente",

                reply_markup=InlineKeyboardMarkup([

                    [

                        InlineKeyboardButton(
                            "⬅️ Regresar",
                            callback_data="productos"
                        )

                    ]

                ])

            )

            return



        if resultado=="KEY":

            await query.edit_message_text(
                "❌ No hay Keys disponibles"
            )

            return



        await query.edit_message_text(

            "✅ COMPRA EXITOSA\n\n"
            f"📦 {resultado['producto']}\n"
            f"🔑 Key:\n{resultado['key']}",

            reply_markup=InlineKeyboardMarkup([

                [

                    InlineKeyboardButton(
                        "🏠 Menú",
                        callback_data="menu"
                    )

                ]

            ])

        )

        return



    # SALIR

    if data=="salir":

        SESIONES.pop(
            telegram_id,
            None
        )


        await query.edit_message_text(

            "Sesión cerrada.",

            reply_markup=InlineKeyboardMarkup([

                [

                    InlineKeyboardButton(
                        "⬅️ Inicio",
                        callback_data="inicio"
                    )

                ]

            ])

        )

        return



    # =================================
    # ADMIN
    # =================================


    if data=="admin":


        if int(telegram_id)!=ADMIN_ID:

            return


        botones=[

            [

                InlineKeyboardButton(
                    "👥 Crear usuario",
                    callback_data="crear_usuario"
                )

            ],

            [

                InlineKeyboardButton(
                    "💰 Agregar saldo",
                    callback_data="admin_saldo"
                )

            ],

            [

                InlineKeyboardButton(
                    "🔑 Agregar Keys",
                    callback_data="admin_keys"
                )

            ],

            [

                InlineKeyboardButton(
                    "📋 Usuarios",
                    callback_data="usuarios_admin"
                )

            ],

            [
            InlineKeyboardButton(
                "🧾 Historial de compras",
                callback_data="historial_compras"
                )
            ],

            [

                InlineKeyboardButton(
                    "🏠 Regresar al menú",
                    callback_data="menu"
                )

            ]

        ]


        await query.edit_message_text(

            "⚙️ PANEL ADMINISTRADOR",

            reply_markup=InlineKeyboardMarkup(botones)

        )

        return


# =====================================
# ADMIN - GESTIÓN DE USUARIOS
# =====================================


def obtener_usuarios_admin():

    return cargar(
        ARCHIVO_USUARIOS
    )



def eliminar_usuario(nombre):

    datos = cargar(
        ARCHIVO_USUARIOS
    )


    if nombre in datos:

        del datos[nombre]

        guardar(
            ARCHIVO_USUARIOS,
            datos
        )


    saldos = cargar(
        ARCHIVO_SALDOS
    )


    if nombre in saldos:

        del saldos[nombre]

        guardar(
            ARCHIVO_SALDOS,
            saldos
        )


    compras_datos = cargar(
        ARCHIVO_COMPRAS
    )


    if nombre in compras_datos:

        del compras_datos[nombre]

        guardar(
            ARCHIVO_COMPRAS,
            compras_datos
        )



def editar_usuario(nombre,nuevo_usuario,nueva_password):

    datos=cargar(
        ARCHIVO_USUARIOS
    )


    if nombre not in datos:
        return False


    datos[nuevo_usuario]={

        "password":nueva_password,

        "fecha":datos[nombre]["fecha"]

    }


    if nuevo_usuario != nombre:

        del datos[nombre]


    guardar(
        ARCHIVO_USUARIOS,
        datos
    )


    return True



def total_compras_usuario(nombre):

    datos=cargar(
        ARCHIVO_COMPRAS
    )


    return len(
        datos.get(nombre,[])
    )



# =====================================
# BOTONES LISTA USUARIOS ADMIN
# =====================================

async def mostrar_usuarios_admin(query):

    datos = obtener_usuarios_admin()

    botones = []

    for usuario in datos:

        botones.append([

            InlineKeyboardButton(
                f"👤 {usuario}",
                callback_data=f"ver_usuario_admin|{usuario}"
            )

        ])


    botones.append([

        InlineKeyboardButton(
            "⬅️ Volver",
            callback_data="admin"
        )

    ])


    await query.edit_message_text(

        "📋 USUARIOS REGISTRADOS",

        reply_markup=InlineKeyboardMarkup(botones)

    )


# =====================================
# DETALLE USUARIO ADMIN
# =====================================


async def detalle_usuario_admin(query,nombre):


    datos=usuarios()


    if nombre not in datos:
        return



    botones=[


        [

            InlineKeyboardButton(

                "🗑 Eliminar usuario",

                callback_data=f"eliminar_usuario|{nombre}"

            )

        ],


        [

            InlineKeyboardButton(

                "⬅️ Volver",

                callback_data="usuarios_admin"

            )

        ]

    ]


    fecha_registro = datos[nombre].get(
      "fecha",
       datos[nombre].get(
         "fecha_registro",
         "No disponible"
       )
    )

    texto=(

        "👤 INFORMACIÓN USUARIO\n\n"

        f"Usuario: {nombre}\n"

        f"🔐 Contraseña: {datos[nombre]['password']}\n"

        f"📅 Registro: {datos[nombre].get('fecha', datos[nombre].get('fecha_registro', 'No disponible'))}\n"

        f"💰 Saldo: {saldo_usuario(nombre)} USD\n"

        f"🛒 Compras realizadas: {total_compras_usuario(nombre)}"

    )



    await query.edit_message_text(

        texto,

        reply_markup=InlineKeyboardMarkup(botones)

    )



# =====================================
# CREAR USUARIO ADMIN
# =====================================


async def iniciar_crear_usuario(query,telegram_id):


    SESIONES[telegram_id]={

        "estado":"crear_usuario_nombre"

    }


    await query.edit_message_text(

        "👤 CREAR USUARIO\n\n"
        "Escribe el nombre de usuario:"

    )



# =====================================
# AGREGAR SALDO ADMIN
# =====================================


async def lista_usuarios_saldo(query):

    datos = usuarios()

    botones = []


    for usuario in datos:

        botones.append([

            InlineKeyboardButton(
                f"👤 {usuario}",
                callback_data=f"saldo_usuario|{usuario}"
            )

        ])


    botones.append([

        InlineKeyboardButton(
            "⬅️ Volver al administrador",
            callback_data="admin"
        )

    ])


    await query.edit_message_text(

        "👥 SELECCIONA USUARIO\n\n"
        "Elige el usuario al que deseas modificar el saldo:",

        reply_markup=InlineKeyboardMarkup(botones)

    )


# =====================================
# ADMIN - AGREGAR KEYS
# =====================================


async def mostrar_productos_keys(query):


    datos=productos()


    botones=[]


    botones.append([

        InlineKeyboardButton(

            "➕ Agregar producto",

            callback_data="agregar_producto"

        )

    ])


    botones.append([

        InlineKeyboardButton(

            "❌ Eliminar producto",

            callback_data="eliminar_producto"

        )

    ])


    for producto in datos:


        botones.append([

            InlineKeyboardButton(

                f"📦 {producto}",

                callback_data=f"keys_producto|{producto}"

            )

        ])



    botones.append([

        InlineKeyboardButton(

            "⬅️ Volver",

            callback_data="admin"

        )

    ])



    await query.edit_message_text(

        "🔑 AGREGAR KEYS\n\n"
        "Selecciona un producto:",

        reply_markup=InlineKeyboardMarkup(botones)

    )



# =====================================
# PLANES PARA AGREGAR KEYS
# =====================================


async def mostrar_planes_keys(query, producto):


    datos = productos()


    botones = []


    for plan in datos[producto]:


        stock = len(
            keys()
            .get(producto, {})
            .get(plan, [])
        )


        botones.append([

            InlineKeyboardButton(

                f"🔑 {plan} | Stock: {stock}",

                callback_data=f"keys_plan|{producto}|{plan}"

            )

        ])



    botones.append([

        InlineKeyboardButton(

            "⬅️ Volver",

            callback_data="admin_keys"

        )

    ])



    await query.edit_message_text(

        f"📦 Producto: {producto}\n\n"
        "Selecciona duración:",

        reply_markup=InlineKeyboardMarkup(botones)

    )



# =====================================
# PEDIR KEYS
# =====================================


async def pedir_keys(query,telegram_id,producto,plan):

    print("ENTRO A PEDIR KEYS")

    SESIONES[telegram_id]={

        "estado":"agregar_keys",

        "producto_keys":producto,

        "plan_keys":plan

    }



    await query.message.reply_text(

    f"🔑 AGREGAR KEYS\n\n"
    f"Producto: {producto}\n"
    f"Plan: {plan}\n\n"
    "Escribe todas las Keys que deseas agregar.\n\n"
    "Puedes poner una por línea:",

    reply_markup=InlineKeyboardMarkup([

        [

            InlineKeyboardButton(
                "❌ Cancelar",
                callback_data="admin_keys"
            )

        ]

    ])

)



# =====================================
# GUARDAR KEYS
# =====================================


def guardar_keys_nuevas(producto,plan,nuevas):


    datos=cargar(
        ARCHIVO_KEYS
    )


    if producto not in datos:

        datos[producto]={}



    if plan not in datos[producto]:

        datos[producto][plan]=[]



    for key in nuevas:

        if key.strip():

            datos[producto][plan].append(
                key.strip()
            )



    guardar(

        ARCHIVO_KEYS,

        datos

    )



# =====================================
# CONFIRMACION AGREGAR KEYS
# =====================================


async def confirmar_keys(query,producto,plan):


    botones=[

        [

            InlineKeyboardButton(

                "➕ Agregar más Keys",

                callback_data=f"keys_plan|{producto}|{plan}"

            )

        ],

        [

            InlineKeyboardButton(

                "⬅️ Volver productos",

                callback_data="admin_keys"

            )

        ],


        [

            InlineKeyboardButton(

                "⚙️ Panel administrador",

                callback_data="admin"

            )

        ]

    ]



    await query.edit_message_text(

        "✅ KEYS AGREGADAS CORRECTAMENTE",

        reply_markup=InlineKeyboardMarkup(botones)

    )



# =====================================
# EDITAR USUARIO
# =====================================


async def pedir_editar_usuario(query,telegram_id,nombre):


    SESIONES[telegram_id]={

        "estado":"editar_usuario",

        "usuario_editar":nombre

    }


    await query.edit_message_text(

        f"✏️ EDITAR USUARIO\n\n"
        f"Usuario actual: {nombre}\n\n"
        "Escribe el nuevo usuario:",

        reply_markup=InlineKeyboardMarkup([

            [

                InlineKeyboardButton(

                    "❌ Cancelar",

                    callback_data="usuarios_admin"

                )

            ]

        ])

    )


# =====================================
# ADMIN CREAR USUARIO
# =====================================


    if estado=="crear_usuario_nombre":

        SESIONES[telegram_id]["nuevo_usuario"]=texto

        SESIONES[telegram_id]["estado"]="crear_usuario_password"


        await update.message.reply_text(
            "🔐 Ahora escribe la contraseña:"
        )

        return



    if estado=="crear_usuario_password":

        usuario_nuevo=SESIONES[telegram_id]["nuevo_usuario"]


        if crear_usuario(usuario_nuevo,texto):

            await update.message.reply_text(
    "✅ REGISTRO EXITOSO\n\n"
    f"👤 Usuario: {usuario_nuevo}\n"
    f"📅 Fecha: {fecha()}",
    reply_markup=InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "⚙️ Volver al administrador",
                callback_data="admin"
            )
        ]
    ])
)

        else:

            await update.message.reply_text(

                "❌ Ese usuario ya existe"

            )


        SESIONES.pop(
            telegram_id,
            None
        )


        return   


    
# =====================================
# ELIMINAR PRODUCTOS - LISTA
# =====================================

async def mostrar_productos_eliminar(query):

    datos = productos()

    botones = []


    for producto in datos:

        botones.append([

            InlineKeyboardButton(
                f"❌ {producto}",
                callback_data=f"eliminar_producto_confirmar|{producto}"
            )

        ])


    botones.append([

        InlineKeyboardButton(
            "⬅️ Volver",
            callback_data="admin_keys"
        )

    ])


    await query.edit_message_text(

        "❌ PRODUCTOS REGISTRADOS\n\n"
        "Selecciona el producto que deseas eliminar:",

        reply_markup=InlineKeyboardMarkup(botones)

    )


# =====================================
# ELIMINAR PRODUCTO DEFINITIVO
# =====================================

def eliminar_producto(producto):

    datos = productos()


    if producto in datos:

        del datos[producto]

        guardar(
            ARCHIVO_PRODUCTOS,
            datos
        )


    datos_keys = keys()


    if producto in datos_keys:

        del datos_keys[producto]

        guardar(
            ARCHIVO_KEYS,
            datos_keys
        )

    
# =====================================
# CONFIRMAR ELIMINACIÓN DE PRODUCTO
# =====================================

async def confirmar_eliminar_producto(query, producto):

    datos_keys = keys()

    stock = 0

    if producto in datos_keys:

        for plan in datos_keys[producto]:

            stock += len(
                datos_keys[producto][plan]
            )


    historial = compras()

    ventas = 0
    ingresos = 0


    for usuario in historial:

        for compra in historial[usuario]:

            if compra["producto"] == producto:

                ventas += 1

                ingresos += compra["precio"]


    botones = [

        [
            InlineKeyboardButton(
                "✅ Confirmar eliminación",
                callback_data=f"confirmar_eliminar_producto|{producto}"
            )
        ],

        [
            InlineKeyboardButton(
                "⬅️ Cancelar",
                callback_data="eliminar_producto"
            )
        ]

    ]


    await query.edit_message_text(

        "📦 INFORMACIÓN DEL PRODUCTO\n\n"
        f"📌 Producto: {producto}\n\n"
        f"🔑 Keys disponibles: {stock}\n"
        f"🛒 Ventas realizadas: {ventas}\n"
        f"💵 Ingresos generados: {ingresos} USD\n\n"
        "⚠️ ¿Deseas eliminar este producto?",

        reply_markup=InlineKeyboardMarkup(botones)

    )


# =====================================
# LISTA USUARIOS CON HISTORIAL
# =====================================

async def mostrar_usuarios_historial(query):

    datos = compras()

    botones = []


    for usuario in datos:

        botones.append([

            InlineKeyboardButton(
                f"👤 {usuario}",
                callback_data=f"ver_historial_usuario|{usuario}"
            )

        ])


    botones.append([

        InlineKeyboardButton(
            "⬅️ Volver al administrador",
            callback_data="admin"
        )

    ])


    await query.edit_message_text(

        "🧾 HISTORIAL DE COMPRAS\n\n"
        "Selecciona un usuario para ver sus compras:",

        reply_markup=InlineKeyboardMarkup(botones)

    )


# =====================================
# HISTORIAL DE UN USUARIO
# =====================================

async def mostrar_historial_usuario(query, usuario):

    datos = compras()

    historial = datos.get(usuario, [])


    if not historial:

        await query.edit_message_text(

            "❌ Este usuario no tiene compras.",

            reply_markup=InlineKeyboardMarkup([

                [

                    InlineKeyboardButton(
                        "⬅️ Volver usuarios",
                        callback_data="historial_compras"
                    )

                ]

            ])

        )

        return



    await query.edit_message_text(

        "🧾 HISTORIAL DE COMPRAS\n\n"
        f"👤 Usuario: {usuario}\n\n"
        "📦 Mostrando compras..."

    )



    for indice, compra in enumerate(historial):


        texto = (

            "━━━━━━━━━━━━━━\n"
            f"🧾 COMPRA #{indice+1}\n\n"
            f"📦 Producto: {compra['producto']}\n"
            f"🔑 Plan: {compra['plan']}\n"
            f"💵 Precio: {compra['precio']} USD\n"
            f"📅 Fecha: {compra['fecha']}\n"
            f"🔐 Key:\n{compra['key']}\n"

        )



        botones = [

            [

                InlineKeyboardButton(

                    f"🗑 Eliminar compra #{indice+1}",

                    callback_data=f"eliminar_compra|{usuario}|{indice}"

                )

            ]

        ]



        await query.message.reply_text(

            texto,

            reply_markup=InlineKeyboardMarkup(botones)

        )



    await query.message.reply_text(

        "✅ FIN DEL HISTORIAL",

        reply_markup=InlineKeyboardMarkup([

            [

                InlineKeyboardButton(

                    "⬅️ Volver usuarios",

                    callback_data="historial_compras"

                )

            ],

            [

                InlineKeyboardButton(

                    "⚙️ Administrador",

                    callback_data="admin"

                )

            ]

        ])

    )


# =====================================
# CREAR APP
# =====================================


def main():

    app=Application.builder().token(TOKEN).build()


    app.add_handler(
        CommandHandler(
            "start",
            inicio
        )
    )


    app.add_handler(
        CallbackQueryHandler(
            botones
        )
    )


    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            recibir_texto
        )
    )


    print(
        "🤖 BOT INICIADO CORRECTAMENTE"
    )


    app.run_polling()



if __name__=="__main__":

    main()
