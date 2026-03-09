const form = document.getElementById("uploadForm");
const resultsDiv = document.getElementById("results");
let chart;

form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const fileInput = document.getElementById("fileInput").files[0];
    const show = document.getElementById("showSelect").value;
    if (!fileInput) { alert("Upload a file."); return; }

    const formData = new FormData();
    formData.append("file", fileInput);
    formData.append("show", show);

    const response = await fetch("/analyze", {
        method: "POST",
        body: formData
    });

    const data = await response.json();
    resultsDiv.innerHTML = `<pre>${data.feedback}</pre><canvas id="scoreChart" width="400" height="200"></canvas>`;

    const ctx = document.getElementById('scoreChart').getContext('2d');
    if(chart) chart.destroy();
    chart = new Chart(ctx, {
        type:'bar',
        data:{
            labels:['Voice','Acting','Overall'],
            datasets:[{
                label:'Score (/10)',
                data:[data.voice_score,data.acting_score,data.overall_score],
                backgroundColor:['#4caf50','#2196f3','#ff9800']
            }]
        },
        options:{scales:{y:{beginAtZero:true,max:10}}}
    });
});
