let currentUser = null
const form = document.getElementById("uploadForm")
const resultsDiv = document.getElementById("results")
let chart

// ---------- ACCOUNT SYSTEM ----------
async function signup(){
    const username = document.getElementById("username").value
    const password = document.getElementById("password").value
    const formData = new FormData()
    formData.append("username",username)
    formData.append("password",password)
    const res = await fetch("/signup",{method:"POST",body:formData})
    const data = await res.json()
    document.getElementById("loginStatus").innerText = data.message
}

async function login(){
    const username = document.getElementById("username").value
    const password = document.getElementById("password").value
    const formData = new FormData()
    formData.append("username",username)
    formData.append("password",password)
    const res = await fetch("/login",{method:"POST",body:formData})
    const data = await res.json()
    if(data.success){
        currentUser = username
        document.getElementById("loginStatus").innerText = "Logged in!"
        loadHistory()
    } else{
        document.getElementById("loginStatus").innerText = "Login failed"
    }
}

// ---------- FILE UPLOAD ----------
form.addEventListener("submit",async(e)=>{
    e.preventDefault()
    const file = document.getElementById("fileInput").files[0]
    let show = document.getElementById("showSelect").value
    if(currentUser){ show = show + "|" + currentUser }
    const formData = new FormData()
    formData.append("file",file)
    formData.append("show",show)
    const response = await fetch("/analyze",{method:"POST",body:formData})
    const data = await response.json()
    showResults(data)
})

// ---------- AUDITION HISTORY ----------
async function loadHistory(){
    const res = await fetch("/history/"+currentUser)
    const data = await res.json()
    let html = "<h2>🎭 Your Past Auditions</h2>"
    data.history.forEach(h=>{
        html += `<div class="history-card"><b>${h.show}</b><pre>${h.feedback}</pre></div>`
    })
    resultsDiv.innerHTML = html
}

// ---------- SHOW RESULTS ----------
function showResults(data){
    resultsDiv.innerHTML = `<pre>${data.feedback}</pre>`
    if(chart) chart.destroy()
    const roles = Object.keys(data.role_probabilities || {})
    const probs = Object.values(data.role_probabilities || {})
    if(roles.length===0) return
    const ctx = document.createElement("canvas")
    resultsDiv.appendChild(ctx)
    const maxProb = Math.max(...probs)
    const colors = probs.map(p=>p===maxProb ? "#ff5722":"#4caf50")
    chart = new Chart(ctx.getContext("2d"),{
        type:"bar",
        data:{ labels:roles, datasets:[{label:"Role Probability (%)",data:probs,backgroundColor:colors}] },
        options:{ scales:{ y:{ beginAtZero:true,max:100 } } }
    })
}

// ---------- MEDIA RECORDER ----------
let mediaRecorder
let recordedChunks=[]
const preview=document.getElementById("preview")
const startBtn=document.getElementById("startRec")
const stopBtn=document.getElementById("stopRec")

async function setupCamera(){
    try{
        const stream = await navigator.mediaDevices.getUserMedia({video:true,audio:true})
        preview.srcObject = stream
        mediaRecorder = new MediaRecorder(stream)
        mediaRecorder.ondataavailable = e=>{
            if(e.data.size>0) recordedChunks.push(e.data)
        }
    }catch(err){
        console.error("Camera error:",err)
        alert("Camera or microphone access failed.")
    }
}
setupCamera()

startBtn.onclick=()=>{
    if(!mediaRecorder){ alert("Camera not ready yet."); return; }
    recordedChunks=[]
    mediaRecorder.start()
    startBtn.disabled=true
    stopBtn.disabled=false
}

stopBtn.onclick=()=>{
    mediaRecorder.stop()
    startBtn.disabled=false
    stopBtn.disabled=true
    mediaRecorder.onstop=async()=>{
        const blob=new Blob(recordedChunks,{type:"video/webm"})
        const file=new File([blob],"audition.webm",{type:"video/webm"})
        let show=document.getElementById("showSelect").value
        if(currentUser){ show=show+"|"+currentUser }
        const formData=new FormData()
        formData.append("file",file)
        formData.append("show",show)
        const response=await fetch("/analyze",{method:"POST",body:formData})
        const data=await response.json()
        showResults(data)
    }
}
