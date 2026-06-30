/**
 * AI-Powered Resume Ranker Client Script
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // --- Loader Actions ---
    const showLoaderForms = document.querySelectorAll('.show-loader-on-submit');
    showLoaderForms.forEach(function(form) {
        form.addEventListener('submit', function() {
            showLoader();
        });
    });

    // --- Search & Filter Tables ---
    const searchInput = document.getElementById('searchCandidate');
    const filterStatus = document.getElementById('filterStatus');
    const rankTableBody = document.querySelector('.filterable-table tbody');

    if (searchInput || filterStatus) {
        const rows = rankTableBody.querySelectorAll('tr');

        const filterTable = function() {
            const query = searchInput ? searchInput.value.toLowerCase().trim() : '';
            const selectedStatus = filterStatus ? filterStatus.value.toLowerCase() : '';

            rows.forEach(function(row) {
                const nameText = row.querySelector('.candidate-name').textContent.toLowerCase();
                const statusText = row.querySelector('.badge-status').textContent.toLowerCase();
                
                const matchesSearch = nameText.includes(query);
                const matchesStatus = selectedStatus === '' || statusText === selectedStatus;

                if (matchesSearch && matchesStatus) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        };

        if (searchInput) {
            searchInput.addEventListener('input', filterTable);
        }
        if (filterStatus) {
            filterStatus.addEventListener('change', filterTable);
        }
    }

    // --- Auto-fade Bootstrap Alerts ---
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 5000);
    });
});

/**
 * Display the loading spinner overlay
 */
function showLoader() {
    // Check if loader already exists
    if (document.getElementById('globalLoader')) return;

    const overlay = document.createElement('div');
    overlay.id = 'globalLoader';
    overlay.className = 'loading-overlay';
    overlay.innerHTML = `
        <div class="text-center text-white">
            <div class="spinner-border text-primary loading-spinner mb-3" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <h5 class="fw-semibold">Processing PDF & running NLP pipeline...</h5>
            <p class="text-light small">Please wait, analyzing candidates similarity scores.</p>
        </div>
    `;
    document.body.appendChild(overlay);
}

/**
 * Confirm delete item
 */
function confirmDelete(event, itemName) {
    if (!confirm(`Are you sure you want to delete ${itemName || 'this item'}? This action cannot be undone.`)) {
        event.preventDefault();
        return false;
    }
    return true;
}
