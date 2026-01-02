// HTMX event handlers
document.body.addEventListener('htmx:afterRequest', function(evt) {
    // Handle successful form submissions
    if (evt.detail.successful) {
        // Reset forms after successful submission
        if (evt.detail.elt.tagName === 'FORM') {
            evt.detail.elt.reset();
        }
    }
});
