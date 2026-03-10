const form = document.getElementById("uploadForm");
const resultsDiv = document.getElementById("results");
let chart;

// Handle file upload
form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const fileInput = document.getElementById("fileInput").files[0];
    const show = document.getElementById("showSelect").value;
    if (!fileInput) { alert("Please select a file."); return; }

    // Check allowed types
    const allowedTypes = ["audio/wav","audio/mp3","audio/mpeg","video/mp4","video/webm"];
    if(!allowedTypes.includes(fileInput.type)){
        alert("Please upload an audio or video file (.mp3, .wav, .mp4, .webm).");
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput);
    formData.append("show", show);

    const response = await fetch("/analyze", { method: "POST", body: formData });
    const data = await response.json();
    showResults(data);
});

// Recorder
let mediaRecorder;
let recordedChunks = [];

const preview = document.getElementById("preview");
const startBtn = document.getElementById("startRec");
const stopBtn = document.getElementById("stopRec");

navigator.mediaDevices.getUserMedia({ video: true, audio: true })
  .then(stream => {
    preview.srcObject = stream;
    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.ondataavailable = e => { if(e.data.size > 0) recordedChunks.push(e.data); };
  })
  .catch(err => console.error("Camera access error:", err));

startBtn.onclick = () => {
    recordedChunks = [];
    mediaRecorder.start();
    startBtn.disabled = true;
    stopBtn.disabled = false;
};

stopBtn.onclick = () => {
    mediaRecorder.stop();
    startBtn.disabled = false;
    stopBtn.disabled = true;
    mediaRecorder.onstop = async () => {
        const blob = new Blob(recordedChunks, { type: "video/webm" });
        const file = new File([blob], "audition.webm", { type: "video/webm" });
        const show = document.getElementById("showSelect").value;
        const formData = new FormData();
        formData.append("file", file);
        formData.append("show", show);

        const response = await fetch("/analyze", { method: "POST", body: formData });
        const data = await response.json();
        showResults(data);
    };
};

// Display feedback + chart
function showResults(data) {
    resultsDiv.innerHTML = `<pre>${data.feedback}</pre>`;
    if(chart) chart.destroy();

    const roles = Object.keys(data.role_probabilities || {});
    const probs = Object.values(data.role_probabilities || {});

    if(roles.length === 0) return;

    const ctx = document.createElement('canvas');
    resultsDiv.appendChild(ctx);

    chart = new Chart(ctx.getContext('2d'), {
        type: 'bar',
        data: {
            labels: roles,
            datasets: [{
                label: 'Role Probability (%)',
                data: probs,
                backgroundColor: '#ff9800'
            }]
        },
        options: {
            scales: { y: { beginAtZero: true, max: 100 } }
        }
    });
}
