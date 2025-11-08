'''
Business: Analyzes Telegram game bot messages and returns winning positions
Args: event - dict with httpMethod, body (telegram_url)
      context - object with request_id, function_name attributes
Returns: HTTP response with positions array and formatted text
'''

import json
import re
from typing import Dict, Any, List
from pydantic import BaseModel, Field
import urllib.request
from urllib.parse import urlparse
import cv2
import numpy as np

class AnalyzeRequest(BaseModel):
    telegram_url: str = Field(..., description="Telegram message URL or image URL")

def extract_image_url(telegram_url: str) -> str:
    parsed = urlparse(telegram_url)
    if 'cdn' in parsed.netloc or parsed.path.endswith(('.jpg', '.jpeg', '.png')):
        return telegram_url
    return telegram_url

def fetch_image_from_url(url: str) -> np.ndarray:
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    )
    with urllib.request.urlopen(req, timeout=15) as response:
        image_data = response.read()
    nparr = np.frombuffer(image_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img

def analyze_game_grid(img: np.ndarray) -> List[Dict[str, int]]:
    if img is None or img.size == 0:
        return []
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    height, width = gray.shape
    
    cell_height = height // 5
    cell_width = width // 3
    
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    winning_positions = []
    
    for row in range(5):
        for col in range(3):
            y_start = row * cell_height
            y_end = (row + 1) * cell_height
            x_start = col * cell_width
            x_end = (col + 1) * cell_width
            
            roi = hsv[y_start:y_end, x_start:x_end]
            
            if roi.size == 0:
                continue
            
            lower_red1 = np.array([0, 50, 50])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([170, 50, 50])
            upper_red2 = np.array([180, 255, 255])
            
            mask1 = cv2.inRange(roi, lower_red1, upper_red1)
            mask2 = cv2.inRange(roi, lower_red2, upper_red2)
            red_mask = mask1 + mask2
            
            red_pixels = cv2.countNonZero(red_mask)
            total_pixels = roi.shape[0] * roi.shape[1]
            
            if red_pixels > total_pixels * 0.05:
                winning_positions.append({'row': row, 'col': col})
    
    return winning_positions

def format_result_text(positions: List[Dict[str, int]]) -> str:
    if not positions:
        return "Выигрышные позиции не найдены"
    
    result_lines = []
    for pos in positions:
        col_num = pos['col'] + 1
        row_num = pos['row'] + 1
        result_lines.append(f"{col_num} столбик {row_num} квадрат")
    
    return ", ".join(result_lines)

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
    
    image_url = extract_image_url(request.telegram_url)
    img = fetch_image_from_url(image_url)
    
    if img is None:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Failed to load image'}),
            'isBase64Encoded': False
        }
    
    positions = analyze_game_grid(img)
    result_text = format_result_text(positions)
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'positions': positions,
            'result_text': result_text,
            'request_id': context.request_id
        }),
        'isBase64Encoded': False
    }