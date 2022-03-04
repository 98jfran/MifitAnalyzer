window.addEventListener('DOMContentLoaded', event => {
    var sleepRecords = reportRAW['report']['origin']['sleep'];

    sleepRecords = sleepRecords.filter((e) => isBetweenGlobalDates(Date.parse(e.date + " " + e.from)/1000));
    let recordsHTML=''
    sleepRecords.forEach(function (item) {
      //TODO FIX

      if(isBetweenGlobalDates(Date.parse(item.date + " " + item.from)/1000)){
        recordsHTML+=`
        <tr>
            <td>${item.date}</td>
            <td>${item.from}</td>
            <td>${item.to}</td>
            <td>${item.mode}</td>
        </tr>`
      }
    });
    

    document.getElementById("sleep-datatable-records").innerHTML = recordsHTML;

    const heartRateDatatable = document.getElementById('sleep-datatable');
    if (heartRateDatatable) {
        new simpleDatatables.DataTable(heartRateDatatable);
    }

Chart.defaults.global.defaultFontFamily = '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#292b2c';

var heartRateChart = document.getElementById("sleep-chart");
new Chart(heartRateChart, {
  type: 'line',
  data: {
    labels: sleepRecords.map((e) => e.mode),
    datasets: [{
      label: "Sleep Mode",
      lineTension: 0.3,
      backgroundColor: "rgba(2,117,216,0.2)",
      borderColor: "rgba(2,117,216,1)",
      pointRadius: 5,
      pointBackgroundColor: "rgba(2,117,216,1)",
      pointBorderColor: "rgba(255,255,255,0.8)",
      pointHoverRadius: 5,
      pointHoverBackgroundColor: "rgba(2,117,216,1)",
      pointHitRadius: 50,
      pointBorderWidth: 2,
      data: sleepRecords.map((e) => e.date),
    }],
  },
  options: {
    scales: {
      xAxes: [{
        time: {
          unit: 'date'
        },
        gridLines: {
          display: false
        },
        ticks: {
          maxTicksLimit: 7
        }
      }],
      yAxes: [{
        ticks: {
          min: Math.min.apply(Math, sleepRecords.map((o) => o.value )) -10,
          max: Math.max.apply(Math, sleepRecords.map((o) => o.value )) + 10,
          maxTicksLimit: 10
        },
        gridLines: {
          color: "rgba(0, 0, 0, .125)",
        }
      }],
    },
    legend: {
      display: false
    }
  }
});




});
