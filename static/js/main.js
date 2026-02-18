document.addEventListener('DOMContentLoaded', () => {
    // --- Existing Functionality: Image Upload & Filters ---
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('image-upload');
    const controls = document.getElementById('controls');
    const previewSection = document.getElementById('preview-section');
    const originalPreview = document.getElementById('original-preview');
    const processedPreview = document.getElementById('processed-preview');
    const loadingOverlay = document.getElementById('loading');
    const downloadBtn = document.getElementById('download-btn');
    const actionButtons = document.getElementById('action-buttons');
    const styleButtons = document.querySelectorAll('.style-btn');

    let currentFile = null;

    if (uploadArea && fileInput) {
        // Handle File Selection
        uploadArea.addEventListener('click', () => fileInput.click());

        fileInput.addEventListener('change', (e) => {
            if (e.target.files && e.target.files[0]) {
                handleFile(e.target.files[0]);
            }
        });

        // Drag and Drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                handleFile(e.dataTransfer.files[0]);
            }
        });
    }

    function handleFile(file) {
        if (!file.type.startsWith('image/')) {
            alert('Please upload a valid image file.');
            return;
        }
        currentFile = file;

        // Show original preview
        const reader = new FileReader();
        reader.onload = (e) => {
            if (originalPreview && processedPreview) {
                originalPreview.src = e.target.result;
                processedPreview.src = e.target.result; // Initially same
                previewSection.classList.remove('hidden');
                controls.classList.remove('disabled');

                // Trigger default process (Original)
                processImage('original');
            }
        };
        reader.readAsDataURL(file);
    }

    // Handle Style Selection
    styleButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            // Update UI
            styleButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const style = btn.dataset.style;
            processImage(style);
        });
    });

    function processImage(style) {
        if (!currentFile) return;

        // Show loading
        if (loadingOverlay) loadingOverlay.classList.remove('hidden');
        if (actionButtons) actionButtons.classList.add('hidden'); // Hide download until ready

        const formData = new FormData();
        formData.append('image', currentFile);
        formData.append('style', style);

        fetch('/process', {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                    if (data.redirect) {
                        window.location.href = data.redirect;
                    }
                    return;
                }

                // Update processed image
                if (processedPreview) processedPreview.src = data.image;
                if (downloadBtn) downloadBtn.href = data.image;

                // Show result
                if (loadingOverlay) loadingOverlay.classList.add('hidden');
                if (actionButtons) actionButtons.classList.remove('hidden');
            })
            .catch(err => {
                console.error(err);
                alert('Failed to process image.');
                if (loadingOverlay) loadingOverlay.classList.add('hidden');
            });
    }

    // --- New Feature: Interactive Background Dots ---
    createInteractiveDots();
});

function createInteractiveDots() {
    const dotsCount = 40;
    const dots = [];
    const container = document.body;

    // Remove existing dots if any
    document.querySelectorAll('.cursor-dot').forEach(d => d.remove());

    for (let i = 0; i < dotsCount; i++) {
        const dot = document.createElement('div');
        dot.className = 'cursor-dot';
        container.appendChild(dot);

        // Random sizes
        const size = Math.random() * 8 + 5;
        dot.style.width = `${size}px`;
        dot.style.height = `${size}px`;

        // Start position (center screen)
        const startX = window.innerWidth / 2;
        const startY = window.innerHeight / 2;

        // Initial transform
        dot.style.transform = `translate(${startX}px, ${startY}px)`;

        dots.push({
            element: dot,
            x: startX,
            y: startY,
            // Offset defines the "shape" of the swarm around the cursor
            offsetX: (Math.random() - 0.5) * 150,
            offsetY: (Math.random() - 0.5) * 150,
            // Speed defines how quickly they catch up (creates depth/lag)
            speed: 0.03 + Math.random() * 0.07
        });
    }

    let mouseX = window.innerWidth / 2;
    let mouseY = window.innerHeight / 2;

    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
    });

    function animate() {
        const time = Date.now() * 0.002;

        dots.forEach((dot, index) => {
            // Add dynamic floating movement so the swarm feels alive
            const floatX = Math.sin(time + index) * 30;
            const floatY = Math.cos(time + index * 0.5) * 30;

            // Target is mouse position + static offset + dynamic float
            const targetX = mouseX + dot.offsetX + floatX;
            const targetY = mouseY + dot.offsetY + floatY;

            // Linear Interpolation (Lerp) for smooth following
            // Current = Current + (Target - Current) * Factor
            dot.x += (targetX - dot.x) * dot.speed;
            dot.y += (targetY - dot.y) * dot.speed;

            dot.element.style.transform = `translate(${dot.x}px, ${dot.y}px)`;
        });

        requestAnimationFrame(animate);
    }
    animate();
}

// --- New Feature: Floating Background Shapes ---
// --- New Feature: Floating Background Shapes ---
function createBackgroundShapes() {
    const shapeCount = 8;
    const colors = ['#FF6B6B', '#4ECDC4', '#FFE66D', '#ff7675', '#74b9ff'];
    const shapes = [];

    // Create shapes
    for (let i = 0; i < shapeCount; i++) {
        const shape = document.createElement('div');
        shape.className = 'bg-shape';

        const size = Math.random() * 200 + 100;
        const color = colors[Math.floor(Math.random() * colors.length)];

        // Initial Position
        const x = Math.random() * window.innerWidth;
        const y = Math.random() * window.innerHeight;

        shape.style.width = `${size}px`;
        shape.style.height = `${size}px`;
        shape.style.background = color;
        shape.style.borderRadius = Math.random() > 0.5 ? '50%' : '20%';
        shape.style.position = 'fixed';
        shape.style.left = '0';
        shape.style.top = '0';
        shape.style.transform = `translate(${x}px, ${y}px)`;

        document.body.appendChild(shape);

        shapes.push({
            element: shape,
            x: x,
            y: y,
            vx: (Math.random() - 0.5) * 3, // Faster random velocity
            vy: (Math.random() - 0.5) * 3,
            rotation: 0,
            rSpeed: (Math.random() - 0.5) * 2
        });
    }

    // Animation Loop specifically for background shapes
    function animateShapes() {
        shapes.forEach(shape => {
            shape.x += shape.vx;
            shape.y += shape.vy;
            shape.rotation += shape.rSpeed;

            // Bounce off edges
            if (shape.x < -200 || shape.x > window.innerWidth) shape.vx *= -1;
            if (shape.y < -200 || shape.y > window.innerHeight) shape.vy *= -1;

            shape.element.style.transform = `translate(${shape.x}px, ${shape.y}px) rotate(${shape.rotation}deg)`;
        });
        requestAnimationFrame(animateShapes);
    }
    animateShapes();
}
createBackgroundShapes();
