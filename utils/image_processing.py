import cv2
import numpy as np

def convert_to_grayscale(img):
    """Converts the image to grayscale."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

def apply_sepia(img):
    """Applies a sepia tone for a retro look."""
    img_float = img.astype(np.float32) / 255.0
    # Sepia matrix
    kernel = np.array([[0.272, 0.534, 0.131],
                       [0.349, 0.686, 0.168],
                       [0.393, 0.769, 0.189]])
    sepia = cv2.transform(img_float, kernel)
    sepia = np.clip(sepia, 0, 1) * 255.0
    sepia = sepia.astype(np.uint8)
    return add_scratches(sepia)

def add_scratches(img):
    """Adds random vertical scratches to simulate old film."""
    height, width = img.shape[:2]
    # Create a black overlay
    scratch_layer = np.zeros_like(img)
    
    # Number of scratches
    num_scratches = np.random.randint(5, 15)
    
    for _ in range(num_scratches):
        x = np.random.randint(0, width)
        y_start = np.random.randint(0, height // 2)
        y_end = np.random.randint(y_start + 10, height)
        
        # Slight horizontal drift for realism
        x_end = x + np.random.randint(-2, 3)
        
        # Scratches are light/white
        color = (255, 255, 255) 
        cv2.line(scratch_layer, (x, y_start), (x_end, y_end), color, 1)
        
    # Blend scratches: Image + (Scratches * opacity)
    return cv2.addWeighted(img, 1.0, scratch_layer, 0.15, 0)

def apply_vintage(img):
    """Applies a vintage effect with vignetting and grain."""
    sepia = apply_sepia(img)
    rows, cols = sepia.shape[:2]

    # Create vignette mask using Gaussian kernels
    # Ensure kernel sizes are odd for getGaussianKernel
    k_cols = cols | 1
    k_rows = rows | 1
    
    kernel_x = cv2.getGaussianKernel(k_cols, 0) 
    kernel_y = cv2.getGaussianKernel(k_rows, 0)
    kernel = kernel_y * kernel_x.T
    
    # Resize kernel to match image exactly if dimensions changed due to rounding
    if kernel.shape != (rows, cols):
        kernel = cv2.resize(kernel, (cols, rows))
    
    # Normalize kernel to have max value of 1
    mask = kernel / kernel.max()
    
    vintage = sepia.copy()
    
    # Apply mask to each channel
    for i in range(3):
        # We might want to keep the center bright and darken corners aggressively
        vintage[:,:,i] = vintage[:,:,i] * mask

    # Add noise
    noise = np.random.normal(0, 10, vintage.shape).astype(np.float32) # Reduced noise for better quality
    vintage = vintage.astype(np.float32) + noise
    vintage = np.clip(vintage, 0, 255).astype(np.uint8)

    return vintage

def apply_sketch(img):
    """Applies a pencil sketch effect with sharp edges and better contrast."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    inv_gray = cv2.bitwise_not(gray)
    
    # Increase blur radius for better shading isolation
    blur = cv2.GaussianBlur(inv_gray, (25, 25), 0)
    inv_blur = cv2.bitwise_not(blur)
    
    # Dodge
    sketch = cv2.divide(gray, inv_blur, scale=256.0)
    
    # Sharpen to simulate pencil texture
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    sketch = cv2.filter2D(sketch, -1, kernel)
    
    # Darken the lines using Gamma Correction (Gamma > 1 makes shadows darker)
    # This removes the "washed out" look common in simple dodge implementations
    invGamma = 1.8
    table = np.array([((i / 255.0) ** invGamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
    sketch = cv2.LUT(sketch, table)
    
    return cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)

def apply_cartoon(img):
    """Applies a cartoon effect using bilateral filtering and edge detection."""
    # 1. Edges: Using an alternative edge method for cleaner lines
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    
    # Use adaptive thresholding but with block size 9 and C=9
    edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
                                  cv2.THRESH_BINARY, 9, 9)
    
    # 2. Color quantization: Use Pyramid Mean Shift or repetitive Bilateral Filter
    # For performance and style, we use repetitive bilateral filter on downscaled image
    
    # Downsample
    height, width = img.shape[:2]
    small_img = cv2.resize(img, (width // 2, height // 2), interpolation=cv2.INTER_LINEAR)
    
    # Apply bilateral filter multiple times
    for _ in range(5):
        small_img = cv2.bilateralFilter(small_img, 9, 75, 75)
        
    # Upsample
    color = cv2.resize(small_img, (width, height), interpolation=cv2.INTER_LINEAR)
    
    # 3. Combine
    cartoon = cv2.bitwise_and(color, color, mask=edges)
    return cartoon

def apply_cyberpunk(img):
    """Applies a futuristic cyberpunk/neon effect."""
    # Enhance contrast
    img = img.astype(np.float32)
    img = img * 1.2 # Increase contrast
    img = np.clip(img, 0, 255)
    
    # Modify channels: Boost Blue and Red, suppress Green to get purple/neon vibe
    b, g, r = cv2.split(img)
    b = np.clip(b * 1.3, 0, 255) # Boost Blue
    r = np.clip(r * 1.2, 0, 255) # Boost Red (for pink/purple)
    g = np.clip(g * 0.8, 0, 255) # Suppress Green
    
    merged = cv2.merge([b, g, r])
    return merged.astype(np.uint8)

def apply_summer(img):
    """Applies a warm/summer filter using LAB color space adjustments."""
    # Convert to LAB color space
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype("float32")
    l, a, b = cv2.split(lab)
    
    # Shift 'a' channel (Green-Red) towards red
    a = a + 10 
    
    # Shift 'b' channel (Blue-Yellow) towards yellow
    b = b + 10
    
    # Increase saturation (approximate by boosting a and b magnitude)
    l = np.clip(l * 1.05, 0, 255) # Slight brightness boost
    
    # Merge and convert back
    lab = cv2.merge([l, a, b])
    lab = np.clip(lab, 0, 255).astype("uint8")
    return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

def apply_winter(img):
    """Applies a cool/winter filter using LAB color space adjustments."""
    # Convert to LAB color space
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype("float32")
    l, a, b = cv2.split(lab)
    
    # Shift 'b' channel (Blue-Yellow) towards blue (negative values)
    b = b - 15
    
    # Slight reduce 'a' (Green-Red)
    a = a - 3
    
    # Merge and convert back
    lab = cv2.merge([l, a, b])
    lab = np.clip(lab, 0, 255).astype("uint8")
    return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

def apply_watercolor(img):
    """Applies a watercolor effect using stylization."""
    # sigma_s controls the size of the neighborhood. Range 1 - 200
    # sigma_r controls the how dissimilar colors within the neighborhood will be averaged. Range 0 - 1
    dst = cv2.stylization(img, sigma_s=50, sigma_r=0.45)
    return dst

def apply_color_sketch(img):
    """Applies a color pencil sketch effect."""
    # sigma_s and sigma_r are similar to stylization.
    # shade_factor is a simple scaling of the output image intensity. 0 - 1
    dst_gray, dst_color = cv2.pencilSketch(img, sigma_s=60, sigma_r=0.07, shade_factor=0.05)
    return dst_color

def process_image_bytes(image_bytes, style):
    """
    Main entry point. Decodes, processes, and encodes image.
    Returns processed image bytes.
    """
    # Decode
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError("Could not decode image")

    # Process
    if style == 'bw':
        processed = convert_to_grayscale(img)
    elif style == 'retro':
        processed = apply_sepia(img)
    elif style == 'vintage':
        processed = apply_vintage(img)
    elif style == 'sketch':
        processed = apply_sketch(img)
    elif style == 'cartoon':
        processed = apply_cartoon(img)
    elif style == 'cyberpunk':
        processed = apply_cyberpunk(img)
    elif style == 'summer':
        processed = apply_summer(img)
    elif style == 'winter':
        processed = apply_winter(img)
    elif style == 'watercolor':
        processed = apply_watercolor(img)
    elif style == 'color_sketch':
        processed = apply_color_sketch(img)
    else:
        processed = img # original

    # Encode
    _, buffer = cv2.imencode('.jpg', processed)
    return buffer.tobytes()
