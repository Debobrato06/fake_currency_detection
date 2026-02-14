const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const scanner = document.getElementById('scanner');
const resultsPanel = document.getElementById('results-panel');
const origPreview = document.getElementById('orig-preview');
const featureList = document.getElementById('feature-list');
const mainStatus = document.getElementById('main-status');
const confidenceVal = document.getElementById('confidence-val');

// Visual Analysis Elements
const edgeImg = document.getElementById('edge-img');
const houghImg = document.getElementById('hough-img');
const faceImg = document.getElementById('face-img');
const ocrContent = document.getElementById('ocr-content');

// --- Drag and Drop Logic ---

dropZone.addEventListener('click', () => fileInput.click());

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('drag-over');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('drag-over');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    const files = e.dataTransfer.files;
    if (files.length) handleFileUpload(files[0]);
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length) handleFileUpload(e.target.files[0]);
});

// --- API Communication ---

async function handleFileUpload(file) {
    if (!file.type.startsWith('image/')) {
        alert('Please upload an image file.');
        return;
    }

    // Show scanning animation
    scanner.classList.remove('hidden');
    dropZone.classList.add('scanning');

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            displayResults(data);
        } else {
            alert(data.error || 'Something went wrong during analysis.');
            resetUI();
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Could not connect to the server.');
        resetUI();
    } finally {
        scanner.classList.add('hidden');
        dropZone.classList.remove('scanning');
    }
}

// --- UI Updates ---

function displayResults(data) {
    // Hide upload zone
    dropZone.classList.add('hidden');
    resultsPanel.classList.remove('hidden');

    // Set Status
    if (data.is_real) {
        mainStatus.innerHTML = '<i class="fas fa-check-circle"></i> <span>GENUINE</span>';
        mainStatus.className = 'result-badge real';
    } else {
        mainStatus.innerHTML = '<i class="fas fa-exclamation-triangle"></i> <span>SUSPICIOUS</span>';
        mainStatus.className = 'result-badge fake';
    }

    // Set Confidence
    confidenceVal.innerText = data.confidence.toFixed(1) + '%';

    // Set Images
    origPreview.src = 'data:image/jpeg;base64,' + data.visuals.original;
    edgeImg.src = 'data:image/jpeg;base64,' + data.visuals.edges;
    houghImg.src = 'data:image/jpeg;base64,' + data.visuals.hough;
    faceImg.src = 'data:image/jpeg;base64,' + data.visuals.faces;
    ocrContent.innerText = data.ocr_text || 'No text detected';

    // Populate Features
    featureList.innerHTML = '';
    data.features.forEach(feat => {
        const row = document.createElement('div');
        row.className = 'feature-item-row';
        row.innerHTML = `
            <span>${feat.name}</span>
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 0.8rem; color: #94a3b8;">${feat.val}</span>
                <span class="feature-status ${feat.status === 'PASS' ? 'status-pass' : 'status-fail'}">${feat.status}</span>
            </div>
        `;
        featureList.appendChild(row);
    });
}

function resetUI() {
    resultsPanel.classList.add('hidden');
    dropZone.classList.remove('hidden');
    fileInput.value = '';
}

// --- Tab Logic ---

document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        // Remove active from all
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));

        // Add to clicked
        btn.classList.add('active');
        const tabId = btn.getAttribute('data-tab');
        document.getElementById(tabId + '-pane').classList.add('active');
    });
});
// --- Theme Logic ---
const themeToggle = document.getElementById('theme-toggle');
const body = document.body;

// Check for saved theme
const savedTheme = localStorage.getItem('theme') || 'dark-theme';
body.className = savedTheme;

themeToggle.addEventListener('click', () => {
    if (body.classList.contains('dark-theme')) {
        body.classList.remove('dark-theme');
        body.classList.add('light-theme');
        localStorage.setItem('theme', 'light-theme');
    } else {
        body.classList.remove('light-theme');
        body.classList.add('dark-theme');
        localStorage.setItem('theme', 'dark-theme');
    }
});
