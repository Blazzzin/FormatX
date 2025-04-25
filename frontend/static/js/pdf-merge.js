import { renderPDFPreview } from './utils/pdfUtils.js';
import { enableDragAndDrop } from './utils/dragUtils.js';

const MAX_FILES = 20;
let filesList = [];

const fileInput = document.getElementById('file-input');
const fileListContainer = document.getElementById('file-list');
const defaultText = document.getElementById('default-text');
const fileLimitMessage = document.getElementById('file-limit-message');
const mergeButton = document.querySelector('.merge-button');

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

            const removeButton = document.createElement('button');
            removeButton.classList.add('remove-file');
            removeButton.textContent = 'X';
            removeButton.title = 'Remove this file';

            removeButton.addEventListener('click', () => {
                filesList = filesList.filter(f => f.name !== file.name);
                fileItem.remove();
                if (filesList.length === 0) {
                    window.location.reload();
                }
                mergeButton.disabled = filesList.length === 0;
            });

            fileItem.appendChild(removeButton);

            const previewContainer = document.createElement('div');
            previewContainer.classList.add('pdf-preview-container');
            fileItem.appendChild(previewContainer);

            fileItem.file = file;
            fileListContainer.appendChild(fileItem);

            renderPDFPreview(file, previewContainer);
        }
    });

    enableDragAndDrop(fileListContainer, () => {
        filesList = Array.from(fileListContainer.children).map(item => item.file);
    });
    mergeButton.disabled = filesList.length === 0;
}

const API_BASE_URL_MERGE = 'http://localhost:5000/api/files';

document.getElementById('mergeForm').addEventListener('submit', function (event) {
    event.preventDefault();

    const formData = new FormData();
    filesList.forEach(file => formData.append('files[]', file));

    const jwtToken = localStorage.getItem('token');

    const headers = jwtToken ? {
        'Authorization': `Bearer ${jwtToken}`
    } : {};

    fetch(`${API_BASE_URL_MERGE}/merge`, {
        method: 'POST',
        headers: headers,
        body: formData
    })
        .then(response => {
            console.log('Response status:', response.status);
            return response.json();
        })
        .then(data => {
            if (data.merged_file_url) {
                const downloadLink = document.createElement('a');
                downloadLink.href = `${API_BASE_URL_MERGE}${data.merged_file_url}`;
                downloadLink.download = 'merged_output.pdf';
                downloadLink.target = '_blank';
                document.body.appendChild(downloadLink);
                downloadLink.click();
                document.body.removeChild(downloadLink);
                alert('PDFs merged successfully!');
            } else if (data.error) {
                alert(data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error merging PDFs');
        });
});