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
    primary: '#3B82F6',
    primaryRgb: '59, 130, 246',
    primaryLight: 'rgba(59, 130, 246, 0.12)',
    success: '#10B981',
    successRgb: '16, 185, 129',
    warning: '#F59E0B',
    warningRgb: '245, 158, 11',
    danger: '#F43F5E',
    purple: '#8B5CF6',
    teal: '#06B6D4',
    pink: '#EC4899',
    sky: '#38BDF8',
    palette: ['#3B82F6', '#10B981', '#F59E0B', '#F43F5E', '#8B5CF6', '#06B6D4', '#EC4899', '#38BDF8'],
    paletteSoft: [
        'rgba(59, 130, 246, 0.75)',
        'rgba(16, 185, 129, 0.75)',
        'rgba(245, 158, 11, 0.75)',
        'rgba(244, 63, 94, 0.75)',
        'rgba(139, 92, 246, 0.75)',
        'rgba(6, 182, 212, 0.75)',
        'rgba(236, 72, 153, 0.75)',
        'rgba(56, 189, 248, 0.75)',
    ],
};


/* ==== CONFIGURATION GLOBALE CHART.JS ==== */
Chart.defaults.font.family = "-apple-system, 'SF Pro Text', 'SF Pro Display', 'Helvetica Neue', system-ui, sans-serif";
Chart.defaults.font.size = 11;
Chart.defaults.color = 'rgba(247,248,250,0.35)';
Chart.defaults.animation = {
    duration: 800,
    easing: 'easeOutQuart',
};


/* ==== PLUGIN : TEXTE CENTRAL DOUGHNUT (dynamique au survol) ==== */
const centerTextPlugin = {
    id: 'centerText',
    afterDraw(chart) {
        if (chart.config.type !== 'doughnut' || !chart.config.options.plugins.centerText) return;
        const { ctx, chartArea: { width, height, top } } = chart;

        // Utilise le segment survolé si disponible, sinon le texte par défaut
        const text = chart._hoveredSegment || chart.config.options.plugins.centerText;
        const isHovered = !!chart._hoveredSegment;

        ctx.save();
        // Valeur
        ctx.font = "700 " + (isHovered ? '1rem' : '1.125rem') + " -apple-system, 'SF Pro Display', system-ui, sans-serif";
        ctx.fillStyle = isHovered ? chart._hoveredSegment.color : '#F7F8FA';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(text.value || '', width / 2, top + height / 2 - 8);
        // Label
        ctx.font = "500 0.625rem -apple-system, 'SF Pro Text', system-ui, sans-serif";
        ctx.fillStyle = 'rgba(247,248,250,0.35)';
        ctx.fillText(text.label || '', width / 2, top + height / 2 + 11);
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
        ctx.strokeStyle = 'rgba(59, 130, 246, 0.30)';
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

    if (tooltip.opacity === 0) {
        tooltipEl.style.opacity = '0';
        tooltipEl.style.pointerEvents = 'none';
        return;
    }

    var inner = tooltipEl.querySelector('.chartjs-tooltip-inner');
    if (tooltip.body) {
        inner.innerHTML = buildContent(tooltip, chart);
    }

    tooltipEl.style.opacity = '1';
    tooltipEl.style.pointerEvents = 'none';

    // --- Positionnement intelligent (évite les débordements) ---
    var canvasW  = chart.canvas.offsetWidth;
    var canvasH  = chart.canvas.offsetHeight;
    var ttW      = tooltipEl.offsetWidth  || 190;
    var ttH      = tooltipEl.offsetHeight || 110;
    var caretX   = tooltip.caretX;
    var caretY   = tooltip.caretY;
    var margin   = 8;

    // Horizontal : centré sur le caret, clampé aux bords
    var left = Math.max(margin, Math.min(caretX - ttW / 2, canvasW - ttW - margin));

    // Vertical : par défaut au-dessus, bascule en-dessous si trop proche du haut
    var top, transformY;
    if (caretY - ttH - 14 < 0) {
        top = caretY + 14;        // afficher en-dessous
        transformY = '0%';
    } else {
        top = caretY - 14;        // afficher au-dessus
        transformY = '-100%';
    }

    tooltipEl.style.left      = left + 'px';
    tooltipEl.style.top       = top  + 'px';
    tooltipEl.style.transform = 'translateY(' + transformY + ')';
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
            font: { size: 11, weight: '400' },
            color: 'rgba(247,248,250,0.40)',
            maxTicksLimit: 5,
            padding: 8,
        },
        grid: { color: 'rgba(255,255,255,0.04)', drawBorder: false },
        border: { display: false },
    },
    x: {
        grid: { display: false },
        border: { display: false },
        ticks: {
            font: { size: 11, weight: '400' },
            color: 'rgba(247,248,250,0.40)',
            maxRotation: 40,
            padding: 4,
        },
    },
};


/* ==== LINE CHART ==== */
function initLineChart(canvasId, labels, values, label) {
    var ctx = document.getElementById(canvasId);
    if (!ctx) return;

    var context2d = ctx.getContext('2d');
    var gradient = context2d.createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, 'rgba(' + COLORS.primaryRgb + ', 0.18)');
    gradient.addColorStop(1, 'rgba(' + COLORS.primaryRgb + ', 0.00)');

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
        pointBorderColor: '#0D1117',
        pointBorderWidth: 2,
        pointHoverBackgroundColor: COLORS.primary,
        pointHoverBorderColor: '#F7F8FA',
        pointHoverBorderWidth: 3,
        pointHitRadius: 20,
    }];

    if (values.length >= 3) {
        var trend = calculateTrendLine(values);
        datasets.push({
            label: 'Tendance',
            data: trend,
            borderColor: 'rgba(' + COLORS.primaryRgb + ', 0.30)',
            borderWidth: 1.5,
            borderDash: [6, 4],
            fill: false,
            pointRadius: 0,
            pointHoverRadius: 0,
        });
    }

    var lineTooltip = getBaseTooltipStyle(function(tooltip, chart) {
        var title = tooltip.title ? tooltip.title[0] : '';
        var html = '<div class="tt-title">' + title + '</div>';

        var mainItem = null;
        for (var i = 0; i < tooltip.dataPoints.length; i++) {
            if (tooltip.dataPoints[i].datasetIndex === 0) {
                mainItem = tooltip.dataPoints[i];
                break;
            }
        }

        if (mainItem) {
            var val  = mainItem.parsed.y;
            var data = mainItem.dataset.data;
            var idx  = mainItem.dataIndex;
            var color = mainItem.dataset.borderColor;

            // Valeur principale
            html += '<div class="tt-row"><span class="tt-color" style="background:' + color + '"></span>CA HT : <strong>' + fmtNum(val) + ' CHF</strong></div>';

            // Variation vs mois précédent
            if (idx > 0 && data[idx - 1] > 0) {
                var prev  = data[idx - 1];
                var diff  = val - prev;
                var pct   = ((diff / prev) * 100).toFixed(1);
                var arrow = diff >= 0 ? '▲' : '▼';
                var sign  = diff >= 0 ? '+' : '';
                var cls   = diff >= 0 ? 'tt-up' : 'tt-down';
                html += '<div class="tt-variation ' + cls + '">' + arrow + ' ' + sign + pct + '% vs mois préc. (' + sign + fmtNum(diff) + ' CHF)</div>';
            }

            // Indicateur min / max de la période
            var maxVal = Math.max.apply(null, data);
            var minVal = Math.min.apply(null, data.filter(function(v) { return v > 0; }));
            if (val === maxVal && data.length > 1) {
                html += '<div class="tt-badge">&#9650; Meilleur mois de la période</div>';
            } else if (val === minVal && data.length > 1) {
                html += '<div class="tt-variation tt-down">&#9660; Mois le plus faible</div>';
            }

            // Cumul YTD + moyenne
            var cumul = data.slice(0, idx + 1).reduce(function(a, b) { return a + b; }, 0);
            var total = data.reduce(function(a, b) { return a + b; }, 0);
            var avg   = total / data.filter(function(v) { return v > 0; }).length;
            html += '<div class="tt-detail">Cumul période : ' + fmtNum(cumul) + ' CHF</div>';
            html += '<div class="tt-footer">Moy. mensuelle : ' + fmtNum(Math.round(avg)) + ' CHF</div>';
        }
        return html;
    });

    new Chart(ctx, {
        type: 'line',
        data: { labels: labels, datasets: datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            layout: { padding: { top: 16, bottom: 8, left: 4, right: 16 } },
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

    var maxVal = Math.max.apply(null, values);
    var bgColors = values.map(function(v) {
        var ratio = v / maxVal;
        if (ratio >= 0.8) return 'rgba(' + COLORS.primaryRgb + ', 0.90)';
        if (ratio >= 0.5) return 'rgba(' + COLORS.primaryRgb + ', 0.65)';
        return 'rgba(' + COLORS.primaryRgb + ', 0.40)';
    });

    var hoverColors = values.map(function() {
        return COLORS.primary;
    });

    var totalBar = values.reduce(function(a, b) { return a + b; }, 0);

    var barTooltip = getBaseTooltipStyle(function(tooltip) {
        var item  = tooltip.dataPoints[0];
        var val   = item.parsed.y;
        var color = item.dataset.backgroundColor[item.dataIndex] || item.dataset.backgroundColor;
        var pct   = ((val / totalBar) * 100).toFixed(1);
        var sorted = item.dataset.data.slice().sort(function(a, b) { return b - a; });
        var rank  = sorted.indexOf(val) + 1;
        var avg   = totalBar / values.length;
        var diff  = val - avg;
        var sign  = diff >= 0 ? '+' : '';
        var maxVal = Math.max.apply(null, values);
        var minVal = Math.min.apply(null, values.filter(function(v) { return v > 0; }));

        var badge = '';
        if (val === maxVal && values.length > 1) {
            badge = '<div class="tt-badge">&#9650; Meilleur mois</div>';
        } else if (val === minVal && values.length > 1) {
            badge = '<div class="tt-variation tt-down">&#9660; Mois le plus faible</div>';
        }

        return '<div class="tt-title">' + item.label + '</div>'
            + '<div class="tt-row"><span class="tt-color" style="background:' + color + '"></span>' + (label || 'Valeur') + ' : <strong>' + fmtNum(val) + ' CHF</strong></div>'
            + '<div class="tt-detail">Part du total : ' + pct + '%</div>'
            + '<div class="tt-detail">Classement : #' + rank + ' / ' + values.length + '</div>'
            + badge
            + '<div class="tt-footer">Moy. : ' + fmtNum(Math.round(avg)) + ' CHF (' + sign + fmtNum(Math.round(diff)) + ')</div>';
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
            maintainAspectRatio: false,
            layout: { padding: { top: 16, bottom: 8, left: 4, right: 16 } },
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
        var best = val === maxHBar ? '<div class="tt-badge">Meilleur résultat</div>' : '';

        return '<div class="tt-title">' + item.label + '</div>'
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
            maintainAspectRatio: false,
            layout: { padding: { top: 8, bottom: 8, left: 4, right: 24 } },
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
                        font: { size: 11, weight: '400' },
                        color: 'rgba(247,248,250,0.40)',
                        maxTicksLimit: 4,
                        padding: 6,
                    },
                    grid: { color: 'rgba(255,255,255,0.04)', drawBorder: false },
                    border: { display: false },
                },
                y: {
                    grid: { display: false },
                    border: { display: false },
                    ticks: {
                        font: { size: 12, weight: '500' },
                        color: 'rgba(247,248,250,0.70)',
                        padding: 8,
                    },
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

    var doughnutChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: COLORS.paletteSoft.slice(0, labels.length),
                hoverBackgroundColor: COLORS.palette.slice(0, labels.length),
                borderWidth: 3,
                borderColor: '#0D1117',
                hoverBorderColor: '#0D1117',
                hoverOffset: 6,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '62%',
            layout: { padding: { top: 8, bottom: 8, left: 8, right: 8 } },
            interaction: { mode: 'nearest', intersect: true },
            onHover: function(event, activeElements, chart) {
                // Met à jour le texte central avec le segment survolé
                var newHovered = null;
                if (activeElements.length > 0) {
                    var el    = activeElements[0];
                    var val   = chart.data.datasets[el.datasetIndex].data[el.index];
                    var lbl   = chart.data.labels[el.index];
                    var color = COLORS.palette[el.index % COLORS.palette.length];
                    newHovered = {
                        value: fmtNum(val) + ' CHF',
                        label: lbl,
                        color: color,
                    };
                }
                // Ne redessine que si le segment a changé
                var prevStr = chart._hoveredSegment ? chart._hoveredSegment.label : null;
                var newStr  = newHovered ? newHovered.label : null;
                if (prevStr !== newStr) {
                    chart._hoveredSegment = newHovered;
                    chart.update('none');
                }
            },
            plugins: {
                centerText: {
                    value: formattedTotal,
                    label: 'CHF total',
                },
                legend: {
                    display: true,
                    position: 'top',
                    align: 'center',
                    labels: {
                        padding: 12,
                        usePointStyle: true,
                        pointStyleWidth: 7,
                        font: { size: 11, weight: '400' },
                        color: 'rgba(247,248,250,0.50)',
                        boxHeight: 7,
                    }
                },
                tooltip: getBaseTooltipStyle(function(tooltip) {
                    var item  = tooltip.dataPoints[0];
                    var val   = item.parsed;
                    var color = item.dataset.backgroundColor[item.dataIndex];
                    var pct   = ((val / total) * 100).toFixed(1);
                    var sorted = item.dataset.data.slice().sort(function(a, b) { return b - a; });
                    var rank  = sorted.indexOf(val) + 1;
                    var isTop = rank === 1 ? '<div class="tt-badge">&#9733; Catégorie principale</div>' : '';

                    return '<div class="tt-title">' + item.label + '</div>'
                        + '<div class="tt-row"><span class="tt-color" style="background:' + color + '"></span>Montant : <strong>' + fmtNum(val) + ' CHF</strong></div>'
                        + '<div class="tt-detail">Part : ' + pct + '% du total</div>'
                        + '<div class="tt-detail">Rang : #' + rank + ' / ' + labels.length + '</div>'
                        + isTop
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
    // Délai minimal pour laisser le DOM se stabiliser avant le premier rendu
    setTimeout(function() {
        _chartsReady = true;
        _chartQueue.forEach(function(fn) { fn(); });
        _chartQueue = [];
    }, 50);
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
    document.querySelectorAll('.data-table th.sortable').forEach(function(th) {
        th.addEventListener('click', function() {
            var table = th.closest('table');
            var tbody = table.querySelector('tbody');
            var rows = Array.from(tbody.querySelectorAll('tr'));
            var colIdx = Array.from(th.parentNode.children).indexOf(th);
            var isNumeric = th.hasAttribute('data-sort-num');

            var isAsc = th.classList.contains('sort-asc');
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
