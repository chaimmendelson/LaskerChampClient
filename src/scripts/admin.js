const engine = 'engine';
const online = 'online';
const newAccounts = 'new';

const engineChart = 'engineChart';
const onlineChart = 'onlineChart';
const accountsChart = 'accountsChart';

let stats = null;

async function getStats() {
    const response = await fetch('/stats', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        },
    });
  const data = await response.json();
  return data.stats;
}

async function reloadStats() {
    stats = await getStats();
}

function setCurrentStats() {
    const key_d = {
        'online': 'Online Games',
        'engine': 'Engine Games',
        'accounts': 'Online players',
        'count': 'Total accounts'
    };
    table = '<tr><th>Stat</th><th>Value</th></tr>';
    for (const [key, value] of Object.entries(stats['current'])) {
        table += `<tr><td>${key_d[key]}</td><td>${value}</td></tr>`;
    }
    document.getElementById('stats').innerHTML = table;
    getDataForPeriod(stats['overall'], 7, engine);
};

// Assume the data is stored in an object with date keys and daily game play values

function getDataForPeriod(days, key) {
    const data = stats['overall'];
    let periodData = {};
    const today = new Date().toISOString().slice(0, 10);
    const date = new Date(today);
    for (let i = 0; i < days; i++) {
        date.setDate(date.getDate() - i);
        const dateString = date.toISOString().slice(0, 10);
        if (dateString in data) {
            periodData[dateString] = data[dateString][key];
        }
    }
    return periodData;
}

Array.prototype.max = function() {
    return Math.max.apply(null, this);
  };
  
Array.prototype.min = function() {
    return Math.min.apply(null, this);
};


function set_chart_data(data, id) {
    const xValues = Object.keys(data);
    const yValues = Object.values(data);
    let max = yValues.max() + 1;
    max = Math.ceil(max / 10) * 10;
    new Chart(id, {
        type: "line",
        data: {
            labels: xValues,
            datasets: [{
            fill: false,
            lineTension: 0,
            backgroundColor: "rgba(0,0,255,1.0)",
            borderColor: "rgba(0,0,255,0.1)",
            data: yValues
            }]
        },
        options: {
            legend: {display: false},
            scales: {
            yAxes: [{ticks: {min: 0, max: max}}],
            }
        }
    });
}

async function set_stats(){
    await reloadStats();
    setCurrentStats();
    set_chart_data(getDataForPeriod(7, engine), engineChart);
    set_chart_data(getDataForPeriod(7, online), onlineChart);
    set_chart_data(getDataForPeriod(7, newAccounts), accountsChart);
}

window.onload = async function() {
    await set_stats();
}