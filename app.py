import os
from datetime import datetime, timedelta
import streamlit as st
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from src.database import make_session_factory
from src.models import Usuario, Restaurante, Rol, Empleado
from src.services.auth import authenticate, PERMISSIONS
from src.services.admin import create_restaurant, create_user, update_user
from src.services.cargo import create_cargo, delete_cargo, list_cargos, update_cargo
from src.services.tipo_comprobante import (
    create_tipo_comprobante,
    delete_tipo_comprobante,
    list_tipos_comprobante,
    update_tipo_comprobante,
)

st.set_page_config(page_title="Gestión de Restaurante", page_icon="🍽️")

@st.cache_resource
def database():
    return make_session_factory()

factory = database()
st.title(os.getenv("APP_NAME", "Gestión de Restaurante"))


def logout():
    st.session_state.clear()
    st.rerun()


try:
    if "user_id" not in st.session_state:
        st.subheader("Iniciar sesión")
        with st.form("login"):
            email = st.text_input("Email")
            password = st.text_input("Contraseña", type="password")
            submitted = st.form_submit_button("Ingresar")
        if submitted:
            with factory.begin() as session:
                user_id = authenticate(session, email, password)
            if user_id:
                st.session_state.user_id = user_id
                st.session_state.last_activity = datetime.now()
                st.rerun()
            else:
                st.error("Email o contraseña incorrectos, o cuenta inactiva.")
        st.stop()

    now = datetime.now()
    if now - st.session_state.get("last_activity", now) > timedelta(minutes=int(os.getenv("SESSION_TIMEOUT_MINUTES", "120"))):
        logout()
    st.session_state.last_activity = now
    with factory() as session:
        user = session.get(Usuario, st.session_state.user_id)
        if not user or not user.activo:
            logout()
        role = user.rol.nombre_rol
        st.sidebar.write(f"{user.nombre_completo} · {role}")
    if st.sidebar.button("Cerrar sesión"):
        logout()
    if role != "ADMIN":
        st.success("Sesión iniciada.")
        st.write("Permisos del rol: " + ", ".join(sorted(PERMISSIONS.get(role, set()))))
        st.info("Los módulos operativos todavía no están implementados.")
        st.stop()

    section = st.sidebar.radio(
        "Administración",
        ["Restaurantes", "Usuarios", "Cargos", "Tipos de comprobante"],
    )
    with factory() as session:
        restaurants = {r.cuit: r.nombre_fantasia for r in session.scalars(select(Restaurante))}
        roles = {r.id_rol: r.nombre_rol for r in session.scalars(select(Rol))}
        employees = {e.dni: f"{e.apellido_empleado}, {e.nombre_empleado}" for e in session.scalars(select(Empleado))}
    if section == "Restaurantes":
        st.subheader("Crear restaurante")
        with st.form("restaurant"):
            cuit = st.text_input("CUIT (11 dígitos)")
            razon = st.text_input("Razón social", max_chars=150)
            nombre = st.text_input("Nombre de fantasía", max_chars=150)
            direccion = st.text_input("Dirección", max_chars=180)
            ciudad = st.text_input("Ciudad", max_chars=100)
            save = st.form_submit_button("Crear restaurante")
        if save:
            with factory.begin() as session:
                create_restaurant(session, st.session_state.user_id, int(cuit), razon, nombre, direccion, ciudad)
            st.success("Restaurante creado. Disponible en la sección Usuarios.")
        st.write([{"CUIT": key, "Nombre": value} for key, value in restaurants.items()])
    elif section == "Usuarios":
        st.subheader("Crear usuario")
        if not roles:
            st.warning("Ejecutá primero python -m scripts.bootstrap para cargar los roles y el administrador.")
            st.stop()
        def assignment_fields(prefix, defaults=None):
            defaults = defaults or (next(iter(roles)), None, None)
            role_ids = list(roles)
            restaurant_ids = [None] + list(restaurants)
            employee_ids = [None] + list(employees)
            role_id = st.selectbox("Rol", role_ids, index=role_ids.index(defaults[0]), format_func=roles.get, key=prefix+"role")
            restaurant_id = st.selectbox("Restaurante", restaurant_ids, index=restaurant_ids.index(defaults[1]), format_func=lambda x: restaurants.get(x, "Sin restaurante"), key=prefix+"restaurant")
            employee_id = st.selectbox("Empleado existente", employee_ids, index=employee_ids.index(defaults[2]), format_func=lambda x: employees.get(x, "Sin empleado"), key=prefix+"employee")
            return role_id, restaurant_id, employee_id
        with st.form("create_user"):
            email = st.text_input("Email", max_chars=80)
            name = st.text_input("Nombre completo", max_chars=150)
            password = st.text_input("Contraseña inicial", type="password")
            role_id, restaurant_id, employee_id = assignment_fields("new")
            save = st.form_submit_button("Crear usuario")
        if save:
            with factory.begin() as session:
                create_user(session, st.session_state.user_id, email, name, password, role_id, restaurant_id, employee_id)
            st.success("Usuario creado.")
        with factory() as session:
            users = list(session.scalars(select(Usuario)))
        selected = st.selectbox("Modificar usuario", users, format_func=lambda u: u.nombre_usuario)
        if selected:
            with st.form(f"edit_{selected.id_usuario}"):
                role_id, restaurant_id, employee_id = assignment_fields(f"edit{selected.id_usuario}", (selected.id_rol, selected.cuit_restaurante, selected.dni_empleado))
                active = st.checkbox("Activo", value=selected.activo)
                save = st.form_submit_button("Guardar rol y vínculos")
            if save:
                with factory.begin() as session:
                    update_user(session, st.session_state.user_id, selected.id_usuario, role_id, restaurant_id, employee_id, active)
                st.success("Usuario actualizado.")
                st.rerun()
    elif section == "Cargos":
        st.subheader("Administrar cargos")
        with st.form("create_cargo"):
            cargo_name = st.text_input("Nombre del cargo", max_chars=100)
            create = st.form_submit_button("Registrar cargo")
        if create:
            with factory.begin() as session:
                create_cargo(session, st.session_state.user_id, cargo_name)
            st.success("Cargo registrado.")
            st.rerun()

        with factory() as session:
            cargos = list_cargos(session, st.session_state.user_id)
        st.subheader("Cargos registrados")
        if not cargos:
            st.info("Todavía no hay cargos registrados.")
        else:
            st.dataframe(
                [{"ID": cargo.id_cargo, "Cargo": cargo.nombre_cargo} for cargo in cargos],
                hide_index=True,
                use_container_width=True,
            )
            selected_id = st.selectbox(
                "Seleccionar cargo", [cargo.id_cargo for cargo in cargos],
                format_func=lambda cargo_id: next(
                    cargo.nombre_cargo for cargo in cargos if cargo.id_cargo == cargo_id
                ),
            )
            selected = next(cargo for cargo in cargos if cargo.id_cargo == selected_id)
            with st.form(f"edit_cargo_{selected_id}"):
                edited_name = st.text_input(
                    "Modificar nombre", value=selected.nombre_cargo, max_chars=100
                )
                update = st.form_submit_button("Guardar cambios")
            if update:
                with factory.begin() as session:
                    update_cargo(session, st.session_state.user_id, selected_id, edited_name)
                st.success("Cargo actualizado.")
                st.rerun()
            if st.button("Eliminar cargo seleccionado", key=f"delete_cargo_{selected_id}"):
                with factory.begin() as session:
                    delete_cargo(session, st.session_state.user_id, selected_id)
                st.success("Cargo eliminado.")
                st.rerun()
    else:
        st.subheader("Administrar tipos de comprobante")
        with st.form("create_tipo_comprobante"):
            tipo_name = st.text_input("Nombre del tipo de comprobante", max_chars=100)
            create = st.form_submit_button("Registrar tipo")
        if create:
            with factory.begin() as session:
                create_tipo_comprobante(session, st.session_state.user_id, tipo_name)
            st.success("Tipo de comprobante registrado.")
            st.rerun()

        with factory() as session:
            tipos = list_tipos_comprobante(session, st.session_state.user_id)
        st.subheader("Tipos registrados")
        if not tipos:
            st.info("Todavía no hay tipos de comprobante registrados.")
        else:
            st.dataframe(
                [{"ID": tipo.id_tipo_comprobante,
                  "Tipo de comprobante": tipo.nombre_tipo_comprobante} for tipo in tipos],
                hide_index=True,
                use_container_width=True,
            )
            selected_id = st.selectbox(
                "Seleccionar tipo", [tipo.id_tipo_comprobante for tipo in tipos],
                format_func=lambda tipo_id: next(
                    tipo.nombre_tipo_comprobante for tipo in tipos
                    if tipo.id_tipo_comprobante == tipo_id
                ),
            )
            selected = next(tipo for tipo in tipos if tipo.id_tipo_comprobante == selected_id)
            with st.form(f"edit_tipo_comprobante_{selected_id}"):
                edited_name = st.text_input(
                    "Modificar nombre", value=selected.nombre_tipo_comprobante, max_chars=100
                )
                update = st.form_submit_button("Guardar cambios")
            if update:
                with factory.begin() as session:
                    update_tipo_comprobante(
                        session, st.session_state.user_id, selected_id, edited_name
                    )
                st.success("Tipo de comprobante actualizado.")
                st.rerun()
            if st.button(
                "Eliminar tipo seleccionado", key=f"delete_tipo_comprobante_{selected_id}"
            ):
                with factory.begin() as session:
                    delete_tipo_comprobante(session, st.session_state.user_id, selected_id)
                st.success("Tipo de comprobante eliminado.")
                st.rerun()
except (ValueError, PermissionError) as exc:
    st.error(str(exc))
except SQLAlchemyError:
    st.error("No se pudo completar la operación. Revisá la conexión, el esquema y posibles registros duplicados.")
