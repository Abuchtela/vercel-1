document.addEventListener('DOMContentLoaded', function() {
    const button = document.getElementById('clickBtn');
    const message = document.getElementById('message');
    let clickCount = 0;

    button.addEventListener('click', function() {
        clickCount++;
        message.textContent = `Button clicked ${clickCount} time${clickCount !== 1 ? 's' : ''}!`;
    });
});
