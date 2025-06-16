document.addEventListener('DOMContentLoaded', function() {
    const productDetailContainer = document.querySelector('.product-detail-grid');
    if (!productDetailContainer) return;

    // --- CACHE DOM ELEMENTS & DATA ---
    const mainImage = document.getElementById('mainProductImage');
    const thumbnailContainer = document.getElementById('thumbnailContainer');
    const variantSelector = document.getElementById('variantSelector');
    const variantDataMap = JSON.parse(document.getElementById('variant-data-map').textContent);
    
    const priceElement = document.getElementById('buy-box-price');
    const stockElement = document.getElementById('buy-box-stock-status');
    const offerIdInput = document.getElementById('add-to-cart-offer-id');
    const addToCartButton = document.getElementById('add-to-cart-button');

    // --- VARIANT SELECTION LOGIC ---
    if (variantSelector) {
        variantSelector.addEventListener('click', (event) => {
            if (event.target.classList.contains('variant-option-btn')) {
                const button = event.target;
                const group = button.closest('.attribute-group');

                // Toggle active state for buttons within the same group
                const currentActive = group.querySelector('.active');
                if (currentActive) {
                    currentActive.classList.remove('active', 'btn-dark');
                    currentActive.classList.add('btn-outline-secondary');
                }
                button.classList.add('active', 'btn-dark');
                button.classList.remove('btn-outline-secondary');
                
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

        if (selectedOptions.length < attributeGroups.length) {
            disableBuyBox("Please select all options.");
            return;
        }

        const selectedIds = Array.from(selectedOptions).map(btn => btn.dataset.valueId);
        selectedIds.sort((a, b) => a - b);
        const variantKey = selectedIds.join('-');
        
        const variantData = variantDataMap[variantKey];

        if (variantData) {
            updateUI(variantData);
        } else {
            disableBuyBox("This combination is currently unavailable.");
            updateImageGallery(null, mainImage.dataset.defaultImage); 
        }
    }

    function updateUI(data) {
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
        thumbnailContainer.innerHTML = '';
        
        let imagesToShow = imageUrls;
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
                if (index === 0) img.classList.add('active');
                thumbnailContainer.appendChild(img);
            });
        } else {
            mainImage.src = mainImage.dataset.defaultImage;
        }
    }
    
    // Image gallery hover logic
    if (thumbnailContainer) {
        thumbnailContainer.addEventListener('mouseover', (event) => {
            if (event.target.classList.contains('thumbnail')) {
                mainImage.src = event.target.dataset.imageSrc;
                document.querySelectorAll('.thumbnail.active').forEach(t => t.classList.remove('active'));
                event.target.classList.add('active');
            }
        });
    }
});
