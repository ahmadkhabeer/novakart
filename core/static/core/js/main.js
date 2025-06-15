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
    const variantDataMap = JSON.parse(document.getElementById('variant-data-map').textContent);
    
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

                // If this button is already active, do nothing to prevent re-rendering.
                if (button.classList.contains('active')) {
                    return;
                }

                // De-select any other active button in the same group
                const currentActive = group.querySelector('.active');
                if (currentActive) {
                    currentActive.classList.remove('active', 'btn-dark');
                    currentActive.classList.add('btn-outline-secondary');
                }
                
                // Select the new button
                button.classList.add('active', 'btn-dark');
                button.classList.remove('btn-outline-secondary');
                
                // Update the text showing the selected value
                const selectedValueEl = group.querySelector('.selected-value');
                if (selectedValueEl) {
                    selectedValueEl.textContent = `: ${button.textContent.trim()}`;
                }

                findVariantAndUpdateUI();
            }
        });
    }

    function findVariantAndUpdateUI() {
        const selectedOptions = document.querySelectorAll('.variant-option-btn.active');
        const attributeGroups = document.querySelectorAll('.attribute-group');

        // Wait until an option from every attribute group is selected
        if (selectedOptions.length < attributeGroups.length) {
            disableBuyBox("Please select all options.");
            return;
        }

        // Create a unique key from the sorted IDs of the selected attributes
        const selectedIds = Array.from(selectedOptions).map(btn => btn.dataset.valueId);
        selectedIds.sort((a, b) => a - b); // Sort numerically for a consistent key
        const variantKey = selectedIds.join('-');
        
        // Look up the complete data for the variant from the pre-loaded map
        const variantData = variantDataMap[variantKey];

        if (variantData) {
            updateUI(variantData);
        } else {
            disableBuyBox("This combination is currently unavailable.");
            // Reset images to the parent product's default image if combination is invalid
            updateImageGallery(null, mainImage.dataset.defaultImage); 
        }
    }

    function updateUI(data) {
        // This is a wrapper function to update all parts of the page
        updateBuyBox(data);
        updateImageGallery(data.image_urls);
    }

    function updateBuyBox(data) {
        priceElement.textContent = data.price ? `$${data.price}` : 'N/A';
        offerIdInput.value = data.offer_id || '';
        
        if (data.in_stock) {
            stockElement.textContent = 'In Stock.';
            stockElement.style.color = 'green';
            addToCartButton.disabled = false;
            addToCartButton.textContent = 'Add to Cart';
        } else {
            // Handle both out of stock and variants with no offers
            disableBuyBox(data.price ? 'Out of Stock.' : 'Currently unavailable.');
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
        
        let imagesToShow = imageUrls;
        // If the variant has no specific images, fall back to the provided default (parent) image
        if (!imagesToShow || imagesToShow.length === 0) {
            imagesToShow = defaultImageUrl ? [defaultImageUrl] : [];
        }

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
            mainImage.src = mainImage.dataset.defaultImage;
        }
    }
});
