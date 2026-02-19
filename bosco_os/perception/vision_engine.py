"""
Bosco Core - Vision Engine
Multimodal visual reasoning and state verification
"""

import base64
import io
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False


class VisualElement:
    """Represents a detected UI element"""
    
    def __init__(
        self,
        element_type: str,
        bbox: Tuple[int, int, int, int],
        text: str = "",
        confidence: float = 0.0,
        clickable: bool = False
    ):
        self.element_type = element_type
        self.bbox = bbox  # (left, top, right, bottom)
        self.text = text
        self.confidence = confidence
        self.clickable = clickable
        
        # Calculate center
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
            "confidence": self.confidence,
            "clickable": self.clickable
        }


class VisionEngine:
    """
    Visual Reasoning Engine
    Provides multimodal perception and visual state verification
    """
    
    def __init__(self, multimodal_api_key: str = None):
        self.api_key = multimodal_api_key
        self.vision_provider = self._detect_vision_provider()
        
        # Screen capture
        self.screen_capture = None
        
        # PIL not available
        self._pil_available = False
        try:
            from PIL import Image
            self._pil_available = True
        except ImportError:
            pass
        
        print(f"[VisionEngine] Initialized with provider: {self.vision_provider}")
    
    def _detect_vision_provider(self) -> str:
        """Detect available vision API"""
        # Check for OpenAI
        try:
            import openai
            if hasattr(openai, 'api_key') or self.api_key:
                return "openai"
        except ImportError:
            pass
        
        # Check for Anthropic
        try:
            import anthropic
            return "anthropic"
        except ImportError:
            pass
        
        # Fallback to local processing
        return "local"
    
    async def analyze_screen(
        self,
        image: Any = None,
        question: str = "Describe what's on this screen"
    ) -> Dict[str, Any]:
        """
        Analyze screen content using multimodal AI
        
        Args:
            image: PIL Image or image path
            question: Question about the screen
            
        Returns:
            Analysis result
        """
        
        # Capture screen if no image provided
        if image is None:
            image = await self._capture_screen()
        
        if image is None:
            return {
                "success": False,
                "error": "No image available and screen capture failed"
            }
        
        # Use vision provider
        if self.vision_provider == "openai":
            return await self._analyze_with_openai(image, question)
        elif self.vision_provider == "anthropic":
            return await self._analyze_with_anthropic(image, question)
        else:
            return await self._analyze_locally(image, question)
    
    async def find_element(
        self,
        element_name: str,
        image: Any = None
    ) -> Optional[VisualElement]:
        """
        Find a specific UI element by name
        
        Args:
            element_name: Name/label of element to find
            image: Optional image to search in
            
        Returns:
            VisualElement if found, None otherwise
        """
        
        # Capture screen
        if image is None:
            image = await self._capture_screen()
        
        if image is None:
            return None
        
        # Use OCR to find text elements
        elements = await self.detect_elements(image)
        
        # Search for matching element
        element_name_lower = element_name.lower()
        
        for elem in elements:
            if element_name_lower in elem.text.lower():
                return elem
        
        return None
    
    async def detect_elements(
        self,
        image: Any = None
    ) -> List[VisualElement]:
        """
        Detect all UI elements on screen
        
        Returns:
            List of VisualElement objects
        """
        
        if image is None:
            image = await self._capture_screen()
        
        if image is None:
            return []
        
        elements = []
        
        # Use OCR for text detection
        if PIL_AVAILABLE:
            try:
                import pytesseract
                
                # Get verbose OCR data
                data = pytesseract.image_to_data(
                    image,
                    output_type=pytesseract.Output.DICT
                )
                
                n_boxes = len(data['text'])
                
                for i in range(n_boxes):
                    text = data['text'][i].strip()
                    
                    if text:
                        x = data['left'][i]
                        y = data['top'][i]
                        w = data['width'][i]
                        h = data['height'][i]
                        
                        conf = float(data['conf'][i]) / 100.0 if data['conf'][i] != -1 else 0.0
                        
                        # Determine if clickable (heuristic: buttons are typically smaller)
                        is_button = w < 300 and h < 60 and h > 15
                        
                        elements.append(VisualElement(
                            element_type="text" if not is_button else "button",
                            bbox=(x, y, x + w, y + h),
                            text=text,
                            confidence=conf,
                            clickable=is_button
                        ))
                
            except ImportError:
                print("[VisionEngine] Tesseract not available")
            except Exception as e:
                print(f"[VisionEngine] OCR error: {e}")
        
        return elements
    
    async def click_element(
        self,
        element_name: str,
        image: Any = None
    ) -> Dict[str, Any]:
        """
        Find and click an element by name
        
        Returns:
            Click result
        """
        
        element = await self.find_element(element_name, image)
        
        if element is None:
            return {
                "success": False,
                "error": f"Element '{element_name}' not found"
            }
        
        # Use pyautogui to click
        try:
            import pyautogui
            
            x, y = element.center
            pyautogui.click(x, y)
            
            return {
                "success": True,
                "clicked_at": element.center,
                "element": element.to_dict()
            }
        
        except ImportError:
            return {
                "success": False,
                "error": "pyautogui not available"
            }
    
    async def _capture_screen(self) -> Optional[Any]:
        """Capture current screen"""
        if not self._pil_available:
            print("[VisionEngine] PIL not available for screen capture")
            return None
        
        try:
            from PIL import ImageGrab
            return ImageGrab.grab()
        except Exception as e:
            print(f"[VisionEngine] Screen capture error: {e}")
            return None
    
    async def _analyze_with_openai(
        self,
        image: Any,
        question: str
    ) -> Dict[str, Any]:
        """Analyze with OpenAI GPT-4 Vision"""
        
        try:
            import openai
            
            # Convert image to base64
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": question},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{img_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )
            
            return {
                "success": True,
                "analysis": response.choices[0].message.content,
                "provider": "openai"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "provider": "openai"
            }
    
    async def _analyze_with_anthropic(
        self,
        image: Any,
        question: str
    ) -> Dict[str, Any]:
        """Analyze with Anthropic Claude Vision"""
        
        try:
            import anthropic
            
            # Convert image to base64
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            client = anthropic.Anthropic(api_key=self.api_key)
            
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": img_base64
                                }
                            },
                            {
                                "type": "text",
                                "text": question
                            }
                        ]
                    }
                ]
            )
            
            return {
                "success": True,
                "analysis": response.content[0].text,
                "provider": "anthropic"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "provider": "anthropic"
            }
    
    async def _analyze_locally(
        self,
        image: Any,
        question: str
    ) -> Dict[str, Any]:
        """Local analysis using OCR only"""
        
        elements = await self.detect_elements(image)
        
        # Return detected elements as "analysis"
        element_summary = "\n".join([
            f"- {e.text} at {e.center} ({e.element_type})"
            for e in elements[:20]
        ])
        
        return {
            "success": True,
            "analysis": f"Detected {len(elements)} elements:\n{element_summary}",
            "provider": "local",
            "elements": [e.to_dict() for e in elements]
        }
    
    def get_element_at_position(
        self,
        x: int,
        y: int,
        elements: List[VisualElement]
    ) -> Optional[VisualElement]:
        """Find element at a specific screen position"""
        
        for elem in elements:
            x1, y1, x2, y2 = elem.bbox
            
            if x1 <= x <= x2 and y1 <= y <= y2:
                return elem
        
        return None


class ScreenState:
    """Represents a screen state for comparison"""
    
    def __init__(self, elements: List[VisualElement], timestamp: datetime = None):
        self.elements = elements
        self.timestamp = timestamp or datetime.now()
        self.element_signatures = self._generate_signatures()
    
    def _generate_signatures(self) -> set:
        """Generate unique signatures for elements"""
        return set(e.text for e in self.elements if e.text)
    
    def has_changed(self, other: 'ScreenState') -> bool:
        """Check if screen state has changed"""
        return self.element_signatures != other.element_signatures


# Global instance
_vision_engine: Optional[VisionEngine] = None


def get_vision_engine(api_key: str = None) -> VisionEngine:
    """Get the vision engine instance"""
    global _vision_engine
    if _vision_engine is None:
        _vision_engine = VisionEngine(api_key)
    return _vision_engine


if __name__ == "__main__":
    import asyncio
    
    print("=== Testing Vision Engine ===\n")
    
    async def test():
        engine = get_vision_engine()
        
        # Detect elements
        print("Detecting elements...")
        elements = await engine.detect_elements()
        print(f"Found {len(elements)} elements")
        
        # Analyze screen
        print("\nAnalyzing screen...")
        result = await engine.analyze_screen(
            question="What buttons and interactive elements are visible?"
        )
        print(f"Success: {result['success']}")
        if result.get('analysis'):
            print(f"Analysis: {result['analysis'][:200]}...")
    
    asyncio.run(test())

