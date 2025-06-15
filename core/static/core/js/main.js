document.addEventListener('DOMContentLoaded', function() {
    // Select the main container for the product detail page. If it doesn't exist, exit the script.
    const productDetailContainer = document.querySelector('.product-detail-grid');
    if (!productDetailContainer) {
        return;
    }

    // --- CACHE ALL NECESSARY DOM ELEMENTS ---
    const mainImage = document.getElementById('mainProductImage');
    const thumbnailContainer = document.getElementById('thumbnailContainer');
    const variantSelector = document.getElementById('variantSelector');
    const variantMap = JSON.parse(document.getElementById('variant-map-data').textContent);
    
    const priceElement = document.getElementById('buy-box-price');
    const stockElement = document.getElementById('buy-box-stock-status');
    const offerIdInput = document.getElementById('add-to-cart-offer-id');
    const addToCartButton = document.getElementById('add-to-cart-button');

    // --- IMAGE GALLERY HOVER LOGIC ---
    if (thumbnailContainer) {
        thumbnailContainer.addEventListener('mouseover', (event) => {
            if (event.target.classList.contains('thumbnail')) {
                mainImage.src = event.target.dataset.imageSrc;
                // Update active state for the border highlight
                document.querySelectorAll('.thumbnail.active').forEach(t => t.classList.remove('active'));
                event.target.classList.add('active');
            }
        });
    }

    // --- VARIANT SELECTION LOGIC ---
    if (variantSelector) {
        variantSelector.addEventListener('click', (event) => {
            // Only act if a variant button was clicked
            if (event.target.classList.contains('variant-option-btn')) {
                const button = event.target;
                const group = button.closest('.attribute-group');

                // Toggle the 'active' class for buttons within the same group
                const currentActive = group.querySelector('.active');
                if (currentActive) {
                    currentActive.classList.remove('active', 'btn-dark');
                    currentActive.classList.add('btn-outline-secondary');
                }
                button.classList.add('active', 'btn-dark');
                button.classList.remove('btn-outline-secondary');
                
                // Update the text showing the selected value
                const selectedValueEl = group.querySelector('.selected-value');
                if (selectedValueEl) {
                    selectedValueEl.textContent = button.textContent.trim();
                }

                findVariantAndUpdateUI();
            }
        });
    }

    function findVariantAndUpdateUI() {
        const selectedOptions = document.querySelectorAll('.variant-option-btn.active');
        const attributeGroups = document.querySelectorAll('.attribute-group');

        // Wait until an option from every attribute group is selected
        if (selectedOptions.length !== attributeGroups.length) {
            disableBuyBox("Please select all options.");
            return;
        }

        // Create a unique key based on the selected attributes to find the variant
        const selectedIds = Array.from(selectedOptions).map(btn => btn.dataset.valueId);
        selectedIds.sort((a, b) => a - b); // Sort numerically for a consistent key
        const variantKey = selectedIds.join('-');
        
        const variantId = variantMap[variantKey];

        if (variantId) {
            fetchVariantData(variantId);
        } else {
            disableBuyBox("This combination is currently unavailable.");
            // Optionally reset the image gallery to the parent product's default
            updateImageGallery(null, mainImage.dataset.defaultImage); 
        }
    }

    async function fetchVariantData(variantId) {
        try {
            const url = `/products/api/variant/${variantId}/`;
            const response = await fetch(url);
            // Always parse the JSON, as the view now always returns a 200 OK status
            const result = await response.json();

            // --- THIS IS THE KEY FIX ---
            // Check the 'status' field inside the JSON payload
            if (result.status === 'ok') {
                updateBuyBox(result);
                updateImageGallery(result.image_urls);
            } else if (result.status === 'unavailable') {
                disableBuyBox("This specific variant is currently unavailable.");
                updateImageGallery(result.image_urls);
            } else { // Handles the 'error' status from the API
                throw new Error(result.message || 'An unknown error occurred.');
            }
            
        } catch (error) {
            disableBuyBox("Error loading variant data.");
        }
    }

    function updateBuyBox(data) {
        priceElement.textContent = `$${data.price}`;
        offerIdInput.value = data.offer_id;
        
        if (data.in_stock) {
            stockElement.textContent = 'In Stock.';
            stockElement.style.color = 'green';
            addToCartButton.disabled = false;
            addToCartButton.textContent = 'Add to Cart';
        } else {
            disableBuyBox('Out of Stock.');
        }
    }

    function disableBuyBox(message) {
        priceElement.textContent = 'N/A';
        stockElement.textContent = message;
        stockElement.style.color = 'red';
        addToCartButton.disabled = true;
        addToCartButton.textContent = 'Unavailable';
        offerIdInput.value = '';
    }

    function updateImageGallery(imageUrls, defaultImageUrl = null) {
        if (!mainImage || !thumbnailContainer) return;
        thumbnailContainer.innerHTML = ''; // Clear old thumbnails
        
        const imagesToShow = imageUrls && imageUrls.length > 0 ? imageUrls : (defaultImageUrl ? [defaultImageUrl] : []);

        if (imagesToShow.length > 0) {
            mainImage.src = imagesToShow[0];
            imagesToShow.forEach((url, index) => {
                const img = document.createElement('img');
                img.src = url;
                img.classList.add('thumbnail');
                img.dataset.imageSrc = url;
                if (index === 0) {
                    img.classList.add('active');
                }
                thumbnailContainer.appendChild(img);
            });
        } else {
            // Final fallback to a placeholder if no images are available at all
            mainImage.src = "{% static 'images/no_image.png' %}";
        }
    }
});
