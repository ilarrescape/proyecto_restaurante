import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from src.models import Base, Usuario, Rol, Restaurante
from src.services.auth import hash_password, verify_password, authenticate, has_permission
from src.services.admin import create_restaurant, create_user, update_user


@pytest.fixture
def session():
    engine = create_engine('sqlite://')
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        db.add_all([Rol(id_rol=1, nombre_rol='ADMIN'), Rol(id_rol=2, nombre_rol='MOZO')])
        db.add(Usuario(id_usuario=1, nombre_usuario='admin@example.com', nombre_completo='Admin',
                       password_hash=hash_password('secreto'), id_rol=1))
        db.commit()
        yield db


def test_bcrypt():
    hashed = hash_password('contraseña')
    assert hashed != 'contraseña'
    assert verify_password('contraseña', hashed)
    assert not verify_password('otra', hashed)
    assert not verify_password('x', 'hash inválido')
    with pytest.raises(ValueError):
        hash_password('á' * 37)


def test_login_and_disabled_account(session):
    assert authenticate(session, ' ADMIN@example.com ', 'secreto') == 1
    assert session.get(Usuario, 1).ultimo_acceso is not None
    assert authenticate(session, 'admin@example.com', 'incorrecta') is None
    assert authenticate(session, 'ausente@example.com', 'secreto') is None
    session.get(Usuario, 1).activo = False
    assert authenticate(session, 'admin@example.com', 'secreto') is None


def test_admin_creates_restaurant_and_user(session):
    restaurant = create_restaurant(session, 1, 30123456789, 'Empresa', 'Local', 'Calle 1', 'Rosario')
    user = create_user(session, 1, 'mozo@example.com', 'Mozo', 'clave', 2, restaurant.cuit)
    assert verify_password('clave', user.password_hash)
    assert has_permission(session, user.id_usuario, 'pedidos')
    assert not has_permission(session, user.id_usuario, 'usuarios')
    with pytest.raises(PermissionError):
        create_restaurant(session, user.id_usuario, 30123456780, 'Otra', 'Otro', 'Calle 2', 'Rosario')
    with pytest.raises(PermissionError):
        update_user(session, user.id_usuario, user.id_usuario, 1, restaurant.cuit, None, True)
    with pytest.raises(ValueError):
        create_user(session, 1, 'MOZO@example.com', 'Duplicado', 'clave', 2, restaurant.cuit)
    with pytest.raises(ValueError):
        update_user(session, 1, 1, 2, restaurant.cuit, None, True)
    update_user(session, 1, user.id_usuario, 1, restaurant.cuit, None, True)
    session.expire(user, ['rol'])
    assert has_permission(session, user.id_usuario, 'usuarios')


def test_bootstrap_seeds_and_preserves_existing_admin(monkeypatch):
    from sqlalchemy import event
    from sqlalchemy.orm import sessionmaker
    from src.services.bootstrap import bootstrap
    engine = create_engine('sqlite://')
    Base.metadata.create_all(engine)

    @event.listens_for(engine, 'before_cursor_execute', retval=True)
    def adapt_mysql_sql(connection, cursor, statement, parameters, context, many):
        # SQLite verifica los datos; el bloqueo MySQL requiere prueba de integración propia.
        if 'GET_LOCK(' in statement or 'RELEASE_LOCK(' in statement:
            return 'SELECT 1', ()
        return statement.replace('INSERT IGNORE', 'INSERT OR IGNORE'), parameters

    monkeypatch.setenv('EMAIL_SUPER', 'SUPER@example.com')
    monkeypatch.setenv('PASSWORD_SUPER', 'inicial')
    factory = sessionmaker(engine)
    assert bootstrap(factory)
    with factory() as db:
        user = db.scalar(select(Usuario))
        original_hash = user.password_hash
        assert user.rol.nombre_rol == 'ADMIN'
        assert verify_password('inicial', original_hash)
    monkeypatch.setenv('PASSWORD_SUPER', 'cambiada')
    assert not bootstrap(factory)
    with factory() as db:
        assert len(list(db.scalars(select(Usuario)))) == 1
        assert len(list(db.scalars(select(Rol)))) == 5
        assert db.scalar(select(Usuario)).password_hash == original_hash
