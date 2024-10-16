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

let chart;

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
    document.getElementById("beforeText").style.display = "none"
    document.getElementById("afterText").style.display = "block"
    document.getElementById("analysisResult").style.display = "block"
    document.getElementById("brandId").innerHTML = data.brand
    const labels = data.data.map(item => item.date);
    const closingPrices = data.data.map(item => item.close);
    const smaValues = data.data.map(item => item.sma_5);
    const ctx = document.getElementById('chart').getContext('2d');

    if (chart) {
        chart.destroy();
    }

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
                x: {
                    title: {
                        display: true,
                        text: 'Fecha'
                    }
                },
                y: {
                    beginAtZero: false,
                    title: {
                        display: true,
                        text: 'Precio (USD)'
                    }
                }
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

    document.getElementById("analysisResultText").innerHTML = data.analysis
}