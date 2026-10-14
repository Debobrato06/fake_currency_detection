// =====================================================================
// Currency Guardian AI - Classic UI
// =====================================================================

const MAX_PHOTOS = 6;
const $ = (id) => document.getElementById(id);
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

// ---------------------------------------------------------------------
// i18n (English / Bangla)
// ---------------------------------------------------------------------
const I18N = {
    en: {
        statusChecking: 'Checking model…', statusReady: 'Model ready', statusError: 'Model not ready',
        proUi: 'Pro UI', eyebrow: 'Explainable AI · Tk 500 & Tk 1000', heroTitle1: 'Is your Taka', heroTitle2: 'genuine?',
        heroSub: 'Upload close photos of a Tk 500 or Tk 1000 note. The AI checks print texture and security features in seconds.',
        hsAcc: 'test accuracy', hsFdr: 'fakes caught', hsPhotos: 'photos per note',
        step1: 'Add photos', step2: 'Analyze', step3: 'Result',
        dropTitle: 'Drop photos here', dropSub: 'or click to browse · paste with Ctrl+V · up to 6 photos of the SAME note',
        browse: 'Browse', camera: 'Camera', trayTitle: 'Selected photos', clearAll: 'Clear all',
        trayHint: 'Tip: front (portrait side), back and the note held against light give the most reliable result. Drag to reorder, click to preview.',
        coverage: (n) => n === 0 ? 'No photos yet' : n < 3 ? 'Add more views for a reliable result' : n < 6 ? 'Good coverage' : 'Maximum coverage',
        thresholdLabel: 'Required confidence for GENUINE', analyze: 'Analyze note',
        pLenient: 'Lenient', pBalanced: 'Balanced', pStrict: 'Strict',
        loadingTitle: 'Authenticating note…',
        load1: 'Uploading photos', load2: 'Checking it is a Tk 500 / 1000 note', load3: 'Analyzing print texture with AI', load4: 'Building explanation heatmap',
        pReal: 'chance it is real', thresholdLive: 'Strictness (updates the verdict live)',
        consensus: 'Per-photo agreement', spread: (v) => `spread ±${v}%`,
        confidence: 'Confidence', photosUsed: 'Photos used',
        modeHeat: 'AI focus', modeCompare: 'Compare', modeEdges: 'Edges', modeOriginal: 'Original', low: 'Low', high: 'High',
        heatHint: 'Red = regions that influenced the AI most · scroll to zoom, drag to pan',
        copy: 'Copy summary', download: 'Download report', report: 'Print report', newScan: 'Scan another note',
        history: 'Recent scans', historyEmpty: 'No scans yet. Results are kept only in this browser.',
        modelTitle: 'AI model', details: 'Details', kAcc: 'Accuracy', kFdr: 'Fakes caught',
        modelNotes: (n) => `Held-out test set: ${n} notes, 6 photos each`,
        howTitle: 'How it works',
        f1t: 'Trained on real notes', f1d: 'EfficientNet model trained on 1,390 genuine and counterfeit Taka notes (JaalTaka).',
        f2t: 'Explainable', f2d: 'The heatmap shows which regions of the note drove the decision.',
        f3t: 'Safe rejection', f3d: 'Photos that are not a Tk 500 / Tk 1000 note are rejected instead of guessed.',
        cameraTitle: 'Take a photo', cameraHint: 'Fill the frame with the note, avoid glare. Take several shots: front, back, against light.',
        switchCam: 'Switch camera', capture: 'Capture', done: 'Done',
        tipsTitle: 'How to photograph a note',
        tip1: 'Get close: the note should fill most of the photo.', tip2: 'Front side: portrait and the security thread.',
        tip3: 'Back side of the note.', tip4: 'Hold the note against light to show the watermark.',
        tip5: 'Avoid glare, blur and scanned images.', tip6: 'This is decision support. Confirm suspicious notes at a bank.',
        keysTitle: 'Keyboard shortcuts', kPaste: 'Paste a photo', kEnter: 'Analyze / capture', kArrows: 'Previous / next photo',
        kModes: 'Switch view mode', kZoom: 'Zoom in / out / reset', kLens: 'Magnifier', kFull: 'Fullscreen viewer',
        kTheme: 'Light / dark theme', kEsc: 'Close / new scan',
        footer: '© 2026 AI Currency Guardian · Decision support only. Confirm suspicious notes at a bank.',
        // model modal
        splits: { test_per_note_6_views: 'Test · per note', test_per_photo: 'Test · per photo', val_per_photo: 'Validation',
            diagnostic_center_hidden: 'Stress · centre hidden', diagnostic_border_hidden: 'Stress · border hidden' },
        mAcc: 'Accuracy', mAuc: 'ROC AUC', mFdr: 'Counterfeits detected', mRar: 'Genuine accepted',
        cmTitle: 'Confusion matrix', actual: 'Actual', predicted: 'Predicted', realL: 'Real', fakeL: 'Fake',
        samples: (n) => `${n} samples`, dataset: 'Dataset',
        // dynamic
        GENUINE: 'GENUINE', COUNTERFEIT: 'COUNTERFEIT', UNCERTAIN: 'UNCERTAIN', NOT_SUPPORTED: 'NOT SUPPORTED',
        msgGENUINE: 'The note looks genuine.',
        msgCOUNTERFEIT: 'The note looks COUNTERFEIT. Do not accept it; verify at a bank.',
        msgUNCERTAIN: 'The AI is not sure. Check the watermark, security thread and raised print by hand, or add more photos.',
        msgNOT_SUPPORTED: 'This does not look like a Tk 500 / Tk 1000 note photo. Upload a clear, close photo of the note.',
        viewHints: ['Front · portrait', 'Front · centre', 'Front · right', 'Watermark area', 'Back side', 'Against light'],
        photo: 'Photo', real: 'REAL', fake: 'FAKE', ignored: 'IGNORED', preview: 'Preview', remove: 'Remove',
        ignoredTip: 'Does not look like a Tk 500 / Tk 1000 note, ignored',
        tooMany: 'Only 6 photos per note. Extra photos were skipped.', notImage: 'Please choose image files.',
        added: (n) => `${n} photo${n > 1 ? 's' : ''} added`, pasted: 'Photo pasted from clipboard',
        noCamera: 'Camera not available. Opening file picker instead.', serverDown: 'Could not connect to the server.',
        captured: 'Photo captured', historyCleared: 'History cleared', removed: 'Photo removed', undo: 'Undo',
        copied: 'Summary copied to clipboard', copyFail: 'Could not copy to clipboard', saved: 'Report downloaded',
        all: 'All',
    },
    bn: {
        statusChecking: 'মডেল যাচাই হচ্ছে…', statusReady: 'মডেল প্রস্তুত', statusError: 'মডেল প্রস্তুত নয়',
        proUi: 'প্রো UI', eyebrow: 'ব্যাখ্যাযোগ্য AI · ৫০০ ও ১০০০ টাকা', heroTitle1: 'আপনার টাকা কি', heroTitle2: 'আসল?',
        heroSub: '৫০০ বা ১০০০ টাকার নোটের কাছ থেকে তোলা ছবি দিন। AI কয়েক সেকেন্ডে ছাপা ও নিরাপত্তা বৈশিষ্ট্য যাচাই করবে।',
        hsAcc: 'পরীক্ষায় নির্ভুলতা', hsFdr: 'জাল শনাক্ত', hsPhotos: 'প্রতি নোটে ছবি',
        step1: 'ছবি দিন', step2: 'বিশ্লেষণ', step3: 'ফলাফল',
        dropTitle: 'এখানে ছবি ছাড়ুন', dropSub: 'অথবা ক্লিক করে বাছাই করুন · Ctrl+V দিয়ে পেস্ট · একই নোটের সর্বোচ্চ ৬টি ছবি',
        browse: 'ফাইল বাছাই', camera: 'ক্যামেরা', trayTitle: 'বাছাই করা ছবি', clearAll: 'সব মুছুন',
        trayHint: 'পরামর্শ: সামনের দিক (প্রতিকৃতি), পেছনের দিক এবং আলোর সামনে ধরা নোট দিলে ফল সবচেয়ে নির্ভরযোগ্য হয়। টেনে ক্রম বদলান, ক্লিক করে দেখুন।',
        coverage: (n) => n === 0 ? 'এখনো ছবি নেই' : n < 3 ? 'নির্ভরযোগ্য ফলের জন্য আরও ছবি দিন' : n < 6 ? 'ভালো কভারেজ' : 'সর্বোচ্চ কভারেজ',
        thresholdLabel: '"আসল" বলার জন্য প্রয়োজনীয় আস্থা', analyze: 'নোট যাচাই করুন',
        pLenient: 'নমনীয়', pBalanced: 'সুষম', pStrict: 'কঠোর',
        loadingTitle: 'নোট যাচাই হচ্ছে…',
        load1: 'ছবি আপলোড হচ্ছে', load2: '৫০০ / ১০০০ টাকার নোট কিনা দেখা হচ্ছে', load3: 'AI দিয়ে ছাপা বিশ্লেষণ', load4: 'ব্যাখ্যা হিটম্যাপ তৈরি',
        pReal: 'আসল হওয়ার সম্ভাবনা', thresholdLive: 'কঠোরতা (সাথে সাথে ফল বদলায়)',
        consensus: 'ছবিগুলোর মিল', spread: (v) => `পার্থক্য ±${v}%`,
        confidence: 'আস্থা', photosUsed: 'ব্যবহৃত ছবি',
        modeHeat: 'AI ফোকাস', modeCompare: 'তুলনা', modeEdges: 'রেখা', modeOriginal: 'মূল ছবি', low: 'কম', high: 'বেশি',
        heatHint: 'লাল = যে অংশ AI-এর সিদ্ধান্তে সবচেয়ে বেশি প্রভাব ফেলেছে · স্ক্রল করে জুম, টেনে সরান',
        copy: 'সারাংশ কপি', download: 'রিপোর্ট ডাউনলোড', report: 'রিপোর্ট প্রিন্ট', newScan: 'আরেকটি নোট যাচাই',
        history: 'সাম্প্রতিক যাচাই', historyEmpty: 'এখনো কোনো যাচাই নেই। ফলাফল শুধু এই ব্রাউজারে থাকে।',
        modelTitle: 'AI মডেল', details: 'বিস্তারিত', kAcc: 'নির্ভুলতা', kFdr: 'জাল শনাক্ত',
        modelNotes: (n) => `পরীক্ষা সেট: ${n}টি নোট, প্রতিটির ৬টি ছবি`,
        howTitle: 'কীভাবে কাজ করে',
        f1t: 'আসল নোটে প্রশিক্ষিত', f1d: '১,৩৯০টি আসল ও জাল টাকার নোটে (JaalTaka) প্রশিক্ষিত EfficientNet মডেল।',
        f2t: 'ব্যাখ্যাযোগ্য', f2d: 'হিটম্যাপ দেখায় নোটের কোন অংশ দেখে সিদ্ধান্ত নেওয়া হয়েছে।',
        f3t: 'নিরাপদ প্রত্যাখ্যান', f3d: '৫০০ / ১০০০ টাকার নোট না হলে অনুমান না করে বাতিল করা হয়।',
        cameraTitle: 'ছবি তুলুন', cameraHint: 'নোট দিয়ে ফ্রেম ভরে দিন, ঝলক এড়িয়ে চলুন। সামনে, পেছনে ও আলোর সামনে কয়েকটি ছবি তুলুন।',
        switchCam: 'ক্যামেরা বদলান', capture: 'ছবি তুলুন', done: 'শেষ',
        tipsTitle: 'নোটের ছবি কীভাবে তুলবেন',
        tip1: 'কাছে যান: নোটটি ছবির বেশিরভাগ জুড়ে থাকবে।', tip2: 'সামনের দিক: প্রতিকৃতি ও নিরাপত্তা সুতা।',
        tip3: 'নোটের পেছনের দিক।', tip4: 'জলছাপ দেখাতে নোটটি আলোর সামনে ধরুন।',
        tip5: 'ঝলক, ঝাপসা ও স্ক্যান করা ছবি এড়িয়ে চলুন।', tip6: 'এটি সহায়ক টুল। সন্দেহজনক নোট ব্যাংকে যাচাই করুন।',
        keysTitle: 'কিবোর্ড শর্টকাট', kPaste: 'ছবি পেস্ট', kEnter: 'যাচাই / ছবি তোলা', kArrows: 'আগের / পরের ছবি',
        kModes: 'দেখার ধরন বদলান', kZoom: 'জুম ইন / আউট / রিসেট', kLens: 'ম্যাগনিফায়ার', kFull: 'পূর্ণ পর্দা',
        kTheme: 'লাইট / ডার্ক থিম', kEsc: 'বন্ধ / নতুন যাচাই',
        footer: '© ২০২৬ AI Currency Guardian · শুধু সহায়ক সিদ্ধান্ত। সন্দেহজনক নোট ব্যাংকে যাচাই করুন।',
        splits: { test_per_note_6_views: 'পরীক্ষা · প্রতি নোট', test_per_photo: 'পরীক্ষা · প্রতি ছবি', val_per_photo: 'যাচাই সেট',
            diagnostic_center_hidden: 'স্ট্রেস · মাঝখান ঢাকা', diagnostic_border_hidden: 'স্ট্রেস · কিনারা ঢাকা' },
        mAcc: 'নির্ভুলতা', mAuc: 'ROC AUC', mFdr: 'জাল শনাক্ত', mRar: 'আসল গ্রহণ',
        cmTitle: 'কনফিউশন ম্যাট্রিক্স', actual: 'প্রকৃত', predicted: 'পূর্বাভাস', realL: 'আসল', fakeL: 'জাল',
        samples: (n) => `${n}টি নমুনা`, dataset: 'ডেটাসেট',
        GENUINE: 'আসল', COUNTERFEIT: 'জাল', UNCERTAIN: 'অনিশ্চিত', NOT_SUPPORTED: 'সমর্থিত নয়',
        msgGENUINE: 'নোটটি আসল মনে হচ্ছে।',
        msgCOUNTERFEIT: 'নোটটি জাল মনে হচ্ছে। গ্রহণ করবেন না; ব্যাংকে যাচাই করুন।',
        msgUNCERTAIN: 'AI নিশ্চিত নয়। জলছাপ, নিরাপত্তা সুতা ও উঁচু ছাপা হাতে যাচাই করুন, অথবা আরও ছবি দিন।',
        msgNOT_SUPPORTED: 'এটি ৫০০ / ১০০০ টাকার নোটের ছবি মনে হচ্ছে না। নোটের পরিষ্কার, কাছ থেকে তোলা ছবি দিন।',
        viewHints: ['সামনে · প্রতিকৃতি', 'সামনে · মাঝখান', 'সামনে · ডান', 'জলছাপ অংশ', 'পেছনের দিক', 'আলোর সামনে'],
        photo: 'ছবি', real: 'আসল', fake: 'জাল', ignored: 'বাদ', preview: 'দেখুন', remove: 'মুছুন',
        ignoredTip: '৫০০ / ১০০০ টাকার নোট মনে হয়নি, বাদ দেওয়া হয়েছে',
        tooMany: 'একটি নোটের জন্য সর্বোচ্চ ৬টি ছবি। বাকিগুলো বাদ দেওয়া হয়েছে।', notImage: 'অনুগ্রহ করে ছবি ফাইল দিন।',
        added: (n) => `${n}টি ছবি যোগ হয়েছে`, pasted: 'ক্লিপবোর্ড থেকে ছবি যোগ হয়েছে',
        noCamera: 'ক্যামেরা পাওয়া যায়নি। ফাইল বাছাই খোলা হচ্ছে।', serverDown: 'সার্ভারের সাথে সংযোগ করা যায়নি।',
        captured: 'ছবি তোলা হয়েছে', historyCleared: 'ইতিহাস মুছে ফেলা হয়েছে', removed: 'ছবি মুছে ফেলা হয়েছে', undo: 'ফেরত',
        copied: 'সারাংশ কপি হয়েছে', copyFail: 'কপি করা যায়নি', saved: 'রিপোর্ট ডাউনলোড হয়েছে',
        all: 'সব',
    },
};

const store = {
    get(k, d) { try { const v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch { return d; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch { /* storage unavailable */ } },
};

let lang = store.get('cg_lang', 'en');
const t = (key) => (I18N[lang] && I18N[lang][key] !== undefined ? I18N[lang][key] : I18N.en[key]);
const pct = (v, d = 1) => (v * 100).toFixed(d) + '%';

function applyLang() {
    document.documentElement.lang = lang;
    document.body.classList.toggle('lang-bn', lang === 'bn');
    document.querySelectorAll('[data-i18n]').forEach((el) => { el.textContent = t(el.dataset.i18n); });
    $('lang-label').textContent = lang === 'en' ? 'বাং' : 'EN';
    renderTray();
    if (state.result) renderResult(false);
    renderHistory();
    refreshStatusText();
    if (!$('model-modal').classList.contains('hidden')) renderModelModal();
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
    split: 'test_per_note_6_views',
    historyFilter: null,
};

// ---------------------------------------------------------------------
// Toasts, tooltips, ripple
// ---------------------------------------------------------------------
const TOAST_ICON = { info: 'fa-circle-check', error: 'fa-circle-exclamation', warn: 'fa-triangle-exclamation' };

function toast(msg, type = 'info', ms = 3200, action = null) {
    const el = document.createElement('div');
    el.className = `toast ${type}`;
    el.innerHTML = `<i class="fas ${TOAST_ICON[type] || TOAST_ICON.info}"></i><span></span><i class="t-life" style="animation-duration:${ms}ms"></i>`;
    el.querySelector('span').textContent = msg;
    const dismiss = () => { el.style.opacity = '0'; el.style.transition = 'opacity .3s'; setTimeout(() => el.remove(), 320); };
    if (action) {
        const b = document.createElement('button');
        b.className = 't-action';
        b.textContent = action.label;
        b.addEventListener('click', () => { action.run(); dismiss(); });
        el.insertBefore(b, el.querySelector('.t-life'));
    }
    $('toasts').appendChild(el);
    setTimeout(dismiss, ms);
}

const tip = $('tooltip');
document.addEventListener('pointerover', (e) => {
    const el = e.target.closest('[data-tip]');
    if (!el || e.pointerType === 'touch') return;
    tip.textContent = el.dataset.tip;
    tip.classList.remove('hidden');
    const r = el.getBoundingClientRect();
    const tr = tip.getBoundingClientRect();
    let left = r.left + r.width / 2 - tr.width / 2;
    left = Math.max(8, Math.min(window.innerWidth - tr.width - 8, left));
    const top = r.bottom + 8 + tr.height > window.innerHeight ? r.top - tr.height - 8 : r.bottom + 8;
    tip.style.left = left + 'px';
    tip.style.top = top + 'px';
});
document.addEventListener('pointerout', (e) => { if (e.target.closest('[data-tip]')) tip.classList.add('hidden'); });

document.addEventListener('pointerdown', (e) => {
    const b = e.target.closest('.btn-primary, .btn-ghost');
    if (!b || b.disabled) return;
    const r = b.getBoundingClientRect();
    const s = Math.max(r.width, r.height);
    const span = document.createElement('span');
    span.className = 'ripple';
    span.style.cssText = `width:${s}px;height:${s}px;left:${e.clientX - r.left - s / 2}px;top:${e.clientY - r.top - s / 2}px`;
    b.appendChild(span);
    setTimeout(() => span.remove(), 650);
});

// ---------------------------------------------------------------------
// Theme & language
// ---------------------------------------------------------------------
function toggleTheme() {
    const root = document.documentElement;
    const next = root.classList.contains('dark-theme') ? 'light-theme' : 'dark-theme';
    root.classList.remove('dark-theme', 'light-theme');
    root.classList.add(next);
    store.set('cg_theme', next);
}
$('theme-toggle').addEventListener('click', toggleTheme);
$('lang-toggle').addEventListener('click', () => {
    lang = lang === 'en' ? 'bn' : 'en';
    store.set('cg_lang', lang);
    applyLang();
});

// ---------------------------------------------------------------------
// Model status, KPIs and the model details modal
// ---------------------------------------------------------------------
function setRing(id, v) {
    const el = $(id);
    el.querySelector('b').textContent = v === undefined ? '–' : (v * 100).toFixed(1);
    requestAnimationFrame(() => el.style.setProperty('--v', v === undefined ? 0 : (v * 100).toFixed(1)));
}

function refreshStatusText() {
    const el = $('model-status');
    const label = el.querySelector('span');
    if (!state.status) { label.textContent = t('statusChecking'); return; }
    const m = (state.status.metrics || {}).test_per_note_6_views;
    if (state.status.ready) {
        el.className = 'status-badge ok';
        label.textContent = t('statusReady') + (m ? ` · ${pct(m.accuracy)}` : '');
        el.dataset.tip = m ? `Held-out test accuracy ${pct(m.accuracy)} · counterfeit detection ${pct(m.fake_detection_rate)}` : '';
    } else {
        el.className = 'status-badge err';
        label.textContent = t('statusError');
        el.dataset.tip = state.status.error || '';
    }
    $('hs-acc').textContent = m ? pct(m.accuracy) : '–';
    $('hs-fdr').textContent = m ? pct(m.fake_detection_rate) : '–';
    setRing('ring-acc', m && m.accuracy);
    setRing('ring-fdr', m && m.fake_detection_rate);
    setRing('ring-auc', m && m.auc);
    $('model-notes').textContent = m ? t('modelNotes')(m.n) : (state.status.error || '');
}

function renderModelModal() {
    const metrics = (state.status && state.status.metrics) || {};
    const splits = Object.keys(t('splits')).filter((k) => metrics[k]);
    const tabs = $('split-tabs');
    tabs.innerHTML = '';
    splits.forEach((k) => {
        const b = document.createElement('button');
        b.textContent = t('splits')[k];
        b.className = k === state.split ? 'active' : '';
        b.addEventListener('click', () => { state.split = k; renderModelModal(); });
        tabs.appendChild(b);
    });
    const m = metrics[state.split];
    const body = $('model-body');
    if (!m) { body.innerHTML = `<p class="hint">${esc((state.status && state.status.error) || '–')}</p>`; return; }
    const rows = [['mAcc', m.accuracy], ['mAuc', m.auc], ['mFdr', m.fake_detection_rate], ['mRar', m.real_acceptance_rate]];
    const c = m.confusion;
    const realN = c.real_as_real + c.real_as_fake;
    const fakeN = c.fake_as_fake + c.fake_as_real;
    const cell = (v, n, good) => {
        const a = (0.12 + 0.6 * (v / Math.max(1, n))).toFixed(2);
        const col = good ? `rgba(16,185,129,${a})` : `rgba(239,68,68,${a})`;
        return `<div class="c" style="background:${col}" data-tip="${pct(v / Math.max(1, n))}">${v}<small>${pct(v / Math.max(1, n), 1)}</small></div>`;
    };
    body.innerHTML = `
        <div class="metric-list">${rows.map(([k, v]) => `
            <div class="metric"><div class="metric-top"><span>${t(k)}</span><b>${pct(v)}</b></div>
            <div class="bar"><i style="width:0" data-w="${(v * 100).toFixed(1)}"></i></div></div>`).join('')}
            <p class="hint">${t('samples')(m.n)}</p>
        </div>
        <div>
            <div class="cm-title">${t('cmTitle')}</div>
            <div class="cm">
                <div class="h">${t('actual')} ↓ / ${t('predicted')} →</div><div class="h">${t('realL')}</div><div class="h">${t('fakeL')}</div>
                <div class="h">${t('realL')}</div>${cell(c.real_as_real, realN, true)}${cell(c.real_as_fake, realN, false)}
                <div class="h">${t('fakeL')}</div>${cell(c.fake_as_real, fakeN, false)}${cell(c.fake_as_fake, fakeN, true)}
            </div>
        </div>
        ${metrics.dataset ? `<p class="model-foot"><b>${t('dataset')}:</b> ${esc(metrics.dataset)}</p>` : ''}`;
    requestAnimationFrame(() => requestAnimationFrame(() => body.querySelectorAll('.bar > i').forEach((i) => { i.style.width = i.dataset.w + '%'; })));
}

function openModelModal() { renderModelModal(); openModal('model-modal'); }
$('model-status').addEventListener('click', openModelModal);
$('model-more').addEventListener('click', openModelModal);

fetch('/status').then((r) => r.json()).then((s) => {
    state.status = s;
    refreshStatusText();
    if (!s.ready) toast(s.error, 'error', 8000);
}).catch(() => { state.status = { ready: false, error: t('serverDown') }; refreshStatusText(); });

// ---------------------------------------------------------------------
// Steps indicator
// ---------------------------------------------------------------------
function setStep(n) {
    document.querySelectorAll('#steps li[data-step]').forEach((li) => {
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
    const [p] = state.photos.splice(i, 1);
    renderTray();
    let undone = false;
    toast(t('removed'), 'info', 4500, {
        label: t('undo'),
        run: () => {
            if (state.photos.length >= MAX_PHOTOS) return;
            undone = true;
            state.photos.splice(Math.min(i, state.photos.length), 0, p);
            renderTray();
        },
    });
    // free the preview URL once undo is no longer possible
    setTimeout(() => { if (!undone) URL.revokeObjectURL(p.url); }, 5000);
}

function clearPhotos() {
    state.photos.forEach((p) => URL.revokeObjectURL(p.url));
    state.photos = [];
    renderTray();
}

let dragFrom = null;
function renderTray() {
    const tray = $('tray');
    tray.innerHTML = '';
    const hints = t('viewHints');
    for (let i = 0; i < MAX_PHOTOS; i++) {
        const slot = document.createElement('div');
        const p = state.photos[i];
        if (p) {
            slot.className = 'slot filled';
            slot.draggable = true;
            slot.innerHTML = `<img src="${p.url}" alt="" draggable="false"><span class="num">${i + 1}</span>
                <button class="zoom" data-tip="${t('preview')}" aria-label="${t('preview')} ${i + 1}"><i class="fas fa-expand"></i></button>
                <button class="rm" data-tip="${t('remove')}" aria-label="${t('remove')} ${i + 1}"><i class="fas fa-xmark"></i></button>`;
            slot.querySelector('.rm').addEventListener('click', (e) => { e.stopPropagation(); tip.classList.add('hidden'); removePhoto(i); });
            slot.querySelector('.zoom').addEventListener('click', (e) => { e.stopPropagation(); preview(p.url); });
            slot.addEventListener('click', () => preview(p.url));
            // drag to reorder
            slot.addEventListener('dragstart', (e) => { dragFrom = i; slot.classList.add('dragging'); e.dataTransfer.effectAllowed = 'move'; });
            slot.addEventListener('dragend', () => { dragFrom = null; slot.classList.remove('dragging'); });
        } else {
            slot.className = 'slot' + (i === state.photos.length ? ' next-up' : '');
            slot.innerHTML = `<i class="fas fa-plus"></i><span>${hints[i]}</span>`;
            slot.addEventListener('click', () => fileInput.click());
        }
        slot.addEventListener('dragover', (e) => {
            if (dragFrom === null) return;
            e.preventDefault();
            slot.classList.add('drop-target');
        });
        slot.addEventListener('dragleave', () => slot.classList.remove('drop-target'));
        slot.addEventListener('drop', (e) => {
            if (dragFrom === null) return;
            e.preventDefault();
            e.stopPropagation();
            const to = Math.min(i, state.photos.length - 1);
            const [moved] = state.photos.splice(dragFrom, 1);
            state.photos.splice(to, 0, moved);
            dragFrom = null;
            renderTray();
        });
        tray.appendChild(slot);
    }
    const n = state.photos.length;
    $('tray-count').textContent = `${n}/${MAX_PHOTOS}`;
    $('cam-count').textContent = `${n}/${MAX_PHOTOS}`;
    $('cam-guide').textContent = n < MAX_PHOTOS ? `${n + 1}. ${hints[n]}` : '';
    $('analyze-btn').disabled = n === 0;
    $('analyze-btn').classList.toggle('ready', n > 0);
    $('clear-btn').classList.toggle('hidden', n === 0);
    $('coverage-fill').style.width = (n / MAX_PHOTOS * 100) + '%';
    $('coverage-text').textContent = t('coverage')(n);
}

function preview(url) {
    $('preview-img').src = url;
    openModal('preview-modal');
}

dropZone.addEventListener('click', (e) => { if (!e.target.closest('button')) fileInput.click(); });
dropZone.addEventListener('keydown', (e) => { if (e.key === ' ' || e.key === 'Enter') { e.preventDefault(); e.stopPropagation(); fileInput.click(); } });
$('browse-btn').addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', (e) => { addFiles(e.target.files); fileInput.value = ''; });

const isFileDrag = (e) => e.dataTransfer && Array.from(e.dataTransfer.types || []).includes('Files');
['dragenter', 'dragover'].forEach((ev) => dropZone.addEventListener(ev, (e) => { if (!isFileDrag(e)) return; e.preventDefault(); dropZone.classList.add('drag-over'); }));
['dragleave', 'drop'].forEach((ev) => dropZone.addEventListener(ev, (e) => { e.preventDefault(); dropZone.classList.remove('drag-over'); }));
dropZone.addEventListener('drop', (e) => { if (e.dataTransfer.files.length) addFiles(e.dataTransfer.files); });
// files dropped on the tray are added too
$('tray').addEventListener('dragover', (e) => { if (isFileDrag(e)) e.preventDefault(); });
$('tray').addEventListener('drop', (e) => { if (isFileDrag(e) && dragFrom === null) { e.preventDefault(); addFiles(e.dataTransfer.files); } });

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
function openModal(id) { tip.classList.add('hidden'); $(id).classList.remove('hidden'); }
function closeModal(id) {
    $(id).classList.add('hidden');
    if (id === 'camera-modal') stopCamera();
}
document.querySelectorAll('.modal').forEach((m) => {
    m.addEventListener('click', (e) => { if (e.target === m || e.target.closest('[data-close]')) closeModal(m.id); });
});
$('tips-btn').addEventListener('click', () => openModal('tips-modal'));
$('keys-btn').addEventListener('click', () => openModal('keys-modal'));

// ---------------------------------------------------------------------
// Sliders: filled track, threshold sync (result verdict updates live), presets
// ---------------------------------------------------------------------
function paintRange(el) {
    const min = Number(el.min || 0), max = Number(el.max || 100);
    el.style.setProperty('--fill', ((el.value - min) / (max - min) * 100) + '%');
}
document.querySelectorAll('input[type=range]').forEach((el) => { paintRange(el); el.addEventListener('input', () => paintRange(el)); });

const thr1 = $('threshold');
const thr2 = $('threshold2');
function setThreshold(v, from) {
    thr1.value = v; thr2.value = v;
    paintRange(thr1); paintRange(thr2);
    $('threshold-val').textContent = v + '%';
    $('threshold2-val').textContent = v + '%';
    document.querySelectorAll('#presets button').forEach((b) => b.classList.toggle('active', Number(b.dataset.v) === Number(v)));
    store.set('cg_threshold', Number(v));
    if (from === 'live' && state.result) renderResult(false);
}
thr1.addEventListener('input', () => setThreshold(thr1.value));
thr2.addEventListener('input', () => setThreshold(thr2.value, 'live'));
document.querySelectorAll('#presets button').forEach((b) => b.addEventListener('click', () => setThreshold(b.dataset.v)));
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
            // cycle the scanned preview through the photos
            if (state.photos[i % n]) $('loading-img').src = state.photos[i % n].url;
        }, ms * Math.max(1, n / 2)));
    });
}

function hideLoading() {
    loadingTimers.forEach(clearTimeout);
    loadingTimers = [];
    document.querySelectorAll('#loading-steps li').forEach((li) => { li.classList.remove('active'); li.classList.add('done'); });
    $('progress-bar').style.width = '100%';
}

let busy = false;
async function analyze() {
    if (!state.photos.length || busy) return;
    busy = true;
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
        resetZoom();
        setTimeout(() => { renderResult(true); addHistory(); }, 250);
    } catch (err) {
        hideLoading();
        $('loading-panel').classList.add('hidden');
        $('input-panel').classList.remove('hidden');
        setStep(1);
        toast(err.message === 'Failed to fetch' ? t('serverDown') : err.message, 'error', 6000);
    } finally {
        busy = false;
    }
}
$('analyze-btn').addEventListener('click', analyze);

// ---------------------------------------------------------------------
// Verdict logic (mirrors detector.summarize, so the threshold can change live)
// ---------------------------------------------------------------------
function decide(result, thr) {
    const usable = result.per_image.filter((p) => p.in_distribution);
    if (!usable.length) return { verdict: 'NOT_SUPPORTED', p: null, conf: null, used: 0, sd: null };
    const p = usable.reduce((s, x) => s + x.real_probability, 0) / usable.length;
    const sd = Math.sqrt(usable.reduce((s, x) => s + (x.real_probability - p) ** 2, 0) / usable.length);
    const verdict = p >= thr ? 'GENUINE' : p < 0.5 ? 'COUNTERFEIT' : 'UNCERTAIN';
    return { verdict, p, conf: 100 * (p >= 0.5 ? p : 1 - p), used: usable.length, sd };
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
    $('verdict-card').className = 'card verdict-card ' + ui.cls;
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

    renderConsensus(d, thr, first);
    renderStrip(first);
    renderViewer();
}

// per-photo dots on a 0-100% scale with the decision zones behind them
function renderConsensus(d, thr, first) {
    $('c-unsure').style.width = ((thr - 0.5) * 100) + '%';
    $('c-thr').style.left = (thr * 100) + '%';
    $('consensus-sd').textContent = d.sd === null || d.used < 2 ? '' : t('spread')((d.sd * 100).toFixed(0));
    const scale = $('c-scale');
    scale.querySelectorAll('.c-dot').forEach((x) => x.remove());
    const placed = [];
    state.result.per_image.forEach((p, i) => {
        // dots closer than ~6% would overlap: spread them over three lanes
        const lane = placed.filter((x) => Math.abs(x - p.real_probability) < 0.06).length % 3;
        placed.push(p.real_probability);
        const dot = document.createElement('button');
        dot.style.top = `calc(50% + ${[0, -11, 11][lane]}px)`;
        const cls = !p.in_distribution ? 'ignored' : p.real_probability >= 0.5 ? 'real' : 'fake';
        dot.className = `c-dot ${cls}` + (i === state.selected ? ' active' : '');
        dot.textContent = i + 1;
        dot.dataset.tip = `${t('photo')} ${i + 1} · P(real) ${pct(p.real_probability)}` + (p.in_distribution ? '' : ` · ${t('ignored')}`);
        dot.style.left = first ? '50%' : (p.real_probability * 100) + '%';
        dot.addEventListener('click', () => selectPhoto(i));
        scale.appendChild(dot);
        if (first) requestAnimationFrame(() => requestAnimationFrame(() => { dot.style.left = (p.real_probability * 100) + '%'; }));
    });
}

function renderStrip(animate) {
    const strip = $('photo-strip');
    strip.innerHTML = '';
    state.result.per_image.forEach((p, i) => {
        const card = document.createElement('button');
        card.className = 'photo-card' + (i === state.selected ? ' active' : '');
        card.style.animationDelay = animate ? `${i * 60}ms` : '0ms';
        let status, cls;
        if (!p.in_distribution) { status = t('ignored'); cls = 'status-warn'; } else if (p.real_probability >= 0.5) { status = t('real'); cls = 'status-pass'; } else { status = t('fake'); cls = 'status-fail'; }
        const v = (p.real_probability * 100).toFixed(0);
        card.dataset.tip = p.in_distribution ? `P(real) ${v}%` : t('ignoredTip');
        card.innerHTML = `<img src="data:image/jpeg;base64,${p.visuals.original}" alt="">
            <div class="pc-body">
                <div class="pc-top"><span>${t('photo')} ${i + 1}</span><span class="feature-status ${cls}">${status}</span></div>
                <div class="bar"><i style="width:${animate ? 0 : v}%"></i></div>
            </div>`;
        card.addEventListener('click', () => selectPhoto(i));
        strip.appendChild(card);
        if (animate) requestAnimationFrame(() => requestAnimationFrame(() => { card.querySelector('.bar i').style.width = v + '%'; }));
    });
}

function selectPhoto(i) {
    if (!state.result) return;
    const n = state.result.per_image.length;
    state.selected = (i + n) % n;
    document.querySelectorAll('#photo-strip .photo-card').forEach((c, j) => c.classList.toggle('active', j === state.selected));
    document.querySelectorAll('#c-scale .c-dot').forEach((c, j) => c.classList.toggle('active', j === state.selected));
    resetZoom();
    renderViewer();
}

// ---------------------------------------------------------------------
// Inspector: modes, heatmap opacity, compare slider, zoom & pan, magnifier, fullscreen
// ---------------------------------------------------------------------
const viewer = $('viewer');
const stage = $('stage');
const vBase = $('v-base');
const vLayer = $('v-layer');
const handle = $('compare-handle');
let comparePos = 50;
const MODES = ['heatmap', 'compare', 'edges', 'original'];

function src(key) { return 'data:image/jpeg;base64,' + state.result.per_image[state.selected].visuals[key]; }

function renderViewer() {
    if (!state.result) return;
    const m = state.mode;
    const p = state.result.per_image[state.selected];
    const n = state.result.per_image.length;
    document.querySelectorAll('#view-modes button').forEach((b) => b.classList.toggle('active', b.dataset.mode === m));
    vBase.src = src(m === 'edges' ? 'edges' : 'original');
    vLayer.classList.toggle('hidden', !(m === 'heatmap' || m === 'compare'));
    handle.classList.toggle('hidden', m !== 'compare');
    $('compare-labels').classList.toggle('hidden', m !== 'compare');
    $('opacity-row').classList.toggle('hidden', m !== 'heatmap');
    $('prev-photo').disabled = n < 2;
    $('next-photo').disabled = n < 2;
    $('viewer-chip').textContent = `${t('photo')} ${state.selected + 1}/${n} · P(real) ${pct(p.real_probability, 0)}`;
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

function setMode(m) { state.mode = m; renderViewer(); }
document.querySelectorAll('#view-modes button').forEach((b) => b.addEventListener('click', () => setMode(b.dataset.mode)));
$('opacity').addEventListener('input', (e) => { vLayer.style.opacity = e.target.value / 100; });
$('prev-photo').addEventListener('click', (e) => { e.stopPropagation(); selectPhoto(state.selected - 1); });
$('next-photo').addEventListener('click', (e) => { e.stopPropagation(); selectPhoto(state.selected + 1); });
['pointerdown', 'pointerup'].forEach((ev) => {
    $('prev-photo').addEventListener(ev, (e) => e.stopPropagation());
    $('next-photo').addEventListener(ev, (e) => e.stopPropagation());
});

// --- zoom & pan (stage is transformed: translate(tx, ty) scale(z), origin top-left)
const view = { z: 1, tx: 0, ty: 0 };
function clampView() {
    const w = stage.offsetWidth, h = stage.offsetHeight;
    view.z = Math.max(1, Math.min(6, view.z));
    view.tx = Math.min(0, Math.max(w - w * view.z, view.tx));
    view.ty = Math.min(0, Math.max(h - h * view.z, view.ty));
}
function applyView() {
    clampView();
    stage.style.transform = `translate(${view.tx}px, ${view.ty}px) scale(${view.z})`;
    viewer.classList.toggle('zoomed', view.z > 1);
    $('zoom-val').textContent = Math.round(view.z * 100) + '%';
    $('zoom-out').disabled = view.z <= 1;
    $('zoom-in').disabled = view.z >= 6;
    if (state.mode === 'compare') setCompare(comparePos);
}
function zoomAt(factor, cx, cy) {
    const r = stage.parentElement.getBoundingClientRect();
    const x = cx === undefined ? r.width / 2 : cx - r.left;
    const y = cy === undefined ? r.height / 2 : cy - r.top;
    const nz = Math.max(1, Math.min(6, view.z * factor));
    view.tx = x - (x - view.tx) * (nz / view.z);
    view.ty = y - (y - view.ty) * (nz / view.z);
    view.z = nz;
    applyView();
}
function resetZoom() { view.z = 1; view.tx = 0; view.ty = 0; applyView(); }
$('zoom-in').addEventListener('click', () => zoomAt(1.5));
$('zoom-out').addEventListener('click', () => zoomAt(1 / 1.5));
viewer.addEventListener('wheel', (e) => {
    if (!state.result) return;
    e.preventDefault();
    zoomAt(e.deltaY < 0 ? 1.2 : 1 / 1.2, e.clientX, e.clientY);
}, { passive: false });
viewer.addEventListener('dblclick', (e) => { if (view.z > 1) resetZoom(); else zoomAt(2.5, e.clientX, e.clientY); });

// --- compare slider (position is in image coordinates so it follows zoom)
function setCompare(p) {
    comparePos = Math.max(0, Math.min(100, p));
    vLayer.style.clipPath = `inset(0 0 0 ${comparePos}%)`;
    handle.style.left = (view.tx + (comparePos / 100) * stage.offsetWidth * view.z) + 'px';
}
function moveCompare(e) {
    const r = viewer.getBoundingClientRect();
    setCompare(((e.clientX - r.left - view.tx) / view.z / stage.offsetWidth) * 100);
}

let drag = null;   // 'compare' | 'pan'
let panStart = null;
viewer.addEventListener('pointerdown', (e) => {
    if (!state.result) return;
    if (state.mode === 'compare' && (e.target.closest('#compare-handle') || view.z === 1)) {
        drag = 'compare';
        moveCompare(e);
    } else if (view.z > 1 && !state.lens) {
        drag = 'pan';
        panStart = { x: e.clientX, y: e.clientY, tx: view.tx, ty: view.ty };
        viewer.classList.add('panning');
    } else return;
    viewer.setPointerCapture(e.pointerId);
});
viewer.addEventListener('pointerup', () => { drag = null; viewer.classList.remove('panning'); });

// Magnifier: works on the visible image content (accounts for letterboxing and zoom)
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
    if (drag === 'compare') { moveCompare(e); return; }
    if (drag === 'pan') {
        view.tx = panStart.tx + (e.clientX - panStart.x);
        view.ty = panStart.ty + (e.clientY - panStart.y);
        applyView();
        return;
    }
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
    lens.style.backgroundPosition = `${-(x * ZOOM - 85)}px ${-(y * ZOOM - 85)}px`;
});
viewer.addEventListener('pointerleave', () => lens.classList.add('hidden'));
function toggleLens() {
    state.lens = !state.lens;
    $('lens-btn').classList.toggle('active', state.lens);
    viewer.style.cursor = state.lens ? 'none' : '';
    if (!state.lens) lens.classList.add('hidden');
}
$('lens-btn').addEventListener('click', toggleLens);
function toggleFullscreen() {
    viewer.classList.toggle('fullscreen');
    $('fullscreen-btn').classList.toggle('active', viewer.classList.contains('fullscreen'));
    requestAnimationFrame(resetZoom);
}
$('fullscreen-btn').addEventListener('click', toggleFullscreen);
window.addEventListener('resize', () => { if (state.result) applyView(); });

// Download exactly what the viewer shows (blended heatmap, compare split, edges or original)
$('download-view').addEventListener('click', () => {
    if (!vBase.naturalWidth) return;
    const c = document.createElement('canvas');
    c.width = vBase.naturalWidth;
    c.height = vBase.naturalHeight;
    const g = c.getContext('2d');
    g.drawImage(vBase, 0, 0);
    if (state.mode === 'heatmap') {
        g.globalAlpha = $('opacity').value / 100;
        g.drawImage(vLayer, 0, 0, c.width, c.height);
    } else if (state.mode === 'compare') {
        const x = Math.round(c.width * comparePos / 100);
        g.drawImage(vLayer, x * vLayer.naturalWidth / c.width, 0, vLayer.naturalWidth - x * vLayer.naturalWidth / c.width, vLayer.naturalHeight, x, 0, c.width - x, c.height);
    }
    const a = document.createElement('a');
    a.href = c.toDataURL('image/jpeg', 0.92);
    a.download = `taka_photo${state.selected + 1}_${state.mode}.jpg`;
    a.click();
});

// ---------------------------------------------------------------------
// Report: copy / download / print
// ---------------------------------------------------------------------
function buildReport() {
    const r = state.result;
    const thr = thr2.value / 100;
    const d = decide(r, thr);
    const lines = [
        'AI CURRENCY GUARDIAN - Banknote Authentication Report',
        `Date: ${new Date().toLocaleString()}`,
        `Supported notes: ${r.supported_notes || 'Tk 500 and Tk 1000'}`, '',
        `VERDICT: ${d.verdict.replace('_', ' ')}`,
        I18N.en['msg' + d.verdict],
        `P(real): ${d.p === null ? '-' : pct(d.p)}`,
        `Confidence: ${d.conf === null ? '-' : d.conf.toFixed(1) + '%'}`,
        `Required confidence for GENUINE: ${Math.round(thr * 100)}%`,
        `Photos used: ${d.used}/${r.per_image.length}`, '', 'Per photo:',
        ...r.per_image.map((p, i) => `  Photo ${i + 1}: P(real) ${pct(p.real_probability)}${p.in_distribution ? '' : '  (ignored: not a supported note)'}`),
        '', 'Decision support only. Confirm suspicious notes at a bank.',
    ];
    return lines.join('\n');
}
$('copy-btn').addEventListener('click', async () => {
    try { await navigator.clipboard.writeText(buildReport()); toast(t('copied')); } catch { toast(t('copyFail'), 'error'); }
});
$('download-btn').addEventListener('click', () => {
    const blob = new Blob([buildReport()], { type: 'text/plain' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    const ts = new Date().toISOString().replace(/[-:T]/g, '').slice(0, 14);
    a.download = `taka_report_${ts}.txt`;
    a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
    toast(t('saved'));
});
$('report-btn').addEventListener('click', () => window.print());

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
    store.set('cg_history', list.slice(0, 12));
    renderHistory();
}

function renderHistory() {
    const list = store.get('cg_history', []);
    const el = $('history-list');
    el.innerHTML = '';
    $('history-empty').classList.toggle('hidden', list.length > 0);
    $('history-clear').classList.toggle('hidden', list.length === 0);

    // summary chips double as filters
    const sum = $('history-summary');
    sum.innerHTML = '';
    if (list.length) {
        const counts = { GENUINE: 0, COUNTERFEIT: 0, UNCERTAIN: 0 };
        list.forEach((h) => { if (counts[h.verdict] !== undefined) counts[h.verdict]++; });
        const chips = [[null, t('all'), list.length, '']].concat(Object.keys(counts).filter((k) => counts[k]).map((k) => [k, t(k), counts[k], VERDICT_UI[k].cls]));
        chips.forEach(([k, label, n, cls]) => {
            const c = document.createElement('button');
            c.className = `chip ${cls}` + (state.historyFilter === k ? ' active' : '');
            c.innerHTML = `${cls ? '<i class="fas fa-circle"></i>' : ''}${esc(label)} · ${n}`;
            c.addEventListener('click', () => { state.historyFilter = state.historyFilter === k ? null : k; renderHistory(); });
            sum.appendChild(c);
        });
    }

    list.filter((h) => !state.historyFilter || h.verdict === state.historyFilter).forEach((h) => {
        const item = document.createElement('div');
        item.className = 'h-item ' + VERDICT_UI[h.verdict].cls;
        const when = new Date(h.time).toLocaleString(lang === 'bn' ? 'bn-BD' : undefined, { dateStyle: 'short', timeStyle: 'short' });
        item.innerHTML = `${h.thumb ? `<img src="${h.thumb}" alt="">` : ''}
            <div><b>${t(h.verdict)}${h.p === null ? '' : ` · ${(h.p * 100).toFixed(0)}%`}</b>
            <small>${when} · ${h.n} ${t('photo')}</small></div>
            <button class="h-del" aria-label="${t('remove')}"><i class="fas fa-xmark"></i></button>`;
        item.querySelector('.h-del').addEventListener('click', () => {
            store.set('cg_history', store.get('cg_history', []).filter((x) => x.time !== h.time));
            renderHistory();
        });
        el.appendChild(item);
    });
}
$('history-clear').addEventListener('click', () => { store.set('cg_history', []); state.historyFilter = null; renderHistory(); toast(t('historyCleared')); });

// ---------------------------------------------------------------------
// Reset & keyboard shortcuts
// ---------------------------------------------------------------------
function newScan() {
    viewer.classList.remove('fullscreen');
    $('fullscreen-btn').classList.remove('active');
    state.result = null;
    clearPhotos();
    $('results-panel').classList.add('hidden');
    $('input-panel').classList.remove('hidden');
    setStep(1);
    window.scrollTo({ top: 0, behavior: 'smooth' });
}
$('new-scan-btn').addEventListener('click', newScan);

document.addEventListener('keydown', (e) => {
    const openModalEl = document.querySelector('.modal:not(.hidden)');
    if (e.key === 'Escape') {
        if (openModalEl) { closeModal(openModalEl.id); return; }
        if (viewer.classList.contains('fullscreen')) { toggleFullscreen(); return; }
        if (state.result) newScan();
        return;
    }
    if (openModalEl) {
        if (e.key === 'Enter' && openModalEl.id === 'camera-modal') $('camera-shot').click();
        return;
    }
    const typing = ['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName) && document.activeElement.type !== 'range';
    if (typing || e.ctrlKey || e.metaKey || e.altKey) return;

    if (e.key === '?') { openModal('keys-modal'); return; }
    if (e.key === 't' || e.key === 'T') { toggleTheme(); return; }

    if (state.result && !$('results-panel').classList.contains('hidden')) {
        if (document.activeElement.type === 'range') return;
        const k = e.key.toLowerCase();
        if (e.key === 'ArrowLeft') selectPhoto(state.selected - 1);
        else if (e.key === 'ArrowRight') selectPhoto(state.selected + 1);
        else if (['1', '2', '3', '4'].includes(e.key)) setMode(MODES[Number(e.key) - 1]);
        else if (e.key === '+' || e.key === '=') zoomAt(1.5);
        else if (e.key === '-') zoomAt(1 / 1.5);
        else if (e.key === '0') resetZoom();
        else if (k === 'm') toggleLens();
        else if (k === 'f') toggleFullscreen();
        else return;
        e.preventDefault();
        return;
    }

    if (e.key === 'Enter' && !$('input-panel').classList.contains('hidden') && state.photos.length
        && document.activeElement.tagName !== 'BUTTON') {
        e.preventDefault();
        analyze();
    }
});

applyLang();
