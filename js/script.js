document.addEventListener('DOMContentLoaded', function() {
    // Hamburger menu toggle
    const hamburger = document.querySelector('.nav-hamburger');
    const navMenu = document.querySelector('.nav-menu');
    
    if (hamburger) {
        hamburger.addEventListener('click', function() {
            hamburger.classList.toggle('active');
            navMenu.classList.toggle('active');
        });
    }

    // Close menu when clicking a link
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            if (hamburger) hamburger.classList.remove('active');
            if (navMenu) navMenu.classList.remove('active');
        });
    });

    // File upload functionality for tool pages
    if (document.getElementById('file-upload')) {
        const fileInput = document.getElementById('file-upload');
        const previewContainer = document.getElementById('preview-container');
        const previewPlaceholder = previewContainer.querySelector('.preview-placeholder');
        
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (!file) return;
            
            // Check file type
            const validTypes = ['application/pdf', 'application/msword', 
                              'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
            if (!validTypes.includes(file.type)) {
                alert('Please upload only PDF or Word documents.');
                return;
            }
            
            // Check file size (5MB max)
            if (file.size > 5 * 1024 * 1024) {
                alert('File size exceeds 5MB limit.');
                return;
            }
            
            // Clear previous preview
            while (previewContainer.firstChild) {
                previewContainer.removeChild(previewContainer.firstChild);
            }
            
            // Create title
            const previewTitle = document.createElement('h4');
            previewTitle.textContent = 'File Preview';
            previewContainer.appendChild(previewTitle);
            
            if (file.type === 'application/pdf') {
                // PDF preview
                const objectEl = document.createElement('object');
                objectEl.data = URL.createObjectURL(file);
                objectEl.type = 'application/pdf';
                objectEl.width = '100%';
                objectEl.height = '500px';
                objectEl.style.borderRadius = '8px';
                objectEl.style.boxShadow = '0 4px 15px rgba(0,0,0,0.1)';
                previewContainer.appendChild(objectEl);
                
                // Add download button
                const downloadBtn = document.createElement('button');
                downloadBtn.className = 'download-btn';
                downloadBtn.innerHTML = '<i class="fas fa-download"></i> Download PDF';
                downloadBtn.onclick = function() {
                    const a = document.createElement('a');
                    a.href = URL.createObjectURL(file);
                    a.download = file.name;
                    a.click();
                };
                previewContainer.appendChild(downloadBtn);
            } else {
                // Word document - show file info
                const fileInfo = document.createElement('div');
                fileInfo.className = 'file-info';
                fileInfo.style.textAlign = 'center';
                fileInfo.innerHTML = `
                    <div style="font-size: 4rem; color: #2b579a; margin: 1rem 0;">
                        <i class="fas fa-file-word"></i>
                    </div>
                    <h3 style="margin-bottom: 0.5rem;">${file.name}</h3>
                    <p style="color: #95a5a6; margin-bottom: 1.5rem;">${(file.size / 1024).toFixed(2)} KB • Word Document</p>
                `;
                
                const downloadBtn = document.createElement('button');
                downloadBtn.className = 'download-btn';
                downloadBtn.innerHTML = '<i class="fas fa-download"></i> Download Document';
                downloadBtn.onclick = function() {
                    const a = document.createElement('a');
                    a.href = URL.createObjectURL(file);
                    a.download = file.name;
                    a.click();
                };
                
                previewContainer.appendChild(fileInfo);
                previewContainer.appendChild(downloadBtn);
            }
        });
    }
});