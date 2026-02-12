/**
 * DecisionBoard — Configuration des graphiques Chart.js.
 *
 * 4 types de graphiques réutilisables :
 * - Line Chart (évolution temporelle avec gradient + trend line optionnelle)
 * - Bar Chart vertical (comparaison par mois, couleurs conditionnelles)
 * - Bar Chart horizontal (classement)
 * - Doughnut Chart (répartition / parts, texte central)
 *
 * + Plugin custom pour afficher un total au centre du doughnut.
 * + Tooltips enrichis avec formatage professionnel.
 * + Animations fluides.
 */

/* ==== PALETTE DE COULEURS ==== */
const COLORS = {
    primary: '#2563eb',
    primaryRgb: '37, 99, 235',
    primaryLight: 'rgba(37, 99, 235, 0.08)',
    success: '#16a34a',
    successRgb: '22, 163, 74',
    warning: '#d97706',
    warningRgb: '217, 119, 6',
    danger: '#dc2626',
    purple: '#7c3aed',
    teal: '#0d9488',
    pink: '#db2777',
    sky: '#0ea5e9',
    palette: ['#2563eb', '#7c3aed', '#0ea5e9', '#16a34a', '#d97706', '#0d9488', '#db2777', '#dc2626'],
    paletteSoft: [
        'rgba(37, 99, 235, 0.85)',
        'rgba(124, 58, 237, 0.85)',
        'rgba(14, 165, 233, 0.85)',
        'rgba(22, 163, 74, 0.85)',
        'rgba(217, 119, 6, 0.85)',
        'rgba(13, 148, 136, 0.85)',
        'rgba(219, 39, 119, 0.85)',
        'rgba(220, 38, 38, 0.85)',
    ],
};


/* ==== CONFIGURATION GLOBALE CHART.JS ==== */
Chart.defaults.font.family = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif";
Chart.defaults.font.size = 12;
Chart.defaults.color = '#64748b';
Chart.defaults.animation = {
    duration: 800,
    easing: 'easeOutQuart',
};


/* ==== PLUGIN : TEXTE CENTRAL DOUGHNUT ==== */
const centerTextPlugin = {
    id: 'centerText',
    afterDraw(chart) {
        if (chart.config.type !== 'doughnut' || !chart.config.options.plugins.centerText) return;
        const { ctx, chartArea: { width, height, top } } = chart;
        const text = chart.config.options.plugins.centerText;

        ctx.save();
        // Valeur
        ctx.font = "800 1.25rem 'Inter', sans-serif";
        ctx.fillStyle = '#1e293b';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(text.value || '', width / 2, top + height / 2 - 8);
        // Label
        ctx.font = "500 0.6875rem 'Inter', sans-serif";
        ctx.fillStyle = '#94a3b8';
        ctx.fillText(text.label || '', width / 2, top + height / 2 + 12);
        ctx.restore();
    }
};
Chart.register(centerTextPlugin);


/* ==== PLUGIN : LIGNE VERTICALE AU SURVOL (Crosshair) ==== */
const crosshairPlugin = {
    id: 'crosshair',
    afterDraw(chart) {
        if (chart.config.type !== 'line') return;
        var tooltip = chart.tooltip;
        if (!tooltip || !tooltip.opacity) return;

        var ctx = chart.ctx;
        var x = tooltip.caretX;
        var topY = chart.chartArea.top;
        var bottomY = chart.chartArea.bottom;

        ctx.save();
        ctx.beginPath();
        ctx.moveTo(x, topY);
        ctx.lineTo(x, bottomY);
        ctx.lineWidth = 1;
        ctx.strokeStyle = 'rgba(37, 99, 235, 0.3)';
        ctx.setLineDash([4, 4]);
        ctx.stroke();
        ctx.restore();
    }
};
Chart.register(crosshairPlugin);


/* ==== UTILITAIRE : FORMATER UN NOMBRE ==== */
function fmtNum(value, decimals) {
    decimals = decimals || 0;
    var parts = Math.abs(value).toFixed(decimals).split('.');
    parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
    var result = decimals > 0 ? parts.join('.') : parts[0];
    return value < 0 ? '-' + result : result;
}

/* ==== TOOLTIP HTML EXTERNE ==== */
/**
 * Crée un tooltip HTML positionné à côté du point survolé.
 * Plus fiable que le tooltip canvas et permet un style riche.
 */
function getOrCreateTooltipEl(chart) {
    var tooltipEl = chart.canvas.parentNode.querySelector('.chartjs-tooltip');
    if (!tooltipEl) {
        tooltipEl = document.createElement('div');
        tooltipEl.classList.add('chartjs-tooltip');
        tooltipEl.innerHTML = '<div class="chartjs-tooltip-inner"></div>';
        chart.canvas.parentNode.appendChild(tooltipEl);
    }
    return tooltipEl;
}

function externalTooltipHandler(context, buildContent) {
    var chart = context.chart;
    var tooltip = context.tooltip;
    var tooltipEl = getOrCreateTooltipEl(chart);

    // Cacher si pas actif
    if (tooltip.opacity === 0) {
        tooltipEl.style.opacity = '0';
        tooltipEl.style.pointerEvents = 'none';
        return;
    }

    // Construire le contenu HTML
    var inner = tooltipEl.querySelector('.chartjs-tooltip-inner');
    if (tooltip.body) {
        inner.innerHTML = buildContent(tooltip, chart);
    }

    // Position
    var position = chart.canvas.getBoundingClientRect();
    var caretX = tooltip.caretX;
    var caretY = tooltip.caretY;

    tooltipEl.style.opacity = '1';
    tooltipEl.style.pointerEvents = 'none';
    tooltipEl.style.left = caretX + 'px';
    tooltipEl.style.top = caretY + 'px';
}

/* ==== OPTIONS COMMUNES ==== */
function getBaseTooltipStyle(buildContent) {
    return {
        enabled: false,
        external: function(context) {
            externalTooltipHandler(context, buildContent);
        }
    };
}

function getTooltipConfig(suffix) {
    suffix = suffix || 'CHF';
    return getBaseTooltipStyle(function(tooltip) {
        var title = tooltip.title ? tooltip.title[0] : '';
        var lines = '';
        tooltip.body.forEach(function(bodyItem, i) {
            var colors = tooltip.labelColors[i];
            var colorBox = '<span class="tt-color" style="background:' + colors.backgroundColor + '"></span>';
            lines += '<div class="tt-row">' + colorBox + bodyItem.lines.join('') + '</div>';
        });
        return '<div class="tt-title">' + title + '</div>' + lines;
    });
}

var commonScaleOptions = {
    y: {
        beginAtZero: true,
        ticks: {
            callback: function(v) { return v.toLocaleString('fr-CH'); },
            font: { size: 11, weight: '500' },
            color: '#94a3b8',
        },
        grid: { color: 'rgba(226, 232, 240, 0.6)', drawBorder: false },
        border: { display: false },
    },
    x: {
        grid: { display: false },
        border: { display: false },
        ticks: { font: { size: 11, weight: '500' }, color: '#94a3b8' },
    },
};


/* ==== LINE CHART ==== */
function initLineChart(canvasId, labels, values, label) {
    var ctx = document.getElementById(canvasId);
    if (!ctx) return;

    // Créer un gradient pour le fill
    var context2d = ctx.getContext('2d');
    var gradient = context2d.createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, 'rgba(' + COLORS.primaryRgb + ', 0.15)');
    gradient.addColorStop(1, 'rgba(' + COLORS.primaryRgb + ', 0.01)');

    var datasets = [{
        label: label || 'Valeur',
        data: values,
        borderColor: COLORS.primary,
        backgroundColor: gradient,
        borderWidth: 2.5,
        fill: true,
        tension: 0.4,
        pointRadius: 4,
        pointHoverRadius: 8,
        pointBackgroundColor: COLORS.primary,
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2,
        pointHoverBackgroundColor: COLORS.primary,
        pointHoverBorderColor: '#ffffff',
        pointHoverBorderWidth: 3,
        pointHitRadius: 20,
    }];

    // Ligne de tendance si assez de points
    if (values.length >= 3) {
        var trend = calculateTrendLine(values);
        datasets.push({
            label: 'Tendance',
            data: trend,
            borderColor: 'rgba(' + COLORS.primaryRgb + ', 0.25)',
            borderWidth: 1.5,
            borderDash: [6, 4],
            fill: false,
            pointRadius: 0,
            pointHoverRadius: 0,
        });
    }

    // Tooltip HTML enrichi pour line chart
    var lineTooltip = getBaseTooltipStyle(function(tooltip, chart) {
        var title = tooltip.title ? tooltip.title[0] : '';
        var html = '<div class="tt-title">📅 ' + title + '</div>';

        // Trouver l'item du dataset principal (pas la tendance)
        var mainItem = null;
        for (var i = 0; i < tooltip.dataPoints.length; i++) {
            if (tooltip.dataPoints[i].datasetIndex === 0) {
                mainItem = tooltip.dataPoints[i];
                break;
            }
        }

        if (mainItem) {
            var val = mainItem.parsed.y;
            var color = mainItem.dataset.borderColor;
            html += '<div class="tt-row"><span class="tt-color" style="background:' + color + '"></span>CA HT : <strong>' + fmtNum(val) + ' CHF</strong></div>';

            // Variation vs mois précédent
            var idx = mainItem.dataIndex;
            var data = mainItem.dataset.data;
            if (idx > 0 && data[idx - 1] > 0) {
                var prev = data[idx - 1];
                var diff = val - prev;
                var pct = ((diff / prev) * 100).toFixed(1);
                var arrow = diff >= 0 ? '▲' : '▼';
                var sign = diff >= 0 ? '+' : '';
                var cls = diff >= 0 ? 'tt-up' : 'tt-down';
                html += '<div class="tt-variation ' + cls + '">' + arrow + ' ' + sign + pct + '% vs mois préc. (' + sign + fmtNum(diff) + ' CHF)</div>';
            }

            // Moyenne
            var total = data.reduce(function(a, b) { return a + b; }, 0);
            var avg = total / data.length;
            html += '<div class="tt-footer">Moy. mensuelle : ' + fmtNum(avg) + ' CHF</div>';
        }
        return html;
    });

    new Chart(ctx, {
        type: 'line',
        data: { labels: labels, datasets: datasets },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            interaction: { mode: 'index', intersect: false },
            hover: { mode: 'index', intersect: false },
            plugins: {
                legend: { display: false },
                tooltip: lineTooltip,
            },
            scales: commonScaleOptions,
        }
    });
}


/* ==== BAR CHART VERTICAL ==== */
function initBarChart(canvasId, labels, values, label) {
    var ctx = document.getElementById(canvasId);
    if (!ctx) return;

    // Couleurs conditionnelles : le plus haut en bleu, les autres proportionnellement
    var maxVal = Math.max.apply(null, values);
    var bgColors = values.map(function(v) {
        var ratio = v / maxVal;
        if (ratio >= 0.8) return 'rgba(' + COLORS.primaryRgb + ', 0.9)';
        if (ratio >= 0.5) return 'rgba(' + COLORS.primaryRgb + ', 0.65)';
        return 'rgba(' + COLORS.primaryRgb + ', 0.4)';
    });

    var hoverColors = values.map(function() {
        return COLORS.primary;
    });

    var totalBar = values.reduce(function(a, b) { return a + b; }, 0);

    var barTooltip = getBaseTooltipStyle(function(tooltip) {
        var item = tooltip.dataPoints[0];
        var val = item.parsed.y;
        var color = item.dataset.backgroundColor[item.dataIndex] || item.dataset.backgroundColor;
        var pct = ((val / totalBar) * 100).toFixed(1);
        var sorted = item.dataset.data.slice().sort(function(a, b) { return b - a; });
        var rank = sorted.indexOf(val) + 1;
        var avg = totalBar / values.length;
        var diff = val - avg;
        var sign = diff >= 0 ? '+' : '';

        return '<div class="tt-title">📊 ' + item.label + '</div>'
            + '<div class="tt-row"><span class="tt-color" style="background:' + color + '"></span>' + (label || 'Valeur') + ' : <strong>' + fmtNum(val) + ' CHF</strong></div>'
            + '<div class="tt-detail">Part du total : ' + pct + '%</div>'
            + '<div class="tt-detail">Classement : #' + rank + ' / ' + values.length + '</div>'
            + '<div class="tt-footer">Moy. : ' + fmtNum(avg) + ' CHF (' + sign + fmtNum(diff) + ')</div>';
    });

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: label || 'Valeur',
                data: values,
                backgroundColor: bgColors,
                hoverBackgroundColor: hoverColors,
                borderRadius: 6,
                borderSkipped: false,
                maxBarThickness: 48,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: { display: false },
                tooltip: barTooltip,
            },
            scales: commonScaleOptions,
        }
    });
}


/* ==== BAR CHART HORIZONTAL ==== */
function initHorizontalBarChart(canvasId, labels, values) {
    var ctx = document.getElementById(canvasId);
    if (!ctx) return;

    var totalHBar = values.reduce(function(a, b) { return a + b; }, 0);
    var maxHBar = Math.max.apply(null, values);

    var hBarTooltip = getBaseTooltipStyle(function(tooltip) {
        var item = tooltip.dataPoints[0];
        var val = item.parsed.x;
        var color = item.dataset.backgroundColor[item.dataIndex] || item.dataset.backgroundColor;
        var pct = ((val / totalHBar) * 100).toFixed(1);
        var rank = item.dataIndex + 1;
        var best = val === maxHBar ? '<div class="tt-badge">🥇 Meilleur résultat</div>' : '';

        return '<div class="tt-title">🏷️ ' + item.label + '</div>'
            + '<div class="tt-row"><span class="tt-color" style="background:' + color + '"></span>CA HT : <strong>' + fmtNum(val) + ' CHF</strong></div>'
            + '<div class="tt-detail">Part du total : ' + pct + '%</div>'
            + '<div class="tt-detail">Rang : #' + rank + ' / ' + labels.length + '</div>'
            + best
            + '<div class="tt-footer">Total cumulé : ' + fmtNum(totalHBar) + ' CHF</div>';
    });

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'CA HT (CHF)',
                data: values,
                backgroundColor: COLORS.paletteSoft.slice(0, labels.length),
                hoverBackgroundColor: COLORS.palette.slice(0, labels.length),
                borderRadius: 6,
                borderSkipped: false,
                barThickness: 28,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            indexAxis: 'y',
            interaction: { mode: 'index', intersect: false, axis: 'y' },
            hover: { mode: 'index', intersect: false, axis: 'y' },
            plugins: {
                legend: { display: false },
                tooltip: hBarTooltip,
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(v) { return v.toLocaleString('fr-CH'); },
                        font: { size: 11, weight: '500' },
                        color: '#94a3b8',
                    },
                    grid: { color: 'rgba(226, 232, 240, 0.6)', drawBorder: false },
                    border: { display: false },
                },
                y: {
                    grid: { display: false },
                    border: { display: false },
                    ticks: { font: { size: 12, weight: '600' }, color: '#1e293b' },
                },
            }
        }
    });
}


/* ==== DOUGHNUT CHART ==== */
function initDoughnutChart(canvasId, labels, values) {
    var ctx = document.getElementById(canvasId);
    if (!ctx) return;

    var total = values.reduce(function(a, b) { return a + b; }, 0);
    var formattedTotal = total.toFixed(0).replace(/\B(?=(\d{3})+(?!\d))/g, ' ');

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: COLORS.paletteSoft.slice(0, labels.length),
                hoverBackgroundColor: COLORS.palette.slice(0, labels.length),
                borderWidth: 3,
                borderColor: '#ffffff',
                hoverBorderColor: '#ffffff',
                hoverOffset: 6,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            cutout: '62%',
            interaction: { mode: 'nearest', intersect: true },
            plugins: {
                centerText: {
                    value: formattedTotal,
                    label: 'CHF total',
                },
                legend: {
                    display: true,
                    position: 'bottom',
                    labels: {
                        padding: 16,
                        usePointStyle: true,
                        pointStyleWidth: 10,
                        font: { size: 12, weight: '500' },
                    }
                },
                tooltip: getBaseTooltipStyle(function(tooltip) {
                    var item = tooltip.dataPoints[0];
                    var val = item.parsed;
                    var color = item.dataset.backgroundColor[item.dataIndex];
                    var pct = ((val / total) * 100).toFixed(1);
                    var sorted = item.dataset.data.slice().sort(function(a, b) { return b - a; });
                    var rank = sorted.indexOf(val) + 1;

                    return '<div class="tt-title">🔵 ' + item.label + '</div>'
                        + '<div class="tt-row"><span class="tt-color" style="background:' + color + '"></span>Montant : <strong>' + fmtNum(val) + ' CHF</strong></div>'
                        + '<div class="tt-detail">Part : ' + pct + '% du total</div>'
                        + '<div class="tt-detail">Rang : #' + rank + ' / ' + labels.length + ' catégories</div>'
                        + '<div class="tt-footer">Total : ' + fmtNum(total) + ' CHF</div>';
                })
            },
        }
    });
}


/* ==== UTILITAIRE : LIGNE DE TENDANCE (régression linéaire) ==== */
function calculateTrendLine(values) {
    var n = values.length;
    var sumX = 0, sumY = 0, sumXY = 0, sumXX = 0;
    for (var i = 0; i < n; i++) {
        sumX += i;
        sumY += values[i];
        sumXY += i * values[i];
        sumXX += i * i;
    }
    var slope = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX);
    var intercept = (sumY - slope * sumX) / n;
    var trend = [];
    for (var j = 0; j < n; j++) {
        trend.push(Math.round(slope * j + intercept));
    }
    return trend;
}


/* ==== INITIALISATION DIFFÉRÉE DES GRAPHIQUES ==== */
/**
 * File d'attente pour initialiser les graphiques APRÈS les animations CSS.
 * Évite le bug où Chart.js calcule mal les dimensions du canvas
 * quand le conteneur est encore en opacity:0 / transform.
 */
var _chartQueue = [];
var _chartsReady = false;

function queueChart(fn) {
    if (_chartsReady) {
        fn();
    } else {
        _chartQueue.push(fn);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Les animations CSS durent 0.5s + max delay de 0.33s = ~0.85s
    // On attend 900ms pour être sûr que tout est terminé
    setTimeout(function() {
        _chartsReady = true;
        _chartQueue.forEach(function(fn) { fn(); });
        _chartQueue = [];
    }, 900);
});


/* ==== FORMATAGE AUTOMATIQUE DES NOMBRES (data-format) ==== */
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('[data-format]').forEach(function(el) {
        var raw = el.getAttribute('data-raw');
        var decimals = parseInt(el.getAttribute('data-format')) || 0;
        if (raw !== null && raw !== '') {
            el.textContent = fmtNum(parseFloat(raw), decimals);
        }
    });
});


/* ==== TABLEAUX TRIABLES ==== */
document.addEventListener('DOMContentLoaded', function() {
    // Rendre tous les <th class="sortable"> cliquables
    document.querySelectorAll('.data-table th.sortable').forEach(function(th) {
        th.addEventListener('click', function() {
            var table = th.closest('table');
            var tbody = table.querySelector('tbody');
            var rows = Array.from(tbody.querySelectorAll('tr'));
            var colIdx = Array.from(th.parentNode.children).indexOf(th);
            var isNumeric = th.hasAttribute('data-sort-num');

            // Toggle direction
            var isAsc = th.classList.contains('sort-asc');
            // Reset all headers
            table.querySelectorAll('th.sortable').forEach(function(h) {
                h.classList.remove('sort-asc', 'sort-desc');
            });

            var direction = isAsc ? -1 : 1;
            th.classList.add(isAsc ? 'sort-desc' : 'sort-asc');

            rows.sort(function(a, b) {
                var cellA = a.children[colIdx];
                var cellB = b.children[colIdx];
                var valA = cellA.getAttribute('data-raw') || cellA.textContent.trim();
                var valB = cellB.getAttribute('data-raw') || cellB.textContent.trim();

                if (isNumeric) {
                    valA = parseFloat(valA.replace(/[^\d.-]/g, '')) || 0;
                    valB = parseFloat(valB.replace(/[^\d.-]/g, '')) || 0;
                    return (valA - valB) * direction;
                }
                return valA.localeCompare(valB, 'fr') * direction;
            });

            // Animation de tri
            rows.forEach(function(row, i) {
                row.style.opacity = '0';
                row.style.transform = 'translateY(-4px)';
                tbody.appendChild(row);
                setTimeout(function() {
                    row.style.transition = 'all 0.2s ease';
                    row.style.opacity = '1';
                    row.style.transform = 'translateY(0)';
                }, i * 30);
            });
        });
    });
});
