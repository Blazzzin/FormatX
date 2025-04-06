const fileInput = document.getElementById('file-input');
const pageListContainer = document.getElementById('page-list');
const defaultText = document.getElementById('default-text');
const organizeButton = document.querySelector('.organize-button');

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

                    renderPDFPreview(page, previewContainer);

                    pageListContainer.appendChild(pageItem);
                    pagesList.push(pageNum);

                    enableDragAndDrop();
                    organizeButton.disabled = false;
                });
            }
        });
    };
    reader.readAsArrayBuffer(file);
}

function renderPDFPreview(page, container) {
    const scale = 1.5;
    const viewport = page.getViewport({ scale });
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');

    canvas.height = viewport.height;
    canvas.width = viewport.width;
    page.render({ canvasContext: context, viewport }).promise.then(() => {
        container.appendChild(canvas);
    });
}

function enableDragAndDrop() {
    new Sortable(pageListContainer, {
        animation: 150,
        onEnd: () => {
            pagesList = Array.from(pageListContainer.children).map(item => parseInt(item.dataset.pageNum));
        }
    });
}

const API_BASE_URL_ORG = 'http://localhost:5000/api/files';

document.getElementById('organizeForm').addEventListener('submit', function (event) {
    event.preventDefault();

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('pages', JSON.stringify(pagesList));

    const jwtToken = localStorage.getItem('token');

    const headers = jwtToken ? {
        'Authorization': `Bearer ${jwtToken}`
    } : {};

    fetch(`${API_BASE_URL_ORG}/organize`, {
        method: 'POST',
        headers: headers,
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.organized_file_url) {
                const downloadLink = document.createElement('a');
                downloadLink.href = `${API_BASE_URL_ORG}${data.organized_file_url}`;
                downloadLink.download = 'organized_output.pdf';
                downloadLink.target = '_blank';
                document.body.appendChild(downloadLink);
                downloadLink.click();
                document.body.removeChild(downloadLink);
                alert('PDF reorganized successfully!');
            } else if (data.error) {
                alert(data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error reorganizing PDF');
        });
});