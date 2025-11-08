'''
Business: Analyzes Telegram game bot messages and returns winning positions
Args: event - dict with httpMethod, body (telegramUrl or imageUrl)
      context - object with request_id, function_name attributes
Returns: HTTP response with positions array
'''

import json
import re
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import urllib.request
import cv2
import numpy as np

class AnalyzeRequest(BaseModel):
    telegram_url: Optional[str] = Field(None, description="Telegram message URL")
    image_url: Optional[str] = Field(None, description="Direct image URL")

def fetch_image_from_url(url: str) -> np.ndarray:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        image_data = response.read()
    nparr = np.frombuffer(image_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img

def analyze_game_grid(img: np.ndarray) -> List[Dict[str, int]]:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    edges = cv2.Canny(blurred, 50, 150)
    
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    cells = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = w / float(h) if h > 0 else 0
        area = cv2.contourArea(contour)
        
        if 0.7 < aspect_ratio < 1.3 and area > 1000:
            cells.append({'x': x, 'y': y, 'w': w, 'h': h, 'area': area})
    
    cells = sorted(cells, key=lambda c: (c['y'], c['x']))
    
    if len(cells) < 15:
        cells = []
        height, width = gray.shape
        cell_height = height // 5
        cell_width = width // 3
        
        for row in range(5):
            for col in range(3):
                x = col * cell_width
                y = row * cell_height
                cells.append({'x': x, 'y': y, 'w': cell_width, 'h': cell_height})
    
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    winning_positions = []
    
    for idx, cell in enumerate(cells[:15]):
        row = idx // 3
        col = idx % 3
        
        x, y, w, h = cell['x'], cell['y'], cell['w'], cell['h']
        
        center_x = x + w // 2
        center_y = y + h // 2
        roi_size = min(w, h) // 3
        
        roi = hsv[
            max(0, center_y - roi_size):min(hsv.shape[0], center_y + roi_size),
            max(0, center_x - roi_size):min(hsv.shape[1], center_x + roi_size)
        ]
        
        if roi.size == 0:
            continue
        
        lower_red1 = np.array([0, 100, 100])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([160, 100, 100])
        upper_red2 = np.array([180, 255, 255])
        
        mask1 = cv2.inRange(roi, lower_red1, upper_red1)
        mask2 = cv2.inRange(roi, lower_red2, upper_red2)
        red_mask = mask1 + mask2
        
        red_pixels = cv2.countNonZero(red_mask)
        total_pixels = roi.shape[0] * roi.shape[1]
        
        if red_pixels > total_pixels * 0.1:
            winning_positions.append({'row': row, 'col': col})
    
    return winning_positions

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    method: str = event.get('httpMethod', 'GET')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Max-Age': '86400'
            },
            'body': '',
            'isBase64Encoded': False
        }
    
    if method != 'POST':
        return {
            'statusCode': 405,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Method not allowed'}),
            'isBase64Encoded': False
        }
    
    body_data = json.loads(event.get('body', '{}'))
    request = AnalyzeRequest(**body_data)
    
    image_url = request.image_url
    
    if request.telegram_url and not image_url:
        match = re.search(r't\.me/\w+/(\d+)', str(request.telegram_url))
        if match:
            image_url = f"https://t.me/{match.group(0)}"
    
    if not image_url:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'No image URL provided'}),
            'isBase64Encoded': False
        }
    
    img = fetch_image_from_url(image_url)
    positions = analyze_game_grid(img)
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'positions': positions,
            'request_id': context.request_id
        }),
        'isBase64Encoded': False
    }
