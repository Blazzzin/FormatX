import { handleDownloadFlow } from './utils/fileUtils.js';

const MAX_FILES = 20;
let filesList = [];

const fileInput = document.getElementById('file-input');
const fileListContainer = document.getElementById('file-list');
const defaultText = document.getElementById('default-text');
const fileLimitMessage = document.getElementById('file-limit-message');
const convertButton = document.querySelector('.convert-button');
const loadingSpinner = document.getElementById('loading-spinner');
const downloadContainer = document.getElementById('download-container');
const downloadLink = document.getElementById('download-link');

fileInput.addEventListener('change', handleFileSelect);

function handleFileSelect(event) {
    const files = Array.from(event.target.files);

    if (filesList.length + files.length > MAX_FILES) {
        fileLimitMessage.style.display = 'block';
        return;
    }

    fileLimitMessage.style.display = 'none';

    const existingDefaultText = document.getElementById('default-text');
    if (existingDefaultText) {
        existingDefaultText.remove();
    }

    files.forEach(file => {
        if (!filesList.some(existingFile => existingFile.name === file.name)) {
            filesList.push(file);

            const fileItem = document.createElement('div');
            fileItem.classList.add('file-item');
            fileItem.textContent = file.name;
            fileItem.dataset.index = filesList.length - 1;

            const removeButton = document.createElement('button');
            removeButton.classList.add('remove-file');
            removeButton.textContent = 'X';
            removeButton.title = 'Remove this file';

            removeButton.addEventListener('click', () => {
                const index = filesList.indexOf(file);
                if (index > -1) {
                    filesList.splice(index, 1);
                }
                fileItem.remove();
                if (filesList.length === 0) {
                    window.location.reload();
                }
                convertButton.disabled = filesList.length === 0;
            });

            fileItem.appendChild(removeButton);

            const previewContainer = document.createElement('div');
            previewContainer.classList.add('pdf-preview-container');

            const icon = document.createElement('img');
            icon.src = '../static/assets/ppt-icon.png';
            icon.alt = 'Word Icon';
            icon.style.width = '60px';
            icon.style.height = '80px';
            icon.style.objectFit = 'contain';
            icon.style.marginTop = '40px';

            previewContainer.appendChild(icon);
            fileItem.appendChild(previewContainer);

            fileItem.file = file;
            fileListContainer.appendChild(fileItem);
        }
    });

    convertButton.disabled = filesList.length === 0;
}

const API_BASE_URL = 'http://localhost:5000/api/files';

document.getElementById('PPTtoPDFForm').addEventListener('submit', async function (event) {
    event.preventDefault();

    const formData = new FormData();
    filesList.forEach(file => formData.append('files[]', file));

    const jwtToken = localStorage.getItem('token');
    const headers = jwtToken ? { 'Authorization': `Bearer ${jwtToken}` } : {};

    const fetchPromise = fetch(`${API_BASE_URL}/convert/ppt-to-pdf`, {
        method: 'POST',
        headers: headers,
        body: formData
    }).then(response => response.json());

    await handleDownloadFlow({
        fetchPromise,
        downloadContainer,
        spinner: loadingSpinner,
        button: convertButton,
        downloadLink,
    });
});