export function enableDragAndDrop(container, onUpdateCallback) {
    new Sortable(container, {
        animation: 150,
        onEnd: onUpdateCallback
    });
}