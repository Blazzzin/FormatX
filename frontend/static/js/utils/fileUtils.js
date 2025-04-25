export async function handleDownloadFlow({
    fetchPromise,
    downloadContainer,
    spinner,
    mergeButton,
    downloadLink,
}) {
    try {
        spinner.style.display = 'block';
        mergeButton.disabled = true;
        downloadContainer.style.display = 'none';

        const data = await fetchPromise;

        spinner.style.display = 'none';

        if (data && data.merged_file_url) {
            downloadContainer.style.display = 'block';
            downloadLink.href = `http://localhost:5000/api/files${data.merged_file_url}`;
            downloadLink.target = '_blank';
            downloadLink.removeAttribute('download');
            mergeButton.disabled = false;
        } else if (data && data.error) {
            alert(data.error);
            mergeButton.disabled = false;
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An unexpected error occurred.');
        spinner.style.display = 'none';
        mergeButton.disabled = false;
    }
}