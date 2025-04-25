import { renderPagePreview } from './utils/pdfUtils.js';

const fileInput = document.getElementById('file-input');
const pageListContainer = document.getElementById('page-list');
const defaultText = document.getElementById('default-text');
const splitControls = document.getElementById('split-controls');
const splitButton = document.querySelector('.split-button');
const pageRangesInput = document.getElementById('page-ranges');
const totalPagesCount = document.getElementById('total-pages-count');

let totalPages = 0;

fileInput.addEventListener('change', handleFileSelect);
pageRangesInput?.addEventListener('input', validatePageRanges);

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;

    pageListContainer.innerHTML = '';
    splitControls.style.display = 'none';
    splitButton.disabled = true;

    const reader = new FileReader();
    reader.onload = function (e) {
        const pdfData = new Uint8Array(e.target.result);
        pdfjsLib.getDocument(pdfData).promise.then(pdf => {
            totalPages = pdf.numPages;
            totalPagesCount.textContent = totalPages;
            renderPDFPreviews(pdf);
            splitControls.style.display = 'block';
        });
    };
    reader.readAsArrayBuffer(file);
}

function renderPDFPreviews(pdf) {
    for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
        pdf.getPage(pageNum).then(page => {
            const pagePreview = document.createElement('div');
            pagePreview.classList.add('page-preview');

            const pageNumber = document.createElement('div');
            pageNumber.classList.add('page-number');
            pageNumber.textContent = `Page ${pageNum}`;
            pagePreview.appendChild(pageNumber);

            const previewContainer = document.createElement('div');
            previewContainer.classList.add('pdf-preview-container');
            pagePreview.appendChild(previewContainer);

            renderPagePreview(page, previewContainer);
            pageListContainer.appendChild(pagePreview);
        });
    }
}

function validatePageRanges(event) {
    const rangesText = event.target.value.trim();
    if (!rangesText) {
        splitButton.disabled = true;
        return;
    }

    try {
        const ranges = rangesText.split(',').map(range => range.trim());
        let valid = true;

        for (const range of ranges) {
            if (range.includes('-')) {
                const [start, end] = range.split('-').map(num => parseInt(num.trim()));
                if (isNaN(start) || isNaN(end) ||
                    start < 1 || start > totalPages ||
                    end < start || end > totalPages) {
                    valid = false;
                    break;
                }
            } else {
                const pageNum = parseInt(range);
                if (isNaN(pageNum) || pageNum < 1 || pageNum > totalPages) {
                    valid = false;
                    break;
                }
            }
        }

        splitButton.disabled = !valid;
        pageRangesInput.style.borderColor = valid ? '#2c3e50' : '#dc3545';
    } catch (e) {
        splitButton.disabled = true;
        pageRangesInput.style.borderColor = '#dc3545';
    }
}

const API_BASE_URL_SPLIT = 'http://localhost:5000/api/files';

document.getElementById('splitForm').addEventListener('submit', function (event) {
    event.preventDefault();

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('ranges', pageRangesInput.value);

    const jwtToken = localStorage.getItem('token');

    const headers = jwtToken ? {
        'Authorization': `Bearer ${jwtToken}`
    } : {};

    fetch(`${API_BASE_URL_SPLIT}/split`, {
        method: 'POST',
        headers: headers,
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.split_files) {
                data.split_files.forEach((fileUrl, index) => {
                    const downloadLink = document.createElement('a');
                    downloadLink.href = `${API_BASE_URL_SPLIT}${fileUrl}`;
                    downloadLink.download = `split_${index + 1}.pdf`;
                    downloadLink.target = '_blank';
                    document.body.appendChild(downloadLink);
                    downloadLink.click();
                    document.body.removeChild(downloadLink);
                });
                alert('PDF split successfully!');
            } else if (data.error) {
                alert(data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error splitting PDF');
        });
});