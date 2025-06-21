document.addEventListener('DOMContentLoaded', function() {
    const fruitSelect = document.getElementById('global-fruit-select');
    
    fruitSelect.addEventListener('change', function() {
        const selectedFruit = this.value;
        
        // Store selection in sessionStorage
        sessionStorage.setItem('selectedFruit', selectedFruit);
        
        // Update all iframes
        document.querySelectorAll('iframe').forEach(iframe => {
            iframe.contentWindow.postMessage({
                type: 'FRUIT_SELECTION',
                fruit: selectedFruit
            }, '*');
        });
        
        // You can also make an AJAX call to store server-side
        fetch('/set-fruit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ fruit: selectedFruit })
        });
    });
    
    // Initialize with stored value
    const storedFruit = sessionStorage.getItem('selectedFruit');
    if (storedFruit) {
        fruitSelect.value = storedFruit;
    }
});