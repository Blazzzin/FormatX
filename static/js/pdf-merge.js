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

            // Add "X" button to remove the file
            const removeButton = document.createElement('button');
            removeButton.classList.add('remove-file');
            removeButton.textContent = 'X';
            removeButton.title = 'Remove this file';

            // Remove the file when the "X" button is clicked
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

    enableDragAndDrop();
    mergeButton.disabled = filesList.length === 0;
}

function renderPDFPreview(file, container) {
    if (file.type !== 'application/pdf') return;

    const reader = new FileReader();
    reader.onload = function (e) {
        const pdfData = new Uint8Array(e.target.result);
        pdfjsLib.getDocument(pdfData).promise.then(pdf => {
            pdf.getPage(1).then(page => {
                const scale = 1.5;
                const viewport = page.getViewport({ scale });
                const canvas = document.createElement('canvas');
                const context = canvas.getContext('2d');

                canvas.height = viewport.height;
                canvas.width = viewport.width;
                page.render({ canvasContext: context, viewport }).promise.then(() => {
                    container.appendChild(canvas);
                });
            });
        });
    };
    reader.readAsArrayBuffer(file);
}

function enableDragAndDrop() {
    new Sortable(fileListContainer, {
        animation: 150,
        onEnd: () => {
            filesList = Array.from(fileListContainer.children).map(item => item.file);
        }
    });
}

document.getElementById('mergeForm').addEventListener('submit', function (event) {
    event.preventDefault();

    const formData = new FormData();
    filesList.forEach(file => formData.append('files[]', file));

    fetch('/pdf-merge', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.merged_file_url) {
                const downloadLink = document.createElement('a');
                downloadLink.href = data.merged_file_url;
                downloadLink.download = 'merged_output.pdf';
                downloadLink.click();
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