from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from datetime import datetime
import yfinance as yf
import pandas as pd
import numpy as np
import pandas as pd
import markdown

def user_login(request):
    if request.method == "POST":
        
        username = request.POST["username"]
        password = request.POST["password"]

        if not(username) or not(password):
            return render(request, 'login.html', {"err_msg":"Username and password required"})

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("/")
        else:
            return render(request, 'login.html', {"err_msg":"Username and/or password incorrect."})
    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return redirect("/login")

@login_required(login_url='/login')
def home(request):
    return render(request, 'index.html')

@login_required(login_url='/login')
def getReturns(request):
    if request.method == 'POST':

        from_date = request.POST.get('from')
        to_date = request.POST.get('to')
        brand = request.POST.get('brand')

        start = datetime.strptime(from_date, '%Y-%m-%d')
        end = datetime.strptime(to_date, '%Y-%m-%d')

        # Crear el objeto Ticker y usar .history()
        ticker = yf.Ticker(brand)
        stock_data = ticker.history(start=start, end=end)

        if stock_data.empty:
            return JsonResponse({'error': 'No se encontraron datos para el ticker y rango de fechas dados.'}, status=404)

        closing_prices = stock_data['Close'].to_list()
        dates = stock_data.index.strftime('%Y-%m-%d').to_list()

        stock_data['SMA_5'] = stock_data['Close'].rolling(window=5).mean()
        sma_5 = stock_data['SMA_5'].to_list()

        analysis = analyze_data(sma_5, dates, closing_prices)

        data = {
            'brand': brand,
            'data': [
                {
                    'date': date,
                    'close': price,
                    'sma_5': sma if not pd.isna(sma) else None
                } 
                for date, price, sma in zip(dates, closing_prices, sma_5)
            ],
            'analysis': analysis
        }


        return JsonResponse(data)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

def analyze_data(prices, dates, close_prices):
    """
    Realiza un análisis predictivo exhaustivo de los precios de cierre históricos para recomendar comprar, vender o mantener una acción.

    Parámetros:
    - prices: Lista de medias móviles simples (SMA_5).
    - dates: Lista de fechas correspondientes a los precios.
    - close_prices: Lista de precios de cierre diarios.

    Retorna:
    - Un informe detallado en formato de string con el análisis y la recomendación.
    """
    # Limpiar datos: eliminar None y convertir a arrays
    valid_data = [(d, c, s) for d, c, s in zip(dates, close_prices, prices) if c is not None and s is not None]
    if len(valid_data) < 20:
        return "No hay suficientes datos para realizar un análisis fiable. Se requieren al menos 20 días de datos."

    dates, close_prices, sma_5 = zip(*valid_data)
    close_prices = np.array(close_prices)
    sma_5 = np.array(sma_5)
    dates = pd.to_datetime(dates)

    # 1. Análisis de Tendencia
    # Tendencia a largo plazo (mínimo 60 días o todo el período)
    long_term_window = min(60, len(close_prices))
    long_term_trend = np.polyfit(range(long_term_window), close_prices[-long_term_window:], 1)[0]

    # Tendencia a corto plazo (últimos 10 días)
    short_term_trend = np.polyfit(range(10), close_prices[-10:], 1)[0] if len(close_prices) >= 10 else 0

    # 2. Indicadores Técnicos
    # Media Móvil Exponencial (EMA_5)
    ema_5 = pd.Series(close_prices).ewm(span=5, adjust=False).mean().tolist()

    # Índice de Fuerza Relativa (RSI, 14 días)
    def calculate_rsi(data, window=14):
        delta = np.diff(data)
        gain = np.where(delta > 0, delta, 0)
        loss = np.where(delta < 0, -delta, 0)
        avg_gain = np.mean(gain[-window:]) if len(gain) >= window else np.mean(gain)
        avg_loss = np.mean(loss[-window:]) if len(loss) >= window else np.mean(loss)
        rs = avg_gain / avg_loss if avg_loss != 0 else np.inf
        rsi = 100 - (100 / (1 + rs)) if rs != np.inf else 100
        return rsi

    rsi = calculate_rsi(close_prices) if len(close_prices) >= 14 else np.nan

    # 3. Volatilidad
    volatility = np.std(close_prices[-20:]) if len(close_prices) >= 20 else np.std(close_prices)

    # 4. Recomendación Predictiva
    recommendation = "mantener"
    if short_term_trend > 0 and sma_5[-1] > ema_5[-1] and rsi < 70:
        recommendation = "comprar"
    elif short_term_trend < 0 and sma_5[-1] < ema_5[-1] and rsi > 30:
        recommendation = "vender"

    # Generar el resumen en Markdown
    summary_md = (
        f"### Análisis Predictivo de Precios de Cierre\n"
        f"**Período Analizado**: {dates[0].strftime('%Y-%m-%d')} a {dates[-1].strftime('%Y-%m-%d')} ({len(dates)} días)\n\n"
        
        f"#### 1. Tendencia de Precios\n"
        f"- **Largo Plazo ({long_term_window} días)**: {'positiva' if long_term_trend > 0 else 'negativa'} (pendiente: {long_term_trend:.4f}).\n"
        f"- **Corto Plazo (10 días)**: {'positiva' if short_term_trend > 0 else 'negativa'} (pendiente: {short_term_trend:.4f}).\n\n"
        
        f"#### 2. Indicadores Técnicos\n"
        f"- **SMA_5**: {sma_5[-1]:.2f} USD (media móvil simple de 5 días).\n"
        f"- **EMA_5**: {ema_5[-1]:.2f} USD (media móvil exponencial de 5 días).\n"
        f"- **RSI (14 días)**: {rsi:.2f} ({'sobrecomprado' if rsi > 70 else 'sobrevendido' if rsi < 30 else 'neutral'}).\n\n"
        
        f"#### 3. Volatilidad\n"
        f"- **Desviación Estándar (20 días)**: {volatility:.2f} USD ({'baja' if volatility < 5 else 'alta'}).\n\n"
        
        f"#### 4. Recomendación\n"
        f"**{recommendation.upper()}**\n"
        f"Basado en un análisis predictivo del comportamiento histórico, se recomienda **{recommendation}** la acción. "
        f"Esto se fundamenta en la tendencia a corto plazo ({'alcista' if short_term_trend > 0 else 'bajista'}), "
        f"el cruce entre SMA_5 y EMA_5 ({'señal de compra' if sma_5[-1] > ema_5[-1] else 'señal de venta'}), "
        f"y el RSI que indica {'condiciones normales' if 30 <= rsi <= 70 else 'extremos a considerar'}. "
        f"La volatilidad actual sugiere un mercado {'estable' if volatility < 5 else 'inestable'}, "
        f"lo que refuerza la decisión. Se aconseja monitorear continuamente los indicadores para ajustar la estrategia ante cambios significativos."
    )

    # Convertir el Markdown a HTML
    summary_html = markdown.markdown(summary_md)

    return summary_html
    
