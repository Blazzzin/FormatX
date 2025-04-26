export async function handleDownloadFlow({
    fetchPromise,
    downloadContainer,
    spinner,
    button,
    downloadLink,
}) {
    try {
        spinner.style.display = 'block';
        button.disabled = true;
        downloadContainer.style.display = 'none';

        const data = await fetchPromise;

        spinner.style.display = 'none';

        if (data) {
            let filePath = null;

            if (data.file_url) {
                filePath = data.file_url;
                downloadLink.textContent = 'Download File';
            } else if (data.zip_url) {
                filePath = data.zip_url;
                downloadLink.textContent = 'Download ZIP';
            }

            if (filePath) {
                downloadContainer.style.display = 'block';
                downloadLink.href = `http://localhost:5000/api/files${filePath}`;
                downloadLink.target = '_blank';
                downloadLink.removeAttribute('download');
            } else if (data.error) {
                alert(data.error);
            }

            button.disabled = false;
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An unexpected error occurred.');
        spinner.style.display = 'none';
        button.disabled = false;
    }
}