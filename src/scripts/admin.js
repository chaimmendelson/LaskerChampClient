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

getStats().then(stats => {
    table = '<tr><th>Stat</th><th>Value</th></tr>';
    for (const [key, value] of Object.entries(stats['current'])) {
        table += `<tr><td>${key}</td><td>${value}</td></tr>`;
    }
    document.getElementById('stats').innerHTML = table;
});