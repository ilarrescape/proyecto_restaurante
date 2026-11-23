
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# Ruta del proyecto para importar los servicios.
SRC_PATH = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SRC_PATH))

from services.database import SessionLocal

from services.restaurante_service import (
    crear_restaurante,
    listar_restaurantes,
    modificar_restaurante,
    eliminar_restaurante
)

from services.restaurante_cargo_empleado_service import (
    crear_asignacion,
    listar_asignaciones,
    buscar_asignacion,
    modificar_asignacion,
    eliminar_asignacion
)


# Configuración de la aplicación.
st.set_page_config(
    page_title="Gestión de Restaurantes",
    page_icon="🍽️",
    layout="wide"
)


def validar_cuit(cuit):
    return cuit.isdigit() and len(cuit) == 11


# ==================================================
# MÓDULO DE RESTAURANTES
# ==================================================

st.title("Gestión de Restaurantes")
st.write("Administración de restaurantes del sistema.")

st.header("Panel de análisis de restaurantes")


# Panel de análisis.
try:
    with SessionLocal() as db:
        restaurantes_panel = listar_restaurantes(db)

        datos_panel = [
            {
                "CUIT": r.cuit,
                "Nombre": r.nombre_fantasia,
                "Ciudad": r.id_ciudad
            }
            for r in restaurantes_panel
        ]

    if datos_panel:
        df = pd.DataFrame(datos_panel)

        total_restaurantes = len(df)
        total_ciudades = df["Ciudad"].nunique()

        promedio_ciudades = (
            total_restaurantes / total_ciudades
            if total_ciudades > 0 else 0
        )

        col1, col2, col3 = st.columns(3)

        col1.metric("Total de restaurantes", total_restaurantes)
        col2.metric("Ciudades con restaurantes", total_ciudades)
        col3.metric("Promedio por ciudad", round(promedio_ciudades, 2))

        restaurantes_ciudad = (
            df.groupby("Ciudad")
            .size()
            .reset_index(name="Cantidad")
        )

        restaurantes_ciudad["Ciudad"] = (
            restaurantes_ciudad["Ciudad"].apply(
                lambda x: f"Ciudad {x}"
            )
        )

        st.subheader("Cantidad de restaurantes por ciudad")

        grafico_barras = px.bar(
            restaurantes_ciudad,
            x="Ciudad",
            y="Cantidad",
            title="Restaurantes registrados por ciudad",
            text="Cantidad"
        )

        st.plotly_chart(
            grafico_barras,
            use_container_width=True
        )

        st.subheader("Distribución de restaurantes por ciudad")

        grafico_circular = px.pie(
            restaurantes_ciudad,
            names="Ciudad",
            values="Cantidad",
            title="Porcentaje de restaurantes por ciudad"
        )

        st.plotly_chart(
            grafico_circular,
            use_container_width=True
        )

    else:
        st.info("Todavía no hay restaurantes registrados para analizar.")

        col1, col2, col3 = st.columns(3)

        col1.metric("Total de restaurantes", 0)
        col2.metric("Ciudades con restaurantes", 0)
        col3.metric("Promedio por ciudad", 0)

except Exception as error:
    st.error(f"Error al cargar el panel de análisis: {error}")


# Pestañas de restaurantes.
tab_alta, tab_buscar, tab_modificar, tab_eliminar = st.tabs(
    ["Alta", "Buscar", "Modificar", "Eliminar"]
)


# ==================================================
# ALTA DE RESTAURANTES
# ==================================================

with tab_alta:
    st.subheader("Registrar restaurante")

    with st.form("form_alta_restaurante"):
        cuit = st.text_input("CUIT")
        razon_social = st.text_input("Razón social")
        nombre_fantasia = st.text_input("Nombre de fantasía")
        direccion = st.text_input("Dirección")

        id_ciudad = st.number_input(
            "ID de ciudad",
            min_value=1,
            step=1
        )

        enviar_restaurante = st.form_submit_button(
            "Registrar restaurante"
        )

        if enviar_restaurante:
            if not all([
                cuit,
                razon_social,
                nombre_fantasia,
                direccion
            ]):
                st.error("Todos los campos son obligatorios.")

            elif not validar_cuit(cuit):
                st.error("El CUIT debe contener 11 números.")

            else:
                try:
                    with SessionLocal() as db:
                        resultado = crear_restaurante(
                            db,
                            int(cuit),
                            razon_social,
                            nombre_fantasia,
                            direccion,
                            int(id_ciudad)
                        )

                    if resultado is not None:
                        st.success("Restaurante registrado correctamente.")
                    else:
                        st.error(
                            "No se pudo registrar. Verificá que el CUIT "
                            "no exista y que la ciudad esté registrada."
                        )

                except Exception as error:
                    st.error(f"No se pudo registrar: {error}")


# ==================================================
# BUSCAR RESTAURANTES
# ==================================================

with tab_buscar:
    st.subheader("Restaurantes registrados")

    if st.button("Mostrar restaurantes"):
        try:
            with SessionLocal() as db:
                restaurantes = listar_restaurantes(db)

                if restaurantes:
                    datos = [
                        {
                            "CUIT": r.cuit,
                            "Razón social": r.razon_social,
                            "Nombre": r.nombre_fantasia,
                            "Dirección": r.direccion,
                            "ID Ciudad": r.id_ciudad
                        }
                        for r in restaurantes
                    ]

                    st.dataframe(datos, use_container_width=True)

                else:
                    st.info("No hay restaurantes registrados.")

        except Exception as error:
            st.error(f"No se pudieron consultar los datos: {error}")


# ==================================================
# MODIFICAR RESTAURANTES
# ==================================================

with tab_modificar:
    st.subheader("Modificar restaurante")

    with st.form("form_modificar_restaurante"):
        cuit_modificar = st.text_input("CUIT del restaurante")
        nueva_razon = st.text_input("Nueva razón social")
        nuevo_nombre = st.text_input("Nuevo nombre de fantasía")
        nueva_direccion = st.text_input("Nueva dirección")

        nueva_ciudad = st.number_input(
            "Nuevo ID de ciudad",
            min_value=1,
            step=1,
            key="ciudad_modificar"
        )

        enviar_modificacion = st.form_submit_button("Guardar cambios")

        if enviar_modificacion:
            if not all([
                cuit_modificar,
                nueva_razon,
                nuevo_nombre,
                nueva_direccion
            ]):
                st.error("Todos los campos son obligatorios.")

            elif not validar_cuit(cuit_modificar):
                st.error("El CUIT debe contener 11 números.")

            else:
                try:
                    with SessionLocal() as db:
                        resultado = modificar_restaurante(
                            db,
                            int(cuit_modificar),
                            nueva_razon,
                            nuevo_nombre,
                            nueva_direccion,
                            int(nueva_ciudad)
                        )

                    if resultado is None:
                        st.warning(
                            "No se encontró el restaurante "
                            "o no se pudieron guardar los cambios."
                        )
                    else:
                        st.success("Restaurante modificado correctamente.")

                except Exception as error:
                    st.error(f"No se pudo modificar: {error}")


# ==================================================
# ELIMINAR RESTAURANTES
# ==================================================

with tab_eliminar:
    st.subheader("Eliminar restaurante")

    with st.form("form_eliminar_restaurante"):
        cuit_eliminar = st.text_input(
            "CUIT del restaurante a eliminar"
        )

        enviar_eliminacion = st.form_submit_button(
            "Eliminar restaurante"
        )

        if enviar_eliminacion:
            if not cuit_eliminar:
                st.error("Ingresá un CUIT.")

            elif not validar_cuit(cuit_eliminar):
                st.error("El CUIT debe contener 11 números.")

            else:
                try:
                    with SessionLocal() as db:
                        resultado = eliminar_restaurante(
                            db,
                            int(cuit_eliminar)
                        )

                    if resultado:
                        st.success("Restaurante eliminado correctamente.")
                    else:
                        st.warning("No se encontró ese restaurante.")

                except Exception as error:
                    st.error(f"No se pudo eliminar: {error}")


# ==================================================
# MÓDULO DE CARGOS Y EMPLEADOS
# ==================================================

st.divider()

st.title("Gestión de cargos y empleados")
st.header("Panel de análisis de asignaciones")


# Panel de análisis de asignaciones.
try:
    with SessionLocal() as db:
        asignaciones_panel = listar_asignaciones(db)

        datos_asignaciones = [
            {
                "Cargo": a.id_cargo,
                "Condición": a.id_condicion,
                "Restaurante": a.cuit_restaurante,
                "Empleado": a.dni_empleado
            }
            for a in asignaciones_panel
        ]

    if datos_asignaciones:
        df_asignaciones = pd.DataFrame(datos_asignaciones)

        total_asignaciones = len(df_asignaciones)
        total_empleados = df_asignaciones["Empleado"].nunique()
        total_restaurantes_asociados = (
            df_asignaciones["Restaurante"].nunique()
        )

        col1, col2, col3 = st.columns(3)

        col1.metric("Total de asignaciones", total_asignaciones)
        col2.metric("Empleados asignados", total_empleados)
        col3.metric(
            "Restaurantes asociados",
            total_restaurantes_asociados
        )

        asignaciones_cargo = (
            df_asignaciones.groupby("Cargo")
            .size()
            .reset_index(name="Cantidad")
        )

        st.subheader("Asignaciones por cargo")

        grafico_cargos = px.bar(
            asignaciones_cargo,
            x="Cargo",
            y="Cantidad",
            title="Cantidad de empleados por cargo",
            text="Cantidad"
        )

        st.plotly_chart(
            grafico_cargos,
            use_container_width=True
        )

        asignaciones_restaurante = (
            df_asignaciones.groupby("Restaurante")
            .size()
            .reset_index(name="Cantidad")
        )

        st.subheader("Distribución de asignaciones por restaurante")

        grafico_restaurantes = px.pie(
            asignaciones_restaurante,
            names="Restaurante",
            values="Cantidad",
            title="Porcentaje de asignaciones por restaurante"
        )

        st.plotly_chart(
            grafico_restaurantes,
            use_container_width=True
        )

    else:
        st.info("Todavía no hay asignaciones registradas.")

        col1, col2, col3 = st.columns(3)

        col1.metric("Total de asignaciones", 0)
        col2.metric("Empleados asignados", 0)
        col3.metric("Restaurantes asociados", 0)

except Exception as error:
    st.error(f"Error al cargar el panel de asignaciones: {error}")


# Pestañas de asignaciones.
(
    tab_asig_alta,
    tab_asig_buscar,
    tab_asig_modificar,
    tab_asig_eliminar
) = st.tabs(
    [
        "Alta asignación",
        "Buscar asignación",
        "Modificar asignación",
        "Eliminar asignación"
    ]
)


# ==================================================
# ALTA DE ASIGNACIONES
# ==================================================

with tab_asig_alta:
    st.subheader("Registrar asignación")

    with st.form("form_alta_asignacion"):
        id_cargo = st.number_input(
            "ID del cargo",
            min_value=1,
            step=1,
            key="alta_id_cargo"
        )

        id_condicion = st.number_input(
            "ID de la condición",
            min_value=1,
            step=1,
            key="alta_id_condicion"
        )

        cuit_restaurante = st.text_input(
            "CUIT del restaurante",
            key="alta_cuit_restaurante"
        )

        dni_empleado = st.number_input(
            "DNI del empleado",
            min_value=1,
            step=1,
            key="alta_dni_empleado"
        )

        enviar_asignacion = st.form_submit_button(
            "Registrar asignación"
        )

        if enviar_asignacion:
            if not validar_cuit(cuit_restaurante):
                st.error("El CUIT debe contener 11 números.")

            else:
                try:
                    with SessionLocal() as db:
                        resultado = crear_asignacion(
                            db,
                            int(id_cargo),
                            int(id_condicion),
                            int(cuit_restaurante),
                            int(dni_empleado)
                        )

                    if resultado is not None:
                        st.success("Asignación registrada correctamente.")
                    else:
                        st.error(
                            "No se pudo registrar la asignación. "
                            "Verificá que los datos relacionados existan "
                            "y que no esté duplicada."
                        )

                except Exception as error:
                    st.error(f"No se pudo registrar: {error}")


# ==================================================
# BUSCAR ASIGNACIONES
# ==================================================

with tab_asig_buscar:
    st.subheader("Asignaciones registradas")

    if st.button("Mostrar todas las asignaciones"):
        try:
            with SessionLocal() as db:
                asignaciones = listar_asignaciones(db)

                if asignaciones:
                    datos = [
                        {
                            "ID Cargo": a.id_cargo,
                            "ID Condición": a.id_condicion,
                            "CUIT Restaurante": a.cuit_restaurante,
                            "DNI Empleado": a.dni_empleado
                        }
                        for a in asignaciones
                    ]

                    st.dataframe(datos, use_container_width=True)

                else:
                    st.info("No hay asignaciones registradas.")

        except Exception as error:
            st.error(
                f"No se pudieron consultar las asignaciones: {error}"
            )

    st.divider()

    st.subheader("Buscar una asignación específica")

    with st.form("form_buscar_asignacion"):
        buscar_cargo = st.number_input(
            "ID del cargo",
            min_value=1,
            step=1,
            key="buscar_cargo"
        )

        buscar_condicion = st.number_input(
            "ID de la condición",
            min_value=1,
            step=1,
            key="buscar_condicion"
        )

        buscar_cuit = st.text_input(
            "CUIT del restaurante",
            key="buscar_cuit"
        )

        buscar_dni = st.number_input(
            "DNI del empleado",
            min_value=1,
            step=1,
            key="buscar_dni"
        )

        enviar_busqueda = st.form_submit_button("Buscar asignación")

        if enviar_busqueda:
            if not validar_cuit(buscar_cuit):
                st.error("Ingresá un CUIT válido de 11 números.")

            else:
                try:
                    with SessionLocal() as db:
                        resultado = buscar_asignacion(
                            db,
                            int(buscar_cargo),
                            int(buscar_condicion),
                            int(buscar_cuit),
                            int(buscar_dni)
                        )

                    if resultado is not None:
                        st.success("Asignación encontrada.")

                        st.write({
                            "ID Cargo": resultado.id_cargo,
                            "ID Condición": resultado.id_condicion,
                            "CUIT Restaurante": resultado.cuit_restaurante,
                            "DNI Empleado": resultado.dni_empleado
                        })

                    else:
                        st.warning("No se encontró esa asignación.")

                except Exception as error:
                    st.error(f"No se pudo realizar la búsqueda: {error}")


# ==================================================
# MODIFICAR ASIGNACIONES
# ==================================================

with tab_asig_modificar:
    st.subheader("Modificar asignación")

    with st.form("form_modificar_asignacion"):
        st.write("Datos actuales de la asignación")

        cargo_original = st.number_input(
            "ID del cargo actual",
            min_value=1,
            step=1,
            key="cargo_original"
        )

        condicion_original = st.number_input(
            "ID de la condición actual",
            min_value=1,
            step=1,
            key="condicion_original"
        )

        cuit_original = st.text_input(
            "CUIT actual del restaurante",
            key="cuit_original"
        )

        dni_original = st.number_input(
            "DNI actual del empleado",
            min_value=1,
            step=1,
            key="dni_original"
        )

        st.divider()

        st.write("Nuevos datos de la asignación")

        nuevo_cargo = st.number_input(
            "Nuevo ID del cargo",
            min_value=1,
            step=1,
            key="nuevo_cargo"
        )

        nueva_condicion = st.number_input(
            "Nuevo ID de la condición",
            min_value=1,
            step=1,
            key="nueva_condicion"
        )

        nuevo_cuit = st.text_input(
            "Nuevo CUIT del restaurante",
            key="nuevo_cuit"
        )

        nuevo_dni = st.number_input(
            "Nuevo DNI del empleado",
            min_value=1,
            step=1,
            key="nuevo_dni"
        )

        enviar_modificacion_asignacion = st.form_submit_button(
            "Guardar cambios"
        )

        if enviar_modificacion_asignacion:
            if (
                not validar_cuit(cuit_original)
                or not validar_cuit(nuevo_cuit)
            ):
                st.error("Los CUIT deben contener 11 números.")

            else:
                try:
                    with SessionLocal() as db:
                        resultado = modificar_asignacion(
                            db,
                            int(cargo_original),
                            int(condicion_original),
                            int(cuit_original),
                            int(dni_original),
                            int(nuevo_cargo),
                            int(nueva_condicion),
                            int(nuevo_cuit),
                            int(nuevo_dni)
                        )

                    if resultado is None:
                        st.warning(
                            "No se encontró la asignación original "
                            "o no se pudieron guardar los cambios."
                        )
                    else:
                        st.success("Asignación modificada correctamente.")

                except Exception as error:
                    st.error(f"No se pudo modificar: {error}")


# ==================================================
# ELIMINAR ASIGNACIONES
# ==================================================

with tab_asig_eliminar:
    st.subheader("Eliminar asignación")

    with st.form("form_eliminar_asignacion"):
        cargo_eliminar = st.number_input(
            "ID del cargo",
            min_value=1,
            step=1,
            key="cargo_eliminar"
        )

        condicion_eliminar = st.number_input(
            "ID de la condición",
            min_value=1,
            step=1,
            key="condicion_eliminar"
        )

        cuit_eliminar_asignacion = st.text_input(
            "CUIT del restaurante",
            key="cuit_eliminar_asignacion"
        )

        dni_eliminar = st.number_input(
            "DNI del empleado",
            min_value=1,
            step=1,
            key="dni_eliminar"
        )

        enviar_eliminacion_asignacion = st.form_submit_button(
            "Eliminar asignación"
        )

        if enviar_eliminacion_asignacion:

            # Mostramos los valores que recibe el formulario.
            st.write(
                "Datos enviados:",
                int(cargo_eliminar),
                int(condicion_eliminar),
                cuit_eliminar_asignacion,
                int(dni_eliminar)
            )

            if not validar_cuit(cuit_eliminar_asignacion):
                st.error("El CUIT debe contener 11 números.")

            else:
                try:
                    with SessionLocal() as db:
                        resultado = eliminar_asignacion(
                            db,
                            int(cargo_eliminar),
                            int(condicion_eliminar),
                            int(cuit_eliminar_asignacion),
                            int(dni_eliminar)
                        )

                    if resultado:
                        st.success("Asignación eliminada correctamente.")
                    else:
                        st.warning("No se encontró esa asignación.")

                except Exception as error:
                    st.error(f"No se pudo eliminar: {error}")
