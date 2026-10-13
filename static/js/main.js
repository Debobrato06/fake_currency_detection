// =====================================================================
// Currency Guardian AI - Classic UI
// =====================================================================

const MAX_PHOTOS = 6;
const $ = (id) => document.getElementById(id);

// ---------------------------------------------------------------------
// i18n (English / Bangla)
// ---------------------------------------------------------------------
const I18N = {
    en: {
        statusChecking: 'Checking model…', statusReady: 'Model ready', statusError: 'Model not ready',
        proUi: 'Pro UI', heroTitle1: 'Is your Taka', heroTitle2: 'genuine?',
        heroSub: 'Upload close photos of a Tk 500 or Tk 1000 note. The AI checks print texture and security features in seconds.',
        step1: 'Add photos', step2: 'Analyze', step3: 'Result',
        dropTitle: 'Drop photos here', dropSub: 'or click to browse · paste with Ctrl+V · up to 6 photos of the SAME note',
        browse: 'Browse', camera: 'Camera', trayTitle: 'Selected photos', clearAll: 'Clear all',
        trayHint: 'Tip: front (portrait side), back and the note held against light give the most reliable result.',
        thresholdLabel: 'Required confidence for GENUINE', analyze: 'Analyze note',
        load1: 'Uploading photos', load2: 'Checking it is a Tk 500 / 1000 note', load3: 'Analyzing print texture with AI', load4: 'Building explanation heatmap',
        pReal: 'chance it is real', thresholdLive: 'Strictness (updates the verdict live)',
        confidence: 'Confidence', photosUsed: 'Photos used',
        modeHeat: 'AI focus', modeCompare: 'Compare', modeEdges: 'Edges', modeOriginal: 'Original',
        heatHint: 'Red = regions that influenced the AI most', report: 'Print report', newScan: 'Scan another note',
        history: 'Recent scans', historyEmpty: 'No scans yet. Results are kept only in this browser.',
        f1t: 'Trained on real notes', f1d: 'EfficientNet model trained on 1,390 genuine and counterfeit Taka notes (JaalTaka).',
        f2t: 'Explainable', f2d: 'The heatmap shows which regions of the note drove the decision.',
        f3t: 'Safe rejection', f3d: 'Photos that are not a Tk 500 / Tk 1000 note are rejected instead of guessed.',
        cameraTitle: 'Take a photo', cameraHint: 'Fill the frame with the note, avoid glare. Take several shots: front, back, against light.',
        switchCam: 'Switch camera', capture: 'Capture',
        tipsTitle: 'How to photograph a note',
        tip1: 'Get close: the note should fill most of the photo.', tip2: 'Front side: portrait and the security thread.',
        tip3: 'Back side of the note.', tip4: 'Hold the note against light to show the watermark.',
        tip5: 'Avoid glare, blur and scanned images.', tip6: 'This is decision support. Confirm suspicious notes at a bank.',
        footer: '© 2026 AI Currency Guardian · Decision support only. Confirm suspicious notes at a bank.',
        // dynamic
        GENUINE: 'GENUINE', COUNTERFEIT: 'COUNTERFEIT', UNCERTAIN: 'UNCERTAIN', NOT_SUPPORTED: 'NOT SUPPORTED',
        msgGENUINE: 'The note looks genuine.',
        msgCOUNTERFEIT: 'The note looks COUNTERFEIT. Do not accept it; verify at a bank.',
        msgUNCERTAIN: 'The AI is not sure. Check the watermark, security thread and raised print by hand, or add more photos.',
        msgNOT_SUPPORTED: 'This does not look like a Tk 500 / Tk 1000 note photo. Upload a clear, close photo of the note.',
        viewHints: ['Front · portrait', 'Front · centre', 'Front · right', 'Watermark area', 'Back side', 'Against light'],
        photo: 'Photo', real: 'REAL', fake: 'FAKE', ignored: 'IGNORED',
        ignoredTip: 'Does not look like a Tk 500 / Tk 1000 note, ignored',
        tooMany: 'Only 6 photos per note. Extra photos were skipped.', notImage: 'Please choose image files.',
        added: (n) => `${n} photo${n > 1 ? 's' : ''} added`, pasted: 'Photo pasted from clipboard',
        noCamera: 'Camera not available. Opening file picker instead.', serverDown: 'Could not connect to the server.',
        captured: 'Photo captured', historyCleared: 'History cleared',
    },
    bn: {
        statusChecking: 'মডেল যাচাই হচ্ছে…', statusReady: 'মডেল প্রস্তুত', statusError: 'মডেল প্রস্তুত নয়',
        proUi: 'প্রো UI', heroTitle1: 'আপনার টাকা কি', heroTitle2: 'আসল?',
        heroSub: '৫০০ বা ১০০০ টাকার নোটের কাছ থেকে তোলা ছবি দিন। AI কয়েক সেকেন্ডে ছাপা ও নিরাপত্তা বৈশিষ্ট্য যাচাই করবে।',
        step1: 'ছবি দিন', step2: 'বিশ্লেষণ', step3: 'ফলাফল',
        dropTitle: 'এখানে ছবি ছাড়ুন', dropSub: 'অথবা ক্লিক করে বাছাই করুন · Ctrl+V দিয়ে পেস্ট · একই নোটের সর্বোচ্চ ৬টি ছবি',
        browse: 'ফাইল বাছাই', camera: 'ক্যামেরা', trayTitle: 'বাছাই করা ছবি', clearAll: 'সব মুছুন',
        trayHint: 'পরামর্শ: সামনের দিক (প্রতিকৃতি), পেছনের দিক এবং আলোর সামনে ধরা নোট দিলে ফল সবচেয়ে নির্ভরযোগ্য হয়।',
        thresholdLabel: '"আসল" বলার জন্য প্রয়োজনীয় আস্থা', analyze: 'নোট যাচাই করুন',
        load1: 'ছবি আপলোড হচ্ছে', load2: '৫০০ / ১০০০ টাকার নোট কিনা দেখা হচ্ছে', load3: 'AI দিয়ে ছাপা বিশ্লেষণ', load4: 'ব্যাখ্যা হিটম্যাপ তৈরি',
        pReal: 'আসল হওয়ার সম্ভাবনা', thresholdLive: 'কঠোরতা (সাথে সাথে ফল বদলায়)',
        confidence: 'আস্থা', photosUsed: 'ব্যবহৃত ছবি',
        modeHeat: 'AI ফোকাস', modeCompare: 'তুলনা', modeEdges: 'রেখা', modeOriginal: 'মূল ছবি',
        heatHint: 'লাল = যে অংশ AI-এর সিদ্ধান্তে সবচেয়ে বেশি প্রভাব ফেলেছে', report: 'রিপোর্ট প্রিন্ট', newScan: 'আরেকটি নোট যাচাই',
        history: 'সাম্প্রতিক যাচাই', historyEmpty: 'এখনো কোনো যাচাই নেই। ফলাফল শুধু এই ব্রাউজারে থাকে।',
        f1t: 'আসল নোটে প্রশিক্ষিত', f1d: '১,৩৯০টি আসল ও জাল টাকার নোটে (JaalTaka) প্রশিক্ষিত EfficientNet মডেল।',
        f2t: 'ব্যাখ্যাযোগ্য', f2d: 'হিটম্যাপ দেখায় নোটের কোন অংশ দেখে সিদ্ধান্ত নেওয়া হয়েছে।',
        f3t: 'নিরাপদ প্রত্যাখ্যান', f3d: '৫০০ / ১০০০ টাকার নোট না হলে অনুমান না করে বাতিল করা হয়।',
        cameraTitle: 'ছবি তুলুন', cameraHint: 'নোট দিয়ে ফ্রেম ভরে দিন, ঝলক এড়িয়ে চলুন। সামনে, পেছনে ও আলোর সামনে কয়েকটি ছবি তুলুন।',
        switchCam: 'ক্যামেরা বদলান', capture: 'ছবি তুলুন',
        tipsTitle: 'নোটের ছবি কীভাবে তুলবেন',
        tip1: 'কাছে যান: নোটটি ছবির বেশিরভাগ জুড়ে থাকবে।', tip2: 'সামনের দিক: প্রতিকৃতি ও নিরাপত্তা সুতা।',
        tip3: 'নোটের পেছনের দিক।', tip4: 'জলছাপ দেখাতে নোটটি আলোর সামনে ধরুন।',
        tip5: 'ঝলক, ঝাপসা ও স্ক্যান করা ছবি এড়িয়ে চলুন।', tip6: 'এটি সহায়ক টুল। সন্দেহজনক নোট ব্যাংকে যাচাই করুন।',
        footer: '© ২০২৬ AI Currency Guardian · শুধু সহায়ক সিদ্ধান্ত। সন্দেহজনক নোট ব্যাংকে যাচাই করুন।',
        GENUINE: 'আসল', COUNTERFEIT: 'জাল', UNCERTAIN: 'অনিশ্চিত', NOT_SUPPORTED: 'সমর্থিত নয়',
        msgGENUINE: 'নোটটি আসল মনে হচ্ছে।',
        msgCOUNTERFEIT: 'নোটটি জাল মনে হচ্ছে। গ্রহণ করবেন না; ব্যাংকে যাচাই করুন।',
        msgUNCERTAIN: 'AI নিশ্চিত নয়। জলছাপ, নিরাপত্তা সুতা ও উঁচু ছাপা হাতে যাচাই করুন, অথবা আরও ছবি দিন।',
        msgNOT_SUPPORTED: 'এটি ৫০০ / ১০০০ টাকার নোটের ছবি মনে হচ্ছে না। নোটের পরিষ্কার, কাছ থেকে তোলা ছবি দিন।',
        viewHints: ['সামনে · প্রতিকৃতি', 'সামনে · মাঝখান', 'সামনে · ডান', 'জলছাপ অংশ', 'পেছনের দিক', 'আলোর সামনে'],
        photo: 'ছবি', real: 'আসল', fake: 'জাল', ignored: 'বাদ',
        ignoredTip: '৫০০ / ১০০০ টাকার নোট মনে হয়নি, বাদ দেওয়া হয়েছে',
        tooMany: 'একটি নোটের জন্য সর্বোচ্চ ৬টি ছবি। বাকিগুলো বাদ দেওয়া হয়েছে।', notImage: 'অনুগ্রহ করে ছবি ফাইল দিন।',
        added: (n) => `${n}টি ছবি যোগ হয়েছে`, pasted: 'ক্লিপবোর্ড থেকে ছবি যোগ হয়েছে',
        noCamera: 'ক্যামেরা পাওয়া যায়নি। ফাইল বাছাই খোলা হচ্ছে।', serverDown: 'সার্ভারের সাথে সংযোগ করা যায়নি।',
        captured: 'ছবি তোলা হয়েছে', historyCleared: 'ইতিহাস মুছে ফেলা হয়েছে',
    },
};

const store = {
    get(k, d) { try { const v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch { return d; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch { /* storage unavailable */ } },
};

let lang = store.get('cg_lang', 'en');
const t = (key) => (I18N[lang] && I18N[lang][key] !== undefined ? I18N[lang][key] : I18N.en[key]);

function applyLang() {
    document.documentElement.lang = lang;
    document.body.classList.toggle('lang-bn', lang === 'bn');
    document.querySelectorAll('[data-i18n]').forEach((el) => { el.textContent = t(el.dataset.i18n); });
    $('lang-label').textContent = lang === 'en' ? 'বাং' : 'EN';
    renderTray();
    if (state.result) renderResult(false);
    renderHistory();
    refreshStatusText();
}

// ---------------------------------------------------------------------
// State
// ---------------------------------------------------------------------
const state = {
    photos: [],          // { file, url }
    result: null,        // server response
    selected: 0,
    mode: 'heatmap',
    lens: false,
    status: null,
};

// ---------------------------------------------------------------------
// Toasts
// ---------------------------------------------------------------------
function toast(msg, type = 'info', ms = 3200) {
    const el = document.createElement('div');
    el.className = `toast ${type}`;
    el.textContent = msg;
    $('toasts').appendChild(el);
    setTimeout(() => { el.style.opacity = '0'; el.style.transition = 'opacity .3s'; }, ms);
    setTimeout(() => el.remove(), ms + 350);
}

// ---------------------------------------------------------------------
// Theme
// ---------------------------------------------------------------------
document.body.className = store.get('cg_theme', 'dark-theme');
$('theme-toggle').addEventListener('click', () => {
    const next = document.body.classList.contains('dark-theme') ? 'light-theme' : 'dark-theme';
    document.body.classList.remove('dark-theme', 'light-theme');
    document.body.classList.add(next);
    store.set('cg_theme', next);
});
$('lang-toggle').addEventListener('click', () => {
    lang = lang === 'en' ? 'bn' : 'en';
    store.set('cg_lang', lang);
    applyLang();
});

// ---------------------------------------------------------------------
// Model status
// ---------------------------------------------------------------------
function refreshStatusText() {
    const el = $('model-status');
    const label = el.querySelector('span');
    if (!state.status) { label.textContent = t('statusChecking'); return; }
    if (state.status.ready) {
        const m = (state.status.metrics || {}).test_per_note_6_views;
        el.className = 'status-badge ok';
        label.textContent = t('statusReady') + (m ? ` · ${(m.accuracy * 100).toFixed(1)}%` : '');
        el.title = m ? `Held-out test accuracy ${(m.accuracy * 100).toFixed(1)}% · counterfeit detection ${(m.fake_detection_rate * 100).toFixed(1)}%` : '';
    } else {
        el.className = 'status-badge err';
        label.textContent = t('statusError');
        el.title = state.status.error || '';
    }
}

fetch('/status').then((r) => r.json()).then((s) => {
    state.status = s;
    refreshStatusText();
    if (!s.ready) toast(s.error, 'error', 8000);
}).catch(() => { state.status = { ready: false, error: t('serverDown') }; refreshStatusText(); });

// ---------------------------------------------------------------------
// Steps indicator
// ---------------------------------------------------------------------
function setStep(n) {
    document.querySelectorAll('#steps li').forEach((li) => {
        const s = Number(li.dataset.step);
        li.classList.toggle('active', s === n);
        li.classList.toggle('done', s < n);
    });
}

// ---------------------------------------------------------------------
// Adding photos: browse / drag & drop / paste / camera
// ---------------------------------------------------------------------
const dropZone = $('drop-zone');
const fileInput = $('file-input');

function addFiles(fileList, source) {
    const files = Array.from(fileList).filter((f) => f.type.startsWith('image/'));
    if (!files.length) { toast(t('notImage'), 'warn'); return; }
    let added = 0;
    for (const f of files) {
        if (state.photos.length >= MAX_PHOTOS) { toast(t('tooMany'), 'warn'); break; }
        if (state.photos.some((p) => p.file.name === f.name && p.file.size === f.size && f.name !== 'image.png')) continue;
        state.photos.push({ file: f, url: URL.createObjectURL(f) });
        added++;
    }
    if (added) toast(source === 'paste' ? t('pasted') : source === 'camera' ? t('captured') : t('added')(added));
    renderTray();
}

function removePhoto(i) {
    URL.revokeObjectURL(state.photos[i].url);
    state.photos.splice(i, 1);
    renderTray();
}

function clearPhotos() {
    state.photos.forEach((p) => URL.revokeObjectURL(p.url));
    state.photos = [];
    renderTray();
}

function renderTray() {
    const tray = $('tray');
    tray.innerHTML = '';
    const hints = t('viewHints');
    for (let i = 0; i < MAX_PHOTOS; i++) {
        const slot = document.createElement('div');
        const p = state.photos[i];
        if (p) {
            slot.className = 'slot filled';
            slot.innerHTML = `<img src="${p.url}" alt=""><span class="num">${i + 1}</span>
                <button class="rm" title="Remove" aria-label="Remove photo ${i + 1}"><i class="fas fa-xmark"></i></button>`;
            slot.querySelector('.rm').addEventListener('click', (e) => { e.stopPropagation(); removePhoto(i); });
        } else {
            slot.className = 'slot';
            slot.innerHTML = `<i class="fas fa-plus"></i><span>${hints[i]}</span>`;
            slot.addEventListener('click', () => fileInput.click());
        }
        tray.appendChild(slot);
    }
    $('tray-count').textContent = `${state.photos.length}/${MAX_PHOTOS}`;
    $('analyze-btn').disabled = state.photos.length === 0;
    $('clear-btn').classList.toggle('hidden', state.photos.length === 0);
}

dropZone.addEventListener('click', (e) => { if (!e.target.closest('button')) fileInput.click(); });
dropZone.addEventListener('keydown', (e) => { if (e.key === ' ') { e.preventDefault(); fileInput.click(); } });
$('browse-btn').addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', (e) => { addFiles(e.target.files); fileInput.value = ''; });

['dragenter', 'dragover'].forEach((ev) => dropZone.addEventListener(ev, (e) => { e.preventDefault(); dropZone.classList.add('drag-over'); }));
['dragleave', 'drop'].forEach((ev) => dropZone.addEventListener(ev, (e) => { e.preventDefault(); dropZone.classList.remove('drag-over'); }));
dropZone.addEventListener('drop', (e) => addFiles(e.dataTransfer.files));

document.addEventListener('paste', (e) => {
    if ($('input-panel').classList.contains('hidden')) return;
    const imgs = Array.from(e.clipboardData.items).filter((it) => it.type.startsWith('image/')).map((it) => it.getAsFile());
    if (imgs.length) addFiles(imgs, 'paste');
});
$('clear-btn').addEventListener('click', clearPhotos);

// Camera
let camStream = null;
let camFacing = 'environment';

async function openCamera() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        toast(t('noCamera'), 'warn');
        fileInput.setAttribute('capture', 'environment');
        fileInput.click();
        fileInput.removeAttribute('capture');
        return;
    }
    try {
        camStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: camFacing, width: { ideal: 1920 } }, audio: false });
        $('camera-video').srcObject = camStream;
        openModal('camera-modal');
    } catch (err) {
        toast(t('noCamera'), 'warn');
        fileInput.click();
    }
}

function stopCamera() {
    if (camStream) camStream.getTracks().forEach((tr) => tr.stop());
    camStream = null;
}

$('camera-btn').addEventListener('click', openCamera);
$('camera-switch').addEventListener('click', async () => {
    camFacing = camFacing === 'environment' ? 'user' : 'environment';
    stopCamera();
    closeModal('camera-modal');
    await openCamera();
});
$('camera-shot').addEventListener('click', () => {
    const video = $('camera-video');
    if (!video.videoWidth) return;
    const c = document.createElement('canvas');
    c.width = video.videoWidth;
    c.height = video.videoHeight;
    c.getContext('2d').drawImage(video, 0, 0);
    video.parentElement.classList.remove('camera-flash');
    void video.parentElement.offsetWidth;
    video.parentElement.classList.add('camera-flash');
    c.toBlob((blob) => {
        addFiles([new File([blob], `camera_${Date.now()}.jpg`, { type: 'image/jpeg' })], 'camera');
        if (state.photos.length >= MAX_PHOTOS) closeModal('camera-modal');
    }, 'image/jpeg', 0.92);
});

// ---------------------------------------------------------------------
// Modals
// ---------------------------------------------------------------------
function openModal(id) { $(id).classList.remove('hidden'); }
function closeModal(id) {
    $(id).classList.add('hidden');
    if (id === 'camera-modal') stopCamera();
}
document.querySelectorAll('.modal').forEach((m) => {
    m.addEventListener('click', (e) => { if (e.target === m || e.target.closest('[data-close]')) closeModal(m.id); });
});
$('tips-btn').addEventListener('click', () => openModal('tips-modal'));

// ---------------------------------------------------------------------
// Threshold sliders (kept in sync; result verdict updates live)
// ---------------------------------------------------------------------
const thr1 = $('threshold');
const thr2 = $('threshold2');
function setThreshold(v, from) {
    thr1.value = v; thr2.value = v;
    $('threshold-val').textContent = v + '%';
    $('threshold2-val').textContent = v + '%';
    store.set('cg_threshold', Number(v));
    if (from === 'live' && state.result) renderResult(false);
}
thr1.addEventListener('input', () => setThreshold(thr1.value));
thr2.addEventListener('input', () => setThreshold(thr2.value, 'live'));
setThreshold(store.get('cg_threshold', 70));

// ---------------------------------------------------------------------
// Analyze
// ---------------------------------------------------------------------
let loadingTimers = [];

function showLoading() {
    $('input-panel').classList.add('hidden');
    $('loading-panel').classList.remove('hidden');
    $('loading-img').src = state.photos[0].url;
    setStep(2);
    const items = Array.from(document.querySelectorAll('#loading-steps li'));
    items.forEach((li) => li.classList.remove('active', 'done'));
    const bar = $('progress-bar');
    bar.style.width = '5%';
    const stages = [0, 500, 1200, 2400];
    const n = state.photos.length;
    stages.forEach((ms, i) => {
        loadingTimers.push(setTimeout(() => {
            items.forEach((li, j) => { li.classList.toggle('done', j < i); li.classList.toggle('active', j === i); });
            bar.style.width = `${15 + i * 22}%`;
        }, ms * Math.max(1, n / 2)));
    });
}

function hideLoading() {
    loadingTimers.forEach(clearTimeout);
    loadingTimers = [];
    document.querySelectorAll('#loading-steps li').forEach((li) => { li.classList.remove('active'); li.classList.add('done'); });
    $('progress-bar').style.width = '100%';
}

async function analyze() {
    if (!state.photos.length) return;
    showLoading();
    const fd = new FormData();
    state.photos.forEach((p) => fd.append('file', p.file));
    fd.append('threshold', (thr1.value / 100).toString());
    try {
        const res = await fetch('/analyze', { method: 'POST', body: fd });
        const data = await res.json();
        hideLoading();
        if (!res.ok) throw new Error(data.error || 'Analysis failed');
        state.result = data;
        state.selected = Math.max(0, data.per_image.findIndex((p) => p.in_distribution));
        setTimeout(() => { renderResult(true); addHistory(); }, 250);
    } catch (err) {
        hideLoading();
        $('loading-panel').classList.add('hidden');
        $('input-panel').classList.remove('hidden');
        setStep(1);
        toast(err.message === 'Failed to fetch' ? t('serverDown') : err.message, 'error', 6000);
    }
}
$('analyze-btn').addEventListener('click', analyze);

// ---------------------------------------------------------------------
// Verdict logic (mirrors detector.summarize, so the threshold can change live)
// ---------------------------------------------------------------------
function decide(result, thr) {
    const usable = result.per_image.filter((p) => p.in_distribution);
    if (!usable.length) return { verdict: 'NOT_SUPPORTED', p: null, conf: null, used: 0 };
    const p = usable.reduce((s, x) => s + x.real_probability, 0) / usable.length;
    const verdict = p >= thr ? 'GENUINE' : p < 0.5 ? 'COUNTERFEIT' : 'UNCERTAIN';
    return { verdict, p, conf: 100 * (p >= 0.5 ? p : 1 - p), used: usable.length };
}

const VERDICT_UI = {
    GENUINE: { cls: 'real', icon: 'fa-circle-check' },
    COUNTERFEIT: { cls: 'fake', icon: 'fa-triangle-exclamation' },
    UNCERTAIN: { cls: 'uncertain', icon: 'fa-circle-question' },
    NOT_SUPPORTED: { cls: 'unsupported', icon: 'fa-ban' },
};

// gauge geometry: p in [0,1] -> point on a semicircle (left = 0, right = 1)
function gPoint(p) {
    const a = Math.PI * p;
    return [100 - 80 * Math.cos(a), 100 - 80 * Math.sin(a)];
}
function gArc(p0, p1) {
    const [x0, y0] = gPoint(p0);
    const [x1, y1] = gPoint(p1);
    return `M${x0.toFixed(2)} ${y0.toFixed(2)} A80 80 0 0 1 ${x1.toFixed(2)} ${y1.toFixed(2)}`;
}

function animateNumber(el, to, suffix = '%', ms = 900) {
    const from = parseFloat(el.dataset.v || '0');
    const start = performance.now();
    el.dataset.v = to;
    function frame(now) {
        const k = Math.min(1, (now - start) / ms);
        const e = 1 - Math.pow(1 - k, 3);
        el.textContent = (from + (to - from) * e).toFixed(1) + suffix;
        if (k < 1) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
}

function renderResult(first) {
    const r = state.result;
    const thr = thr2.value / 100;
    const d = decide(r, thr);
    const ui = VERDICT_UI[d.verdict];

    $('loading-panel').classList.add('hidden');
    $('input-panel').classList.add('hidden');
    $('results-panel').classList.remove('hidden');
    setStep(3);

    const badge = $('main-status');
    const newHtml = `<i class="fas ${ui.icon}"></i> <span>${t(d.verdict)}</span>`;
    if (badge.innerHTML !== newHtml) {
        badge.innerHTML = newHtml;
        badge.className = 'result-badge ' + ui.cls;
        badge.style.animation = 'none'; void badge.offsetWidth; badge.style.animation = '';
    }
    $('verdict-card').className = 'glass verdict-card ' + ui.cls;
    $('verdict-message').textContent = t('msg' + d.verdict);

    // gauge
    $('g-unsure').setAttribute('d', gArc(0.5, thr));
    $('g-real').setAttribute('d', gArc(thr, 1));
    $('g-thr').style.transform = `rotate(${thr * 180 - 90}deg)`;
    const needle = $('g-needle');
    needle.style.opacity = d.p === null ? '0.25' : '1';
    if (first) { needle.style.transition = 'none'; needle.style.transform = 'rotate(-90deg)'; void needle.getBoundingClientRect(); needle.style.transition = ''; }
    needle.style.transform = `rotate(${((d.p ?? 0.5) * 180 - 90)}deg)`;

    const pEl = $('p-real-val');
    if (d.p === null) { pEl.textContent = '–'; pEl.dataset.v = '0'; } else if (first) { pEl.dataset.v = '0'; animateNumber(pEl, d.p * 100); } else { pEl.textContent = (d.p * 100).toFixed(1) + '%'; }
    $('confidence-val').textContent = d.conf === null ? '–' : d.conf.toFixed(1) + '%';
    $('photos-used').textContent = `${d.used}/${r.per_image.length}`;

    renderStrip(first);
    renderViewer();
}

function renderStrip(animate) {
    const strip = $('photo-strip');
    strip.innerHTML = '';
    state.result.per_image.forEach((p, i) => {
        const card = document.createElement('button');
        card.className = 'photo-card' + (i === state.selected ? ' active' : '');
        let status, cls;
        if (!p.in_distribution) { status = t('ignored'); cls = 'status-warn'; } else if (p.real_probability >= 0.5) { status = t('real'); cls = 'status-pass'; } else { status = t('fake'); cls = 'status-fail'; }
        const pct = (p.real_probability * 100).toFixed(0);
        card.title = p.in_distribution ? `P(real) ${pct}%` : t('ignoredTip');
        card.innerHTML = `<img src="data:image/jpeg;base64,${p.visuals.original}" alt="">
            <div class="pc-body">
                <div class="pc-top"><span>${t('photo')} ${i + 1}</span><span class="feature-status ${cls}">${status}</span></div>
                <div class="bar"><i style="width:${animate ? 0 : pct}%"></i></div>
            </div>`;
        card.addEventListener('click', () => { state.selected = i; renderStrip(false); renderViewer(); });
        strip.appendChild(card);
        if (animate) requestAnimationFrame(() => requestAnimationFrame(() => { card.querySelector('.bar i').style.width = pct + '%'; }));
    });
}

// ---------------------------------------------------------------------
// Inspector: modes, heatmap opacity, compare slider, magnifier, fullscreen
// ---------------------------------------------------------------------
const viewer = $('viewer');
const vBase = $('v-base');
const vLayer = $('v-layer');
const handle = $('compare-handle');
let comparePos = 50;

function src(key) { return 'data:image/jpeg;base64,' + state.result.per_image[state.selected].visuals[key]; }

function renderViewer() {
    if (!state.result) return;
    const m = state.mode;
    document.querySelectorAll('#view-modes button').forEach((b) => b.classList.toggle('active', b.dataset.mode === m));
    vBase.src = src(m === 'edges' ? 'edges' : 'original');
    vLayer.classList.toggle('hidden', !(m === 'heatmap' || m === 'compare'));
    handle.classList.toggle('hidden', m !== 'compare');
    $('opacity-row').classList.toggle('hidden', m !== 'heatmap');
    if (m === 'heatmap') {
        vLayer.src = src('heatmap');
        vLayer.style.opacity = $('opacity').value / 100;
        vLayer.style.clipPath = 'none';
    } else if (m === 'compare') {
        vLayer.src = src('gradcam');
        vLayer.style.opacity = 1;
        setCompare(comparePos);
    }
}

document.querySelectorAll('#view-modes button').forEach((b) => b.addEventListener('click', () => { state.mode = b.dataset.mode; renderViewer(); }));
$('opacity').addEventListener('input', (e) => { vLayer.style.opacity = e.target.value / 100; });

function setCompare(pct) {
    comparePos = Math.max(0, Math.min(100, pct));
    vLayer.style.clipPath = `inset(0 0 0 ${comparePos}%)`;
    handle.style.left = comparePos + '%';
}

let draggingCompare = false;
viewer.addEventListener('pointerdown', (e) => {
    if (state.mode !== 'compare') return;
    draggingCompare = true;
    viewer.setPointerCapture(e.pointerId);
    moveCompare(e);
});
viewer.addEventListener('pointerup', () => { draggingCompare = false; });
function moveCompare(e) {
    const r = viewer.getBoundingClientRect();
    setCompare(((e.clientX - r.left) / r.width) * 100);
}

// Magnifier: works on the visible image content (accounts for letterboxing)
const lens = $('lens');
const ZOOM = 3;
function contentRect() {
    const r = vBase.getBoundingClientRect();
    const ir = vBase.naturalWidth / vBase.naturalHeight;
    const br = r.width / r.height;
    let w = r.width, h = r.height;
    if (ir > br) h = w / ir; else w = h * ir;
    return { left: r.left + (r.width - w) / 2, top: r.top + (r.height - h) / 2, width: w, height: h };
}
viewer.addEventListener('pointermove', (e) => {
    if (draggingCompare) { moveCompare(e); return; }
    if (!state.lens || !vBase.naturalWidth) return;
    const c = contentRect();
    const x = e.clientX - c.left, y = e.clientY - c.top;
    if (x < 0 || y < 0 || x > c.width || y > c.height) { lens.classList.add('hidden'); return; }
    const vr = viewer.getBoundingClientRect();
    lens.classList.remove('hidden');
    lens.style.left = (e.clientX - vr.left) + 'px';
    lens.style.top = (e.clientY - vr.top) + 'px';
    // always magnify the photo itself (edges map in Edges mode) so print detail is visible
    lens.style.backgroundImage = `url(${vBase.src})`;
    lens.style.backgroundSize = `${c.width * ZOOM}px ${c.height * ZOOM}px`;
    lens.style.backgroundPosition = `${-(x * ZOOM - 80)}px ${-(y * ZOOM - 80)}px`;
});
viewer.addEventListener('pointerleave', () => lens.classList.add('hidden'));
$('lens-btn').addEventListener('click', () => {
    state.lens = !state.lens;
    $('lens-btn').classList.toggle('active', state.lens);
    viewer.style.cursor = state.lens ? 'none' : '';
    if (!state.lens) lens.classList.add('hidden');
});
$('fullscreen-btn').addEventListener('click', () => viewer.classList.toggle('fullscreen'));

// ---------------------------------------------------------------------
// History (kept in this browser only)
// ---------------------------------------------------------------------
function thumbFromUrl(url) {
    return new Promise((resolve) => {
        const img = new Image();
        img.onload = () => {
            const c = document.createElement('canvas');
            const s = 96 / Math.max(img.width, img.height);
            c.width = Math.round(img.width * s); c.height = Math.round(img.height * s);
            c.getContext('2d').drawImage(img, 0, 0, c.width, c.height);
            resolve(c.toDataURL('image/jpeg', 0.7));
        };
        img.onerror = () => resolve('');
        img.src = url;
    });
}

async function addHistory() {
    const d = decide(state.result, thr2.value / 100);
    const thumb = await thumbFromUrl(src('original'));
    const list = store.get('cg_history', []);
    list.unshift({ verdict: d.verdict, p: d.p, n: state.result.per_image.length, time: Date.now(), thumb });
    store.set('cg_history', list.slice(0, 8));
    renderHistory();
}

function renderHistory() {
    const list = store.get('cg_history', []);
    const el = $('history-list');
    el.innerHTML = '';
    $('history-empty').classList.toggle('hidden', list.length > 0);
    $('history-clear').classList.toggle('hidden', list.length === 0);
    list.forEach((h) => {
        const item = document.createElement('div');
        item.className = 'h-item ' + VERDICT_UI[h.verdict].cls;
        const when = new Date(h.time).toLocaleString(lang === 'bn' ? 'bn-BD' : undefined, { dateStyle: 'short', timeStyle: 'short' });
        item.innerHTML = `${h.thumb ? `<img src="${h.thumb}" alt="">` : ''}
            <div><b>${t(h.verdict)}${h.p === null ? '' : ` · ${(h.p * 100).toFixed(0)}%`}</b>
            <small>${when} · ${h.n} ${t('photo')}</small></div>`;
        el.appendChild(item);
    });
}
$('history-clear').addEventListener('click', () => { store.set('cg_history', []); renderHistory(); toast(t('historyCleared')); });

// ---------------------------------------------------------------------
// Reset, report, keyboard shortcuts
// ---------------------------------------------------------------------
function newScan() {
    viewer.classList.remove('fullscreen');
    state.result = null;
    clearPhotos();
    $('results-panel').classList.add('hidden');
    $('input-panel').classList.remove('hidden');
    setStep(1);
    window.scrollTo({ top: 0, behavior: 'smooth' });
}
$('new-scan-btn').addEventListener('click', newScan);
$('report-btn').addEventListener('click', () => window.print());

document.addEventListener('keydown', (e) => {
    const openModalEl = document.querySelector('.modal:not(.hidden)');
    if (e.key === 'Escape') {
        if (openModalEl) { closeModal(openModalEl.id); return; }
        if (viewer.classList.contains('fullscreen')) { viewer.classList.remove('fullscreen'); return; }
        if (state.result) newScan();
        return;
    }
    if (openModalEl) {
        if (e.key === 'Enter' && openModalEl.id === 'camera-modal') $('camera-shot').click();
        return;
    }
    if (e.key === 'Enter' && !$('input-panel').classList.contains('hidden') && state.photos.length
        && document.activeElement.tagName !== 'BUTTON') {
        e.preventDefault();
        analyze();
    }
});

applyLang();
