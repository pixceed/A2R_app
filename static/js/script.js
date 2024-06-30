const JCD_MAX = 24;
const RACE_NUM_MAX = 12;

async function dateFormat(today, format){
    format = format.replace("YYYY", today.getFullYear());
    format = format.replace("MM", ("0"+(today.getMonth() + 1)).slice(-2));
    format = format.replace("DD", ("0"+ today.getDate()).slice(-2));
    return format;
}

async function setDefaultValue() {
    // レース場コード
    const selectJCD = document.getElementById("jcd");
    for (let i = 0; i <= JCD_MAX; i++) {
        const option = document.createElement("option");
        option.value = i;
        option.text = i;
        selectJCD.appendChild(option);
    }

    // レース場コード
    const selectRaceNum = document.getElementById("racenum");
    for (let i = 0; i <= RACE_NUM_MAX; i++) {
        const option = document.createElement("option");
        option.value = i;
        option.text = i;
        selectRaceNum.appendChild(option);
    }

    // レース日
    const inputDate = document.getElementById("date");
    inputDate.value = dateFormat(new Date(),'YYYY-MM-DD');;
}

async function sendData() {
    const form = document.getElementById('myForm');
    const formData = new FormData(form);
    
    const data = {
        jcd: formData.get('jcd'),
        racenum: parseInt(formData.get('racenum')),
        date: formData.get('date'),
        should_dl: formData.get('should_dl') === 'true'
    };

    fetch('/your-backend-endpoint', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        displayPredictedData(data);
        console.log('Success:', data);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

async function displayPredictedData(data) {
    const predictedData = []
    for (let i = 0; i < data.length; i++) {
        const prediction = data[i];
        const expectation = prediction['expectation'];
        const odds = prediction['odds'];
        const order3t = [prediction['first'], prediction['second'], prediction['third']];
        predictedData.push({expectation, odds, order3t});
    
    }

    // const predictedData = [
    //     {expectation: 0.987, odds: 10.1, order3t: [1,2,3]},
    //     {expectation: 1.01, odds: 2.3, order3t: [1,2,3]},
    // ];

    const tableBody = document.getElementById('data-table-body');
    predictedData.forEach(data => {
        const row = document.createElement('tr');

        const cellExpectation = document.createElement('td');
        cellExpectation.textContent = data.expectation;
        row.appendChild(cellExpectation);

        const cellOdds = document.createElement('td');
        cellOdds.textContent = data.odds;
        row.appendChild(cellOdds);

        const cellOrder3T = document.createElement('td');
        cellOrder3T.textContent = data.order3t.join(', ');
        row.appendChild(cellOrder3T);

        tableBody.appendChild(row);
    });


}
setDefaultValue();
displayPredictedData();