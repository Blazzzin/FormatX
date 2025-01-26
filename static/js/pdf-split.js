const MAX_SPLITS = 3;
let pdfPages = [];
let splitBoxes = [];
const fileInput = document.getElementById('file-input');
const mainPdfContainer = document.getElementById('main-pdf-container');
const pdfPreview = document.getElementById('pdf-preview');
const splitCountInput = document.getElementById('split-count');
const generateSplitsButton = document.getElementById('generate-splits');
const splitBoxContainer = document.getElementById('split-box-container');
const submitButton = document.querySelector('.merge-button');

fileInput.addEventListener('change', handleFileUpload);
generateSplitsButton.addEventListener('click', generateSplitBoxes);

function handleFileUpload(event) {
    const file = event.target.files[0];
    if (file && file.type === 'application/pdf') {
        mainPdfContainer.style.display = 'block';
        renderPDFPreview(file);
    } else {
        alert('Please upload a valid PDF.');
    }
}

function renderPDFPreview(file) {
    pdfPages = [];
    pdfPreview.innerHTML = '';
    const reader = new FileReader();
    reader.onload = (e) => {
        const pdfData = new Uint8Array(e.target.result);
        pdfjsLib.getDocument(pdfData).promise.then(pdf => {
            for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
                pdf.getPage(pageNum).then(page => {
                    const canvas = document.createElement('canvas');
                    const context = canvas.getContext('2d');
                    const scale = 1.5;
                    const viewport = page.getViewport({ scale });
                    canvas.height = viewport.height;
                    canvas.width = viewport.width;

                    page.render({ canvasContext: context, viewport }).promise.then(() => {
                        canvas.dataset.page = pageNum;
                        canvas.classList.add('file-item');
                        pdfPreview.appendChild(canvas);
                        pdfPages.push(canvas);

                        enableDragAndDrop();
                    });
                });
            }
        });
    };
    reader.readAsArrayBuffer(file);
}

function generateSplitBoxes() {
    const count = Math.min(Math.max(parseInt(splitCountInput.value) || 1, 1), MAX_SPLITS);
    splitBoxContainer.style.display = 'flex';
    splitBoxContainer.innerHTML = '';

    for (let i = 1; i <= count; i++) {
        const box = document.createElement('div');
        box.classList.add('split-box');
        box.textContent = `Split ${i}`;
        box.dataset.split = i;
        splitBoxContainer.appendChild(box);
    }

    enableDragAndDrop();
    submitButton.disabled = false;
}

function enableDragAndDrop() {
    pdfPages.forEach(page => {
        page.draggable = true;
        page.ondragstart = (e) => e.dataTransfer.setData('page', page.dataset.page);
    });

    const splitBoxes = document.querySelectorAll('.split-box');
    splitBoxes.forEach(box => {
        box.ondragover = (e) => e.preventDefault();
        box.ondrop = (e) => {
            const page = e.dataTransfer.getData('page');
            const draggedPage = pdfPages.find(p => p.dataset.page === page);
            box.appendChild(draggedPage);
        };
    });
}