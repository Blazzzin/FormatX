import { renderPagePreview } from './utils/pdfUtils.js';
import { enableDragAndDrop } from './utils/dragUtils.js';
import { handleDownloadFlow } from './utils/fileUtils.js';

const fileInput = document.getElementById('file-input');
const pageListContainer = document.getElementById('page-list');
const defaultText = document.getElementById('default-text');
const organizeButton = document.querySelector('.organize-button');
const loadingSpinner = document.getElementById('loading-spinner');
const downloadContainer = document.getElementById('download-container');
const downloadLink = document.getElementById('download-link');

let pagesList = [];

fileInput.addEventListener('change', handleFileSelect);

function handleFileSelect(event) {
    pageListContainer.innerHTML = '';
    pagesList = [];

    const file = event.target.files[0];
    if (!file) return;

    const existingDefaultText = document.getElementById('default-text');
    if (existingDefaultText) {
        existingDefaultText.remove();
    }

    renderPDFPages(file);
}

function renderPDFPages(file) {
    const reader = new FileReader();
    reader.onload = function (e) {
        const pdfData = new Uint8Array(e.target.result);
        pdfjsLib.getDocument(pdfData).promise.then(pdf => {
            for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
                pdf.getPage(pageNum).then(page => {
                    const pageItem = document.createElement('div');
                    pageItem.classList.add('page-item');
                    pageItem.dataset.pageNum = pageNum;

                    const previewContainer = document.createElement('div');
                    previewContainer.classList.add('pdf-preview-container');
                    pageItem.appendChild(previewContainer);

                    const removeButton = document.createElement('button');
                    removeButton.classList.add('remove-page');
                    removeButton.textContent = 'X';
                    removeButton.title = 'Remove this page';
                    removeButton.addEventListener('click', () => {
                        pagesList = pagesList.filter(p => p !== pageNum);
                        pageItem.remove();
                        if (pagesList.length === 0) {
                            window.location.reload();
                        }
                        organizeButton.disabled = pagesList.length === 0;
                    });
                    pageItem.appendChild(removeButton);

                    renderPagePreview(page, previewContainer);

                    pageListContainer.appendChild(pageItem);
                    pagesList.push(pageNum);

                    enableDragAndDrop(pageListContainer, () => {
                        pagesList = Array.from(pageListContainer.children).map(item => parseInt(item.dataset.pageNum));
                    });
                    organizeButton.disabled = false;
                });
            }
        });
    };
    reader.readAsArrayBuffer(file);
}

const API_BASE_URL_ORG = 'http://localhost:5000/api/files';

document.getElementById('organizeForm').addEventListener('submit', async function (event) {
    event.preventDefault();

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('pages', JSON.stringify(pagesList));

    const jwtToken = localStorage.getItem('token');

    const headers = jwtToken ? {
        'Authorization': `Bearer ${jwtToken}`
    } : {};

    const fetchPromise = fetch(`${API_BASE_URL_ORG}/organize`, {
        method: 'POST',
        headers: headers,
        body: formData
    }).then(response => response.json());

    await handleDownloadFlow({
        fetchPromise,
        downloadContainer,
        spinner: loadingSpinner,
        button: organizeButton,
        downloadLink,
        responseKey: 'organized_file_url'
    });
});