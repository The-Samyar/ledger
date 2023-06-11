var doughnutChartData = JSON.parse(JSON.parse(document.getElementById('doughnutData').textContent))
console.log(doughnutChartData)

const dataDoughnut = doughnutChartData

const configDoughnut = {
type: "doughnut",
data: dataDoughnut,
options: {
    plugins: {
        legend: {
            labels: {
                color : "#FBFBFF",
                font: {
                    size: 12
                }
            }
        }
    },
    cutout :'55%',
    radius : '90%'
}
};

var chartBar = new Chart(document.getElementById("chartDoughnut"), configDoughnut);

var lineChartData = JSON.parse(JSON.parse(document.getElementById('lineData').textContent))
console.log(lineChartData)
const data = lineChartData

const configLineChart = {
    type: "line",
    data,
    options: {
        plugins: {
            legend: {
                labels: {
                    color : "#FBFBFF",
                    font: {
                        size: 14
                    }
                }
            }
        },

        scales: {
            y : {
                ticks : {
                    color : '#FBFBFF'
                }
            },
            x : {
                ticks : {
                    color : '#FBFBFF'
                }
            }
        }
    },
};

var chartLine = new Chart(
    document.getElementById("chartLine"),
    configLineChart
);


function dropDownFunction(){
    element = document.getElementById("userDropdown")
    if (element.hidden == false){
        element.hidden = true
    } else {
        element.hidden = false
    }
}
