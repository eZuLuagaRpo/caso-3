function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();

            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

let chart, smaChartInstance, diffChartInstance, emaChartInstance;

async function obtenerDatos() {
    const from = document.getElementById('from').value;
    const to = document.getElementById('to').value;
    const brand = document.getElementById('brand').value;

    const csrftoken = getCookie('csrftoken');

    const response = await fetch("/getReturns", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrftoken
        },
        body: new URLSearchParams({
            'from': from,
            'to': to,
            'brand': brand
        })
    });

    if (response.ok) {
        const data = await response.json();
        graficarDatos(data);
    } else {
        console.error('Error en la consulta:', response.statusText);
    }
}

function graficarDatos(data) {
    // Ocultar mensaje inicial y mostrar secciones de análisis
    document.getElementById("beforeText").style.display = "none";
    document.getElementById("afterText").style.display = "block";
    document.getElementById("analysisIntro").style.display = "block";
    document.getElementById("analysisCharts").style.display = "block";
    document.getElementById("analysisResult").style.display = "block";
    document.getElementById("brandId").innerHTML = data.brand;

    // Crear los gráficos
    const labels = data.data.map(item => item.date);
    const closingPrices = data.data.map(item => item.close);
    const smaValues = data.data.map(item => item.sma_5);
    
    // Gráfico principal
    const ctx = document.getElementById('chart').getContext('2d');
    if (chart) {
        chart.destroy();
    }

    // Gráfico 1: Precio de cierre + SMA_5
    chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: `Precio de Cierre de ${data.brand}`,
                    data: closingPrices,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderWidth: 2,
                    fill: false,
                },
                {
                    label: `Media Móvil Simple (SMA_5) de ${data.brand}`,
                    data: smaValues,
                    borderColor: 'rgba(255, 99, 132, 1)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    borderWidth: 2,
                    fill: false,
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                x: { title: { display: true, text: 'Fecha' }},
                y: { beginAtZero: false, title: { display: true, text: 'Precio (USD)' }}
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function (tooltipItem) {
                            return `${tooltipItem.dataset.label}: $${tooltipItem.raw.toFixed(2)}`;
                        }
                    }
                }
            }
        }
    });

    // Crear los gráficos adicionales
    graficarSMAArea(data);
    graficarDiferencias(data);
    graficarSMAvsEMA(data);

    // Mostrar el análisis
    document.getElementById("analysisResultText").innerHTML = data.analysis;
}

function graficarSMAArea(data) {
    const labels = data.data.map(item => item.date);
    const smaValues = data.data.map(item => item.sma_5);
    const ctx = document.getElementById('smaChart').getContext('2d');
    if (smaChartInstance) smaChartInstance.destroy();
    smaChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: `Evolución de SMA_5 de ${data.brand}`,
                data: smaValues,
                backgroundColor: 'rgba(153, 102, 255, 0.4)',
                borderColor: 'rgba(153, 102, 255, 1)',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: { display: true, text: 'Área bajo la SMA_5' }
            },
            scales: {
                x: { title: { display: true, text: 'Fecha' }},
                y: { title: { display: true, text: 'Precio (USD)' }}
            }
        }
    });
}

function graficarDiferencias(data) {
    const labels = data.data.slice(1).map(item => item.date);
    const closingPrices = data.data.map(item => item.close);
    const changes = [];

    for (let i = 1; i < closingPrices.length; i++) {
        changes.push(closingPrices[i] - closingPrices[i - 1]);
    }

    const ctx = document.getElementById('diffChart').getContext('2d');
    if (diffChartInstance) diffChartInstance.destroy();
    diffChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: `Cambio Diario del Precio de ${data.brand}`,
                data: changes,
                backgroundColor: changes.map(change => change >= 0 ? 'rgba(75, 192, 192, 0.6)' : 'rgba(255, 99, 132, 0.6)'),
                borderColor: changes.map(change => change >= 0 ? 'rgba(75, 192, 192, 1)' : 'rgba(255, 99, 132, 1)'),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: { display: true, text: 'Variaciones Diarias del Precio de Cierre' }
            },
            scales: {
                x: { title: { display: true, text: 'Fecha' }},
                y: { title: { display: true, text: 'Cambio (USD)' }}
            }
        }
    });
}

function calcularEMA(data, window) {
    let k = 2 / (window + 1);
    let emaArray = [];
    let emaPrev = null;

    for (let i = 0; i < data.length; i++) {
        if (data[i] === null || isNaN(data[i])) {
            emaArray.push(null);
            continue;
        }

        if (emaPrev === null) {
            emaPrev = data[i];
        } else {
            emaPrev = data[i] * k + emaPrev * (1 - k);
        }
        emaArray.push(emaPrev);
    }
    return emaArray;
}

function graficarSMAvsEMA(data) {
    const labels = data.data.map(item => item.date);
    const sma = data.data.map(item => item.sma_5);
    const closePrices = data.data.map(item => item.close);
    const ema = calcularEMA(closePrices, 5);
    const ctx = document.getElementById('emaChart').getContext('2d');
    if (emaChartInstance) emaChartInstance.destroy();
    emaChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: `SMA_5 de ${data.brand}`,
                    data: sma,
                    borderColor: 'rgba(255, 159, 64, 1)',
                    fill: false,
                    tension: 0.3
                },
                {
                    label: `EMA_5 de ${data.brand}`,
                    data: ema,
                    borderColor: 'rgba(54, 162, 235, 1)',
                    fill: false,
                    tension: 0.3
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Comparación entre SMA_5 y EMA_5'
                }
            },
            scales: {
                x: { title: { display: true, text: 'Fecha' }},
                y: { title: { display: true, text: 'Precio (USD)' }}
            }
        }
    });
}
