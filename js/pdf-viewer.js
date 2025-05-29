class PDFViewer {
    constructor() {
        this.pdfDoc = null;
        this.currentPage = 1;
        this.scale = 1.0;
        this.initElements();
        this.loadDocument();
    }
    
    initElements() {
        this.canvas = document.getElementById('pdf-render');
        this.ctx = this.canvas.getContext('2d');
        this.documentPreview = document.getElementById('document-preview');
    }
    
    loadDocument() {
        const storedDoc = sessionStorage.getItem('currentDocument');
        if (!storedDoc) {
            alert('No document found. Please upload a document first.');
            window.location.href = 'hand-gestures.html';
            return;
        }

        const docInfo = JSON.parse(storedDoc);
        
        // Show preview
        if (docInfo.preview) {
            this.documentPreview.innerHTML = docInfo.preview;
        }
        
        // Initialize PDF.js
        pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://mozilla.github.io/pdf.js/build/pdf.worker.js';
        
        // Load PDF document
        pdfjsLib.getDocument(docInfo.url).promise.then(pdf => {
            this.pdfDoc = pdf;
            this.renderPage(this.currentPage);
        }).catch(err => {
            console.error('PDF loading error:', err);
            alert('Error loading PDF document');
        });
    }
    
    renderPage(pageNum) {
        if (!this.pdfDoc) return;
        
        this.currentPage = Math.max(1, Math.min(pageNum, this.pdfDoc.numPages));
        
        this.pdfDoc.getPage(this.currentPage).then(page => {
            const viewport = page.getViewport({ scale: this.scale });
            this.canvas.height = viewport.height;
            this.canvas.width = viewport.width;
            
            const renderContext = {
                canvasContext: this.ctx,
                viewport: viewport
            };
            
            page.render(renderContext);
        });
    }
    
    zoomIn() {
        const settings = window.gestureControls.getSettings();
        this.scale = Math.min(this.scale + (0.25 * (settings.zoomSpeed / 50)), 3.0);
        this.renderPage(this.currentPage);
    }
    
    zoomOut() {
        const settings = window.gestureControls.getSettings();
        this.scale = Math.max(this.scale - (0.25 * (settings.zoomSpeed / 50)), 0.5);
        this.renderPage(this.currentPage);
    }
    
    prevPage() {
        if (this.currentPage > 1) {
            this.renderPage(this.currentPage - 1);
        }
    }
    
    nextPage() {
        if (this.pdfDoc && this.currentPage < this.pdfDoc.numPages) {
            this.renderPage(this.currentPage + 1);
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.pdfViewer = new PDFViewer();
});