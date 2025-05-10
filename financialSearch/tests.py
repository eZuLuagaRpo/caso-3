from django.test import TestCase
import pytest
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User
from financialSearch.views import user_login, user_logout, home, getReturns, analyze_data
import pandas as pd
from datetime import datetime
from unittest.mock import patch, MagicMock
import allure

# --------------- Fixtures ---------------

@pytest.fixture
def client():
    """Simula un navegador web sin sesión activa."""
    return Client()

@pytest.fixture
def test_user(db):
    """
    Crea un usuario en la base de datos de prueba.
    El parámetro 'db' habilita un entorno transaccional que revierte los cambios al finalizar la prueba.
    """
    user = User.objects.create_user(username='testuser', password='testpass')
    return user

@pytest.fixture
def logged_in_client(client, test_user):
    """Simula un navegador con sesión activa autenticada."""
    client.login(username='testuser', password='testpass')
    return client

@pytest.fixture
def mock_yfinance(monkeypatch):
    """Mock para simular datos de yfinance y evitar llamadas reales a la API."""
    class MockTicker:
        def history(self, start, end):
            dates = pd.date_range(start=start, end=end, freq='D')
            data = pd.DataFrame({
                'Close': [100 + i for i in range(len(dates))],
                'SMA_5': [100 + i for i in range(len(dates))]
            }, index=dates)
            return data

    monkeypatch.setattr('yfinance.Ticker', lambda x: MockTicker())

# --------------- Pruebas Unitarias ---------------

# Feature: Autenticación
@allure.feature("Autenticación")
class TestAuthentication:
    
    @allure.story("Acceso a la Página de Login")
    @allure.title("GET /login devuelve 200 y renderice login.html")
    @allure.description("Verifica que una solicitud GET a la URL /login devuelva un código de estado 200 y renderice correctamente la plantilla login.html.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.django_db
    def test_user_login_get(self, client):
        response = client.get('/login')
        assert response.status_code == 200
        assert 'login.html' in [t.name for t in response.templates] 

    @allure.story("Login Exitoso")
    @allure.title("POST /login con credenciales válidas redirige a /")
    @allure.description("Prueba que un usuario con credenciales correctas pueda iniciar sesión y sea redirigido a la página principal (/) con un código de estado 302.")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.django_db
    def test_user_login_post_success(self, client, test_user):
        response = client.post('/login', {'username': 'testuser', 'password': 'testpass'})
        assert response.status_code == 302
        assert response.url == '/'

    @allure.story("Login Fallido")
    @allure.title("POST /login con credenciales inválidas muestra mensaje de error")
    @allure.description("Comprueba que al intentar iniciar sesión con credenciales incorrectas, la respuesta sea un código 200 y se muestre un mensaje de error indicando que el usuario o contraseña son incorrectos.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.django_db
    def test_user_login_post_invalid_credentials(self, client, test_user):
        response = client.post('/login', {'username': 'wronguser', 'password': 'wrongpass'})
        assert response.status_code == 200
        assert 'Username and/or password incorrect.' in response.content.decode()

    @allure.story("Login con Campos Vacíos")
    @allure.title("POST /login con campos vacíos muestra mensaje de error")
    @allure.description("Asegura que al enviar una solicitud POST a /login con campos de usuario y contraseña vacíos, se devuelva un código 200 y un mensaje indicando que ambos campos son requeridos.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.django_db
    def test_user_login_post_missing_fields(self, client):
        response = client.post('/login', {'username': '', 'password': ''})
        assert response.status_code == 200
        assert 'Username and password required' in response.content.decode()

    @allure.story("Logout")
    @allure.title("GET /logout cierra la sesión y redirige a /login")
    @allure.description("Valida que una solicitud GET a /logout cierre la sesión del usuario autenticado, redirija a /login con un código 302 y evite el acceso a rutas protegidas.")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.django_db
    def test_user_logout(self, logged_in_client):
        response = logged_in_client.get('/logout')
        assert response.status_code == 302
        assert response.url == '/login'
        # Verifica que la sesión se haya cerrado
        response = logged_in_client.get('/')
        assert response.status_code == 302
        assert '/login' in response.url

# Feature: Acceso a la Página Principal
@allure.feature("Acceso a la Página Principal")
class TestHomePage:
    
    @allure.story("Acceso Autenticado")
    @allure.title("GET / devuelve 200 para usuarios autenticados")
    @allure.description("Confirma que un usuario autenticado pueda acceder a la página principal (/) con un código de estado 200, renderizando index.html y mostrando el contenido esperado.")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.django_db
    def test_home_authenticated(self, logged_in_client):
        response = logged_in_client.get('/')
        assert response.status_code == 200
        assert 'index.html' in [t.name for t in response.templates]
        assert b'Consulta de Datos de Yahoo Finance' in response.content

# Feature: Obtención de Datos Financieros
@allure.feature("Obtención de Datos Financieros")
class TestGetReturns:
    
    @allure.story("Obtener Datos con POST")
    @allure.title("POST /getReturns con datos válidos devuelve 200 y datos correctos")
    @allure.description("Prueba que una solicitud POST a /getReturns con fechas y ticker válidos devuelva un código 200 y un JSON con la marca, datos financieros y análisis esperados.")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.django_db
    def test_get_returns_post_success(self, logged_in_client, mock_yfinance):
        data = {'from': '2023-01-01', 'to': '2023-01-05', 'brand': 'AAPL'}
        response = logged_in_client.post('/getReturns', data)
        assert response.status_code == 200
        json_data = response.json()
        assert 'brand' in json_data and json_data['brand'] == 'AAPL'
        assert 'data' in json_data and len(json_data['data']) > 0
        assert 'analysis' in json_data and json_data['analysis'] == "Implemente su análisis acá."

    @allure.story("Método No Permitido")
    @allure.title("GET /getReturns devuelve 405 Método no permitido")
    @allure.description("Verifica que una solicitud GET a /getReturns sea rechazada con un código 405 y un mensaje de error indicando que el método no está permitido.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.django_db
    def test_get_returns_get_method_not_allowed(self, logged_in_client):
        response = logged_in_client.get('/getReturns')
        assert response.status_code == 405
        assert response.json()['error'] == 'Método no permitido'

# --------------- Pruebas de Integración ---------------

@allure.feature("Flujo Completo de la Aplicación")
class TestIntegration:
    
    @allure.story("Login -> Obtener Datos -> Logout")
    @allure.title("Verifica el flujo completo: login, obtener datos y logout")
    @allure.description("Evalúa el flujo completo de la aplicación: un usuario inicia sesión, accede a datos financieros y cierra sesión, asegurando que cada paso funcione correctamente y que las rutas protegidas estén restringidas tras el logout.")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.django_db
    def test_integration_login_get_returns_logout(self, logged_in_client, mock_yfinance):
        # 1. Verifica que estamos logueados
        response = logged_in_client.get('/')
        assert response.status_code == 200
        
        # 2. Obtiene datos
        data = {'from': '2023-01-01', 'to': '2023-01-05', 'brand': 'AAPL'}
        response = logged_in_client.post('/getReturns', data)
        assert response.status_code == 200
        json_data = response.json()
        assert 'data' in json_data
        
        # 3. Logout
        response = logged_in_client.get('/logout')
        assert response.status_code == 302
        assert response.url == '/login'
        
        # 4. Verifica que no se puede acceder a datos sin login
        response = logged_in_client.post('/getReturns', data)
        assert response.status_code == 302
        assert '/login' in response.url

    @allure.story("Procesamiento de Datos")
    @allure.title("Verifica la estructura de los datos devueltos por /getReturns")
    @allure.description("Comprueba que los datos financieros devueltos por /getReturns tengan la estructura esperada (fecha, cierre, SMA) y que los tipos de datos sean correctos.")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.django_db
    def test_integration_data_processing(self, logged_in_client, mock_yfinance):
        data = {'from': '2023-01-01', 'to': '2023-01-10', 'brand': 'AAPL'}
        response = logged_in_client.post('/getReturns', data)
        assert response.status_code == 200
        json_data = response.json()
        assert 'data' in json_data and len(json_data['data']) > 0
        for item in json_data['data']:
            assert 'date' in item and 'close' in item and 'sma_5' in item
            assert isinstance(item['close'], (int, float))
            assert isinstance(item['date'], str)

# --------------- Pruebas Paramétricas ---------------

@allure.feature("Obtención de Datos Financieros")
class TestGetReturnsParametric:
    
    @allure.story("Casos Varios de Obtención de Datos")
    @allure.title("Prueba paramétrica para /getReturns con diferentes entradas")
    @allure.description("Evalúa el comportamiento de /getReturns con múltiples combinaciones de entradas, incluyendo casos válidos, fechas invertidas, tickers inválidos, formatos incorrectos y campos faltantes.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize(
        "from_date,to_date,brand,expected_status,expected_error",
        [
            # Caso de éxito: Fechas válidas y ticker válido
            ('2023-01-01', '2023-01-05', 'AAPL', 200, None),
            # Fechas invertidas: from > to
            ('2023-01-05', '2023-01-01', 'AAPL', 404, 'No se encontraron datos para el ticker y rango de fechas dados.'),
            # Ticker inválido
            ('2023-01-01', '2023-01-05', 'INVALID', 404, 'No se encontraron datos para el ticker y rango de fechas dados.'),
            # Fecha inválida: Formato incorrecto
            ('invalid-date', '2023-01-05', 'AAPL', 400, 'Formato de fecha inválido.'),
            # Campos faltantes: Falta 'to'
            ('2023-01-01', '', 'AAPL', 400, 'Faltan campos requeridos.'),
            # Campos faltantes: Falta 'from'
            ('', '2023-01-05', 'AAPL', 400, 'Faltan campos requeridos.'),
            # Fechas iguales: Comprobar comportamiento con rango de un solo día
            ('2023-01-01', '2023-01-01', 'AAPL', 200, None),
            # Fechas en el futuro: No deberían devolver datos
            ('2025-01-01', '2025-01-05', 'AAPL', 404, 'No se encontraron datos para el ticker y rango de fechas dados.')
        ]
    )
    @pytest.mark.django_db
    def test_get_returns_parametric(self, logged_in_client, mock_yfinance, from_date, to_date, brand, expected_status, expected_error):
        data = {'from': from_date, 'to': to_date, 'brand': brand}
        response = logged_in_client.post('/getReturns', data)
        assert response.status_code == expected_status
        if expected_status != 200:
            json_data = response.json()
            assert 'error' in json_data
            if expected_error:
                assert json_data['error'] == expected_error
        else:
            json_data = response.json()
            assert 'brand' in json_data and 'data' in json_data and 'analysis' in json_data

# --------------- Pruebas para Demostrar Mejoras ---------------

@allure.feature("Mejoras en el Manejo de Errores")
class TestErrorHandlingImprovements:
    
    @allure.story("Tipos de Datos Inválidos")
    @allure.title("POST /getReturns con tipos de datos inválidos devuelve 400")
    @allure.description("Demuestra que enviar tipos de datos incorrectos (números y booleanos en lugar de strings) a /getReturns resulta en un código 400, resaltando la necesidad de validación en la vista.")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.django_db
    def test_get_returns_invalid_data_types(self, logged_in_client, mock_yfinance):
        data = {'from': 123, 'to': True, 'brand': 456}
        response = logged_in_client.post('/getReturns', data)
        assert response.status_code == 400

    @allure.story("DataFrames Vacíos")
    @allure.title("POST /getReturns con DataFrame vacío devuelve 404")
    @allure.description("Asegura que cuando yfinance devuelve un DataFrame vacío, la vista /getReturns responde con un código 404, indicando que no se encontraron datos.")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.django_db
    def test_get_returns_empty_dataframe(self, logged_in_client, monkeypatch):
        class MockEmptyTicker:
            def history(self, start, end):
                return pd.DataFrame()  # DataFrame vacío
        monkeypatch.setattr('yfinance.Ticker', lambda x: MockEmptyTicker())
        data = {'from': '2023-01-01', 'to': '2023-01-05', 'brand': 'AAPL'}
        response = logged_in_client.post('/getReturns', data)
        assert response.status_code == 404