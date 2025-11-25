const downloadInterface = document.getElementById('download-interface');

const urlInput = document.getElementById('url-input');
const loader = document.getElementById('loader');

const submitBtn = document.getElementById('submit-btn');
const downloadBtn = document.getElementById('download-btn');

const videoThumbnail = document.getElementById('thumbnail-video');
const videoTitle = document.getElementById('title-video');

const videoFormatsSelect = document.getElementById('video-formats-select');
const audioFormatsSelect = document.getElementById('audio-formats-select');

const notyf = new Notyf();

const socket = io('/download');

socket.on('progress', function(data) {
    const percentage = data.percentage;
    console.log('Progreso:', percentage + '%');
    
    // Actualizar una barra de progreso, por ejemplo:
    downloadBtn.innerHTML = percentage + '%';
});

async function showInfo(url) {
    const [title, extractor, thumbnail, video_formats, audio_formats] = await getInfo(url);

    videoThumbnail.src = thumbnail;
    videoTitle.innerHTML = title;

    videoFormatsSelect.innerHTML = '<option value="none">❌ None</option>';
    audioFormatsSelect.innerHTML = '<option value="none">❌ None</option>';

    video_formats.reverse();
    audio_formats.reverse();

    let video_counter = 0;

    video_formats.forEach(format => {
        if (video_counter == 0) {
            videoFormatsSelect.innerHTML += `
                <option value="${format.format_id}">${format.ext} (${format.format_note})🔥</option>
            `;
        } else {
            videoFormatsSelect.innerHTML += `
                <option value="${format.format_id}">${format.ext} (${format.format_note})</option>
            `;
        }
        video_counter++;
    });

    audio_formats.forEach(format => {
        audioFormatsSelect.innerHTML += `
            <option value="${format.format_id}">${format.ext} (${format.format_note})</option>
        `;
    });

    videoFormatsSelect.selectedIndex = 1;
    audioFormatsSelect.selectedIndex = 1;

    downloadInterface.classList.remove('hidden');
    setTimeout(() => {
        downloadInterface.classList.remove('opacity-0', 'translate-y-4');
    }, 10);

    loader.classList.add('hidden');
}

async function getInfo(url) {
    const response = await fetch('/api/format', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ url: url })
    });

    const data = await response.json();

    if (data.success) {        
        const title = data.title;
        const extractor = data.extractor;
        const thumbnail = data.thumbnail;
        const video_formats = data.video_formats;
        const audio_formats = data.audio_formats;

        return [title, extractor, thumbnail, video_formats, audio_formats];
    } else {
        notyf.error('URL invalid.');
        loader.classList.add('hidden');
        throw new Error(data.error);
    }
}

async function startDownload(url) {
    try {
        const response = await fetch('/api/startDownload', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                url: url,
                video_format_id: videoFormatsSelect.value,
                audio_format_id: audioFormatsSelect.value
            })
        });

        const data = await response.json();

        if (data.success) {
            notyf.success('Download started!');
            downloadVideo(data.filename);
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        downloadBtn.classList.remove('downloading', 'w-full');
        downloadBtn.classList.add('min-w-[120px]');
        downloadBtn.innerHTML = 'Download';
        
        notyf.error('Download failed: ' + error.message);
    }
}

function downloadVideo(filename) {
    const url = `/api/download/${encodeURIComponent(filename)}`;
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();

    downloadBtn.classList.remove('downloading')
    downloadBtn.classList.remove('w-full')

    downloadBtn.classList.add('min-w-[120px]')
    downloadBtn.innerHTML = 'Download';
}

submitBtn.addEventListener('click', () => {
    showInfo(urlInput.value);

    if (!downloadInterface.classList.contains('hidden')) {
        downloadInterface.classList.add('opacity-0', 'hidden', 'translate-y-4');
    }

    loader.classList.remove('hidden');
});

downloadBtn.addEventListener('click', () => {
    if (videoFormatsSelect.value != "none" || audioFormatsSelect.value != "none") {
        startDownload(urlInput.value);
        downloadBtn.classList.add('downloading', 'w-full');
        //downloadBtn.innerHTML = '';
    } else {
        notyf.error('At least one format must not be none.');
    }
});