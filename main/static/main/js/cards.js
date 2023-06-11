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
        maintainAspectRatio: false,

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
var lineChart = new Chart(
document.getElementById("lineChart"),
configLineChart
);

function fillEditCardForm(selectedOption){
    const cards = JSON.parse(JSON.parse(document.getElementById('cards_json').textContent));
    for (i=0; i<cards.length; i++){
        if(cards[i].pk == selectedOption.value){
            let card = cards[i].fields
            document.getElementById("edited_card_number").value = card['card_number']
            document.getElementById("edited_card_expdate").value = card['expiry_date']
            document.getElementById("edited_card_bankname").value = card['bank_name']
            document.getElementById("edited_card_balance").value = card['balance']
            document.getElementById('editCardForm').action = "/cards/edit/" + cards[i].pk + "/"
            document.getElementById("deleteCard").href = "/cards/delete/" + cards[i].pk + "/"
        }
    }
}
