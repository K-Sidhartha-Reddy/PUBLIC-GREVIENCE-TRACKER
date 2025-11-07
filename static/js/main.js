// Main JavaScript for Public Grievance & Digital Governance Portal

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Form validation
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // File upload preview
    var fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(function(input) {
        input.addEventListener('change', function(e) {
            var file = e.target.files[0];
            if (file) {
                // Check file size (5MB limit)
                if (file.size > 5 * 1024 * 1024) {
                    alert('File size must be less than 5MB');
                    input.value = '';
                    return;
                }

                // Check file type
                if (!file.type.startsWith('image/')) {
                    alert('Please select an image file');
                    input.value = '';
                    return;
                }

                // Show preview
                var preview = document.getElementById('imagePreview');
                if (preview) {
                    var reader = new FileReader();
                    reader.onload = function(e) {
                        preview.src = e.target.result;
                        preview.style.display = 'block';
                    };
                    reader.readAsDataURL(file);
                }
            }
        });
    });

    // Search functionality
    var searchInputs = document.querySelectorAll('.search-input');
    searchInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            var searchTerm = this.value.toLowerCase();
            var targetElements = document.querySelectorAll(this.dataset.target);
            
            targetElements.forEach(function(element) {
                var text = element.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    element.style.display = '';
                } else {
                    element.style.display = 'none';
                }
            });
        });
    });

    // Smooth scrolling for anchor links
    var anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            var target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add loading state to forms
    var forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function() {
            var submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                var originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<span class="loading"></span> Processing...';
                submitBtn.disabled = true;
                
                // Re-enable after 10 seconds (fallback)
                setTimeout(function() {
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                }, 10000);
            }
        });
    });

    // Initialize charts if Chart.js is available
    if (typeof Chart !== 'undefined') {
        initializeCharts();
    }

    // Add animation classes to elements
    addAnimationClasses();

    // Initialize location-based features
    initializeLocationFeatures();
});

// Chart initialization
function initializeCharts() {
    // Status distribution chart
    var statusCtx = document.getElementById('statusChart');
    if (statusCtx) {
        new Chart(statusCtx, {
            type: 'doughnut',
            data: {
                labels: ['Pending', 'In Progress', 'Resolved'],
                datasets: [{
                    data: [30, 20, 50],
                    backgroundColor: ['#ffc107', '#17a2b8', '#28a745'],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    }
                }
            }
        });
    }

    // Monthly trends chart
    var trendsCtx = document.getElementById('trendsChart');
    if (trendsCtx) {
        new Chart(trendsCtx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Complaints Submitted',
                    data: [12, 19, 3, 5, 2, 3],
                    borderColor: '#007bff',
                    backgroundColor: 'rgba(0, 123, 255, 0.1)',
                    tension: 0.4,
                    fill: true
                }, {
                    label: 'Complaints Resolved',
                    data: [8, 15, 2, 4, 1, 2],
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                plugins: {
                    legend: {
                        position: 'top'
                    }
                }
            }
        });
    }
}

// Add animation classes to elements
function addAnimationClasses() {
    var observer = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, {
        threshold: 0.1
    });

    var animatedElements = document.querySelectorAll('.card, .alert, .btn');
    animatedElements.forEach(function(element) {
        observer.observe(element);
    });
}

// Location-based features
function initializeLocationFeatures() {
    // Get user's location (if permission granted)
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            var lat = position.coords.latitude;
            var lon = position.coords.longitude;
            
            // You can use this to auto-populate location fields
            console.log('User location:', lat, lon);
        }, function(error) {
            console.log('Geolocation error:', error);
        });
    }

    // Location selection handlers
    var stateSelect = document.getElementById('state');
    var districtSelect = document.getElementById('district');
    var villageSelect = document.getElementById('village');

    if (stateSelect && districtSelect && villageSelect) {
        stateSelect.addEventListener('change', function() {
            updateDistricts(this.value);
        });

        districtSelect.addEventListener('change', function() {
            updateVillages(stateSelect.value, this.value);
        });

        villageSelect.addEventListener('change', function() {
            updateAreaInfo(stateSelect.value, districtSelect.value, this.value);
        });
    }
}

// Update districts based on state selection
function updateDistricts(state) {
    var districtSelect = document.getElementById('district');
    if (!districtSelect) return;

    // Clear existing options
    districtSelect.innerHTML = '<option value="">Select District</option>';

    if (state === 'Telangana') {
        var districts = ['Hyderabad', 'Rangareddy', 'Medchal-Malkajgiri', 'Sangareddy', 'Vikarabad'];
        districts.forEach(function(district) {
            var option = document.createElement('option');
            option.value = district;
            option.textContent = district;
            districtSelect.appendChild(option);
        });
    }
}

// Update villages based on state and district selection
function updateVillages(state, district) {
    var villageSelect = document.getElementById('village');
    if (!villageSelect) return;

    // Clear existing options
    villageSelect.innerHTML = '<option value="">Select Village/Locality</option>';

    if (state === 'Telangana' && district === 'Hyderabad') {
        var villages = [
            'Amberpet', 'Tirumalagiri', 'Bandlaguda', 'Maredpalle',
            'Secunderabad', 'Charminar', 'Banjara Hills', 'Jubilee Hills',
            'Himayatnagar', 'Kukatpally', 'Kondapur', 'Gachibowli'
        ];
        villages.forEach(function(village) {
            var option = document.createElement('option');
            option.value = village;
            option.textContent = village;
            villageSelect.appendChild(option);
        });
    }
}

// Update area information based on location selection
function updateAreaInfo(state, district, village) {
    var areaInfo = document.getElementById('areaInfo');
    var areaDetails = document.getElementById('areaDetails');
    
    if (!areaInfo || !areaDetails) return;

    if (state && district && village) {
        // Determine area type based on village selection
        var urbanAreas = ['Amberpet', 'Secunderabad', 'Charminar', 'Banjara Hills', 'Jubilee Hills', 'Himayatnagar', 'Kukatpally', 'Kondapur', 'Gachibowli'];
        var isUrban = urbanAreas.includes(village);
        
        var areaType = isUrban ? 'Urban' : 'Rural';
        var authority = isUrban ? 'Greater Hyderabad Municipal Corporation' : village + ' Gram Panchayat';
        var responseTime = isUrban ? '7-10 working days' : '10-15 working days';
        
        var details = `
            <div class="row">
                <div class="col-md-6">
                    <p><strong>Area Type:</strong> ${areaType}</p>
                    <p><strong>Governing Authority:</strong> ${authority}</p>
                </div>
                <div class="col-md-6">
                    <p><strong>Expected Response Time:</strong> ${responseTime}</p>
                    <p><strong>Services Available:</strong> ${isUrban ? 'Municipal Services, Urban Development' : 'Panchayat Services, Rural Development, Welfare Schemes'}</p>
                </div>
            </div>
        `;
        
        areaDetails.innerHTML = details;
        areaInfo.style.display = 'block';
    } else {
        areaInfo.style.display = 'none';
    }
}

// Utility functions
function showNotification(message, type = 'info') {
    var alertClass = 'alert-' + type;
    var alertHtml = `
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    var container = document.querySelector('.container');
    if (container) {
        container.insertAdjacentHTML('afterbegin', alertHtml);
        
        // Auto-hide after 5 seconds
        setTimeout(function() {
            var alert = container.querySelector('.alert');
            if (alert) {
                var bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    }
}

function formatDate(dateString) {
    var date = new Date(dateString);
    return date.toLocaleDateString('en-IN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

function formatDateTime(dateString) {
    var date = new Date(dateString);
    return date.toLocaleString('en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Export functions for global use
window.PortalUtils = {
    showNotification: showNotification,
    formatDate: formatDate,
    formatDateTime: formatDateTime,
    updateAreaInfo: updateAreaInfo
};

