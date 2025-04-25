export function renderPDFPreview(file, container) {
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

export function renderPagePreview(page, container) {
    const scale = 1.5;
    const viewport = page.getViewport({ scale });
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');

    canvas.height = viewport.height;
    canvas.width = viewport.width;

    page.render({
        canvasContext: context,
        viewport: viewport
    }).promise.then(() => {
        container.appendChild(canvas);
    });
}