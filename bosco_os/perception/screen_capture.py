"""
Bosco Core - Screen Capture Module
Captures screenshots and screen regions for visual AI processing
"""

import os
import base64
import io
from typing import Optional, Tuple, List, Dict, Any
from datetime import datetime
from pathlib import Path

# Try to import screen capture libraries
try:
    import mss
    import mss.tools
    MSS_AVAILABLE = True
except ImportError:
    MSS_AVAILABLE = False
    print("[ScreenCapture] MSS not available")

try:
    from PIL import Image, ImageGrab
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("[ScreenCapture] PIL not available - install with: pip install Pillow")


class ScreenCapture:
    """
    Screen capture functionality for Bosco Core
    Provides screenshots, region capture, and window detection
    """
    
    def __init__(self, save_dir: str = "data/screenshots"):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
        # Check available backends
        self.backend = self._detect_backend()
        
        print(f"[ScreenCapture] Initialized with backend: {self.backend}")
    
    def _detect_backend(self) -> str:
        """Detect available screen capture backend"""
        if PIL_AVAILABLE:
            return "PIL"
        elif MSS_AVAILABLE:
            return "MSS"
        else:
            return "None"
    
    def capture_full_screen(self) -> Optional[Image.Image]:
        """Capture the entire screen"""
        if self.backend == "PIL":
            try:
                return ImageGrab.grab()
            except Exception as e:
                print(f"[ScreenCapture] PIL capture error: {e}")
        
        elif self.backend == "MSS":
            try:
                with mss.mss() as sct:
                    monitor = sct.monitors[1]  # Primary monitor
                    sct_img = sct.grab(monitor)
                    return Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
            except Exception as e:
                print(f"[ScreenCapture] MSS capture error: {e}")
        
        return None
    
    def capture_region(self, bbox: Tuple[int, int, int, int]) -> Optional[Image.Image]:
        """
        Capture a specific screen region
        
        Args:
            bbox: (left, top, right, bottom) coordinates
        """
        if self.backend == "PIL":
            try:
                return ImageGrab.grab(bbox=bbox)
            except Exception as e:
                print(f"[ScreenCapture] Region capture error: {e}")
        
        elif self.backend == "MSS":
            try:
                with mss.mss() as sct:
                    monitor = {
                        "left": bbox[0],
                        "top": bbox[1],
                        "width": bbox[2] - bbox[0],
                        "height": bbox[3] - bbox[1]
                    }
                    sct_img = sct.grab(monitor)
                    return Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
            except Exception as e:
                print(f"[ScreenCapture] MSS region error: {e}")
        
        return None
    
    def capture_window(self, window_title: str) -> Optional[Image.Image]:
        """Capture a specific window by title"""
        # This is a simplified version - full implementation would use platform-specific APIs
        if self.backend == "PIL":
            try:
                # Try using pygetwindow if available
                import pygetwindow as gw
                windows = gw.getWindowsWithTitle(window_title)
                if windows:
                    win = windows[0]
                    bbox = (win.left, win.top, win.right, win.bottom)
                    return ImageGrab.grab(bbox=bbox)
            except ImportError:
                pass
            except Exception as e:
                print(f"[ScreenCapture] Window capture error: {e}")
        
        return None
    
    def get_active_window(self) -> Optional[Dict[str, Any]]:
        """Get information about the currently active window"""
        try:
            import pygetwindow as gw
            win = gw.getActiveWindow()
            if win:
                return {
                    "title": win.title,
                    "left": win.left,
                    "top": win.top,
                    "width": win.width,
                    "height": win.height,
                    "is_minimized": win.isMinimized
                }
        except ImportError:
            pass
        except Exception as e:
            print(f"[ScreenCapture] Active window error: {e}")
        
        return None
    
    def list_windows(self) -> List[Dict[str, Any]]:
        """List all visible windows"""
        windows = []
        
        try:
            import pygetwindow as gw
            for win in gw.getAllWindows():
                if win.title and not win.isMinimized:
                    windows.append({
                        "title": win.title,
                        "left": win.left,
                        "top": win.top,
                        "width": win.width,
                        "height": win.height
                    })
        except ImportError:
            pass
        except Exception as e:
            print(f"[ScreenCapture] List windows error: {e}")
        
        return windows
    
    def save_screenshot(self, filename: Optional[str] = None) -> Optional[str]:
        """
        Capture and save a screenshot
        
        Args:
            filename: Optional custom filename
            
        Returns:
            Path to saved screenshot or None
        """
        img = self.capture_full_screen()
        
        if img is None:
            return None
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
        
        filepath = self.save_dir / filename
        
        try:
            img.save(filepath)
            return str(filepath)
        except Exception as e:
            print(f"[ScreenCapture] Save error: {e}")
            return None
    
    def capture_to_base64(self) -> Optional[str]:
        """Capture screen and return as base64 encoded string"""
        img = self.capture_full_screen()
        
        if img is None:
            return None
        
        try:
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            return base64.b64encode(buffer.getvalue()).decode()
        except Exception as e:
            print(f"[ScreenCapture] Base64 error: {e}")
            return None
    
    def capture_region_to_base64(self, bbox: Tuple[int, int, int, int]) -> Optional[str]:
        """Capture region and return as base64"""
        img = self.capture_region(bbox)
        
        if img is None:
            return None
        
        try:
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            return base64.b64encode(buffer.getvalue()).decode()
        except Exception as e:
            print(f"[ScreenCapture] Base64 error: {e}")
            return None
    
    def get_screen_size(self) -> Optional[Tuple[int, int]]:
        """Get screen dimensions"""
        if self.backend == "PIL":
            try:
                img = self.capture_full_screen()
                if img:
                    return img.size
            except:
                pass
        
        elif self.backend == "MSS":
            try:
                with mss.mss() as sct:
                    monitor = sct.monitors[1]
                    return (monitor["width"], monitor["height"])
            except:
                pass
        
        return None


class VisualElement:
    """Represents a detected visual element on screen"""
    
    def __init__(
        self,
        element_type: str,
        bbox: Tuple[int, int, int, int],
        text: str = "",
        confidence: float = 0.0
    ):
        self.element_type = element_type  # button, text, image, input, etc.
        self.bbox = bbox  # (left, top, right, bottom)
        self.text = text
        self.confidence = confidence
        
        # Calculate center point
        self.center = (
            (bbox[0] + bbox[2]) // 2,
            (bbox[1] + bbox[3]) // 2
        )
    
    def to_dict(self) -> Dict:
        return {
            "type": self.element_type,
            "bbox": self.bbox,
            "center": self.center,
            "text": self.text,
            "confidence": self.confidence
        }


class VisualAnalyzer:
    """
    Analyzes screenshots to detect UI elements
    Uses OCR and computer vision for element detection
    """
    
    def __init__(self):
        self.ocr_available = False
        
        # Try to import OCR
        try:
            import pytesseract
            self.tesseract = pytesseract
            self.ocr_available = True
            print("[VisualAnalyzer] OCR (Tesseract) available")
        except ImportError:
            print("[VisualAnalyzer] OCR not available - install pytesseract")
            self.tesseract = None
        
        # Try to import OpenCV
        try:
            import cv2
            import numpy as np
            self.cv2 = cv2
            self.np = np
            self.cv2_available = True
            print("[VisualAnalyzer] OpenCV available")
        except ImportError:
            self.cv2 = None
            self.np = None
            self.cv2_available = False
    
    def detect_text_elements(self, image) -> List[VisualElement]:
        """Detect text elements in an image using OCR"""
        elements = []
        
        if not self.ocr_available:
            return elements
        
        try:
            # Get verbose data including bounding boxes
            data = self.tesseract.image_to_data(image, output_type=self.tesseract.Output.DICT)
            
            n_boxes = len(data['text'])
            
            for i in range(n_boxes):
                text = data['text'][i].strip()
                
                if text:  # Only include non-empty text
                    (x, y, w, h) = (
                        data['left'][i],
                        data['top'][i],
                        data['width'][i],
                        data['height'][i]
                    )
                    
                    # Calculate confidence
                    conf = float(data['conf'][i]) / 100.0 if data['conf'][i] != -1 else 0.0
                    
                    element = VisualElement(
                        element_type="text",
                        bbox=(x, y, x + w, y + h),
                        text=text,
                        confidence=conf
                    )
                    elements.append(element)
        
        except Exception as e:
            print(f"[VisualAnalyzer] OCR error: {e}")
        
        return elements
    
    def detect_buttons(self, image) -> List[VisualElement]:
        """Detect button-like elements"""
        elements = []
        
        if not self.cv2_available:
            return elements
        
        try:
            # Convert to grayscale
            gray = self.cv2.cvtColor(self.np.array(image), self.cv2.COLOR_RGB2GRAY)
            
            # Detect contours
            _, thresh = self.cv2.threshold(gray, 240, 255, self.cv2.THRESH_BINARY_INV)
            contours, _ = self.cv2.findContours(thresh, self.cv2.RETR_EXTERNAL, self.cv2.CHAIN_APPROX_SIMPLE)
            
            for cnt in contours:
                x, y, w, h = self.cv2.boundingRect(cnt)
                
                # Filter by size (buttons are typically not too small or too large)
                if 30 < w < 500 and 15 < h < 100:
                    element = VisualElement(
                        element_type="button",
                        bbox=(x, y, x + w, y + h),
                        confidence=0.7
                    )
                    elements.append(element)
        
        except Exception as e:
            print(f"[VisualAnalyzer] Button detection error: {e}")
        
        return elements
    
    def get_clickable_points(self, image) -> List[Tuple[int, int]]:
        """Get list of clickable points (center of detected elements)"""
        points = []
        
        # Get text elements
        text_elements = self.detect_text_elements(image)
        for elem in text_elements:
            points.append(elem.center)
        
        # Get button elements
        button_elements = self.detect_buttons(image)
        for elem in button_elements:
            points.append(elem.center)
        
        return points
    
    def draw_element_boxes(self, image, elements: List[VisualElement]):
        """Draw bounding boxes around detected elements"""
        if not self.cv2_available:
            return image
        
        try:
            import numpy as np
            img_array = np.array(image).copy()
            
            color_map = {
                "text": (0, 255, 0),    # Green
                "button": (255, 0, 0),  # Red
                "input": (0, 0, 255),    # Blue
                "image": (255, 255, 0)   # Yellow
            }
            
            for elem in elements:
                color = color_map.get(elem.element_type, (255, 255, 255))
                x1, y1, x2, y2 = elem.bbox
                self.cv2.rectangle(img_array, (x1, y1), (x2, y2), color, 2)
                
                # Draw label
                label = f"{elem.element_type}: {elem.text[:20]}"
                self.cv2.putText(img_array, label, (x1, y1 - 5),
                                self.cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            
            return Image.fromarray(img_array)
        
        except Exception as e:
            print(f"[VisualAnalyzer] Draw error: {e}")
            return image


# Global instances
_screen_capture: Optional[ScreenCapture] = None
_visual_analyzer: Optional[VisualAnalyzer] = None


def get_screen_capture() -> ScreenCapture:
    """Get the screen capture instance"""
    global _screen_capture
    if _screen_capture is None:
        _screen_capture = ScreenCapture()
    return _screen_capture


def get_visual_analyzer() -> VisualAnalyzer:
    """Get the visual analyzer instance"""
    global _visual_analyzer
    if _visual_analyzer is None:
        _visual_analyzer = VisualAnalyzer()
    return _visual_analyzer


if __name__ == "__main__":
    print("=== Testing Screen Capture ===\n")
    
    capture = ScreenCapture()
    
    print(f"Backend: {capture.backend}")
    print(f"Screen size: {capture.get_screen_size()}")
    
    # List windows
    print("\nOpen windows:")
    windows = capture.list_windows()
    for win in windows[:5]:
        print(f"  - {win['title'][:50]}")
    
    # Test capture
    print("\nCapturing screenshot...")
    filepath = capture.save_screenshot()
    print(f"Saved to: {filepath}")

