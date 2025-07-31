import cv2
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
import logging

logger = logging.getLogger(__name__)

class StyleTransfer:
    """Handles various artistic style transfers using open-source methods"""
    
    def __init__(self):
        """Initialize style transfer models"""
        self.models_loaded = False
        self._load_models()
    
    def _load_models(self):
        """Load any pre-trained models if available"""
        try:
            # For now, we'll use filter-based approaches
            # In production, you can add AnimeGANv2 or other models here
            self.models_loaded = True
            logger.info("Style transfer models initialized")
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            self.models_loaded = False
    
    def apply_style(self, input_path, output_path, style):
        """Apply the specified style to an image"""
        try:
            if style == 'ghibli':
                self._apply_ghibli_style(input_path, output_path)
            elif style == 'cartoon':
                self._apply_cartoon_style(input_path, output_path)
            elif style == 'sketch':
                self._apply_sketch_style(input_path, output_path)
            elif style == 'oil_painting':
                self._apply_oil_painting_style(input_path, output_path)
            elif style == 'watercolor':
                self._apply_watercolor_style(input_path, output_path)
            elif style == 'anime':
                self._apply_anime_style(input_path, output_path)
            else:
                # Default to cartoon style
                self._apply_cartoon_style(input_path, output_path)
            
            logger.info(f"Applied {style} style to {input_path}")
        except Exception as e:
            logger.error(f"Error applying style {style}: {e}")
            # Fallback: just copy the original
            import shutil
            shutil.copy2(input_path, output_path)
    
    def _apply_ghibli_style(self, input_path, output_path):
        """Apply Studio Ghibli-like style using OpenCV and PIL"""
        # Read image
        img = cv2.imread(input_path)
        
        # Apply bilateral filter for smooth, painted look
        smooth = cv2.bilateralFilter(img, 15, 50, 50)
        
        # Enhance colors
        smooth = cv2.convertScaleAbs(smooth, alpha=1.2, beta=10)
        
        # Convert to PIL for further processing
        pil_img = Image.fromarray(cv2.cvtColor(smooth, cv2.COLOR_BGR2RGB))
        
        # Enhance saturation
        enhancer = ImageEnhance.Color(pil_img)
        pil_img = enhancer.enhance(1.3)
        
        # Slight blur for dreamy effect
        pil_img = pil_img.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        pil_img.save(output_path, quality=95)
    
    def _apply_cartoon_style(self, input_path, output_path):
        """Apply cartoon style using edge detection and color quantization"""
        img = cv2.imread(input_path)
        
        # Edge detection
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
                                    cv2.THRESH_BINARY, 7, 7)
        edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        
        # Color quantization
        data = np.float32(img).reshape((-1, 3))
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
        _, labels, centers = cv2.kmeans(data, 8, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        centers = np.uint8(centers)
        quantized = centers[labels.flatten()].reshape(img.shape)
        
        # Bilateral filter for smoothing
        smooth = cv2.bilateralFilter(quantized, 15, 40, 40)
        
        # Combine with edges
        cartoon = cv2.bitwise_and(smooth, edges)
        
        cv2.imwrite(output_path, cartoon)
    
    def _apply_sketch_style(self, input_path, output_path):
        """Apply pencil sketch style"""
        img = cv2.imread(input_path)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Invert the image
        inverted = cv2.bitwise_not(gray)
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(inverted, (111, 111), 0)
        
        # Invert the blurred image
        inverted_blur = cv2.bitwise_not(blurred)
        
        # Create the sketch
        sketch = cv2.divide(gray, inverted_blur, scale=256.0)
        
        # Convert back to BGR for saving
        sketch_bgr = cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)
        
        cv2.imwrite(output_path, sketch_bgr)
    
    def _apply_oil_painting_style(self, input_path, output_path):
        """Apply oil painting effect"""
        img = cv2.imread(input_path)
        
        # Apply oil painting effect using OpenCV
        try:
            oil_painting = cv2.xphoto.oilPainting(img, 7, 1)
            cv2.imwrite(output_path, oil_painting)
        except:
            # Fallback if xphoto is not available
            self._apply_ghibli_style(input_path, output_path)
    
    def _apply_watercolor_style(self, input_path, output_path):
        """Apply watercolor painting effect"""
        img = cv2.imread(input_path)
        
        # Apply bilateral filter multiple times
        for _ in range(3):
            img = cv2.bilateralFilter(img, 9, 200, 200)
        
        # Convert to PIL for additional effects
        pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        
        # Reduce color palette
        pil_img = pil_img.quantize(colors=16).convert('RGB')
        
        # Apply slight blur
        pil_img = pil_img.filter(ImageFilter.GaussianBlur(radius=1))
        
        pil_img.save(output_path, quality=90)
    
    def _apply_anime_style(self, input_path, output_path):
        """Apply anime-like style (simplified version)"""
        img = cv2.imread(input_path)
        
        # Smooth the image
        smooth = cv2.bilateralFilter(img, 15, 80, 80)
        
        # Create edge mask
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
                                    cv2.THRESH_BINARY, 7, 7)
        edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        
        # Color quantization with fewer colors
        data = np.float32(smooth).reshape((-1, 3))
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
        _, labels, centers = cv2.kmeans(data, 6, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        centers = np.uint8(centers)
        quantized = centers[labels.flatten()].reshape(smooth.shape)
        
        # Combine smooth areas with sharp edges
        anime = cv2.bitwise_and(quantized, edges)
        
        cv2.imwrite(output_path, anime)