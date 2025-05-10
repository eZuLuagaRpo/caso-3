from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

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



import yfinance as yf
from datetime import datetime
import pandas as pd

from datetime import datetime
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import yfinance as yf
import pandas as pd

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

        analysis = analyze_data(sma_5)

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

import numpy as np

def analyze_data(prices):
    clean_prices = [p for p in prices if p is not None]
    
    if len(clean_prices) < 10:
        return "No hay suficientes datos para realizar un análisis fiable."

    trend = np.polyfit(range(len(clean_prices)), clean_prices, 1)[0]
    recent_movement = clean_prices[-1] - clean_prices[-5] if len(clean_prices) >= 5 else 0
    volatility = np.std(clean_prices[-20:]) if len(clean_prices) >= 20 else np.std(clean_prices)

    recommendation = "mantener"
    if trend > 0 and recent_movement > 0 and volatility < 5:
        recommendation = "comprar"
    elif trend < 0 and recent_movement < 0:
        recommendation = "vender"

    summary = (
        f"Se ha realizado un análisis sobre los precios de cierre (media móvil simple de 5 días) para la empresa seleccionada. "
        f"En el período analizado, se observa una {'tendencia positiva' if trend > 0 else 'tendencia negativa'}, "
        f"con un cambio reciente de aproximadamente {recent_movement:.2f} USD en los últimos días. "
        f"La volatilidad de los precios es de {volatility:.2f}, lo cual indica un {'nivel bajo' if volatility < 5 else 'nivel alto'} de incertidumbre en el mercado.\n\n"
        f"Basándonos en este análisis cuantitativo, la recomendación actual es {recommendation.upper()}. "
        f"Esto se debe a la {'estabilidad' if volatility < 5 else 'inestabilidad'} de los precios y la dirección general de la tendencia. "
        f"Se recomienda al inversionista realizar un seguimiento continuo de los precios y ajustar su estrategia si se presentan cambios significativos en la volatilidad o en la dirección del mercado."
    )

    return summary