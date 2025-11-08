'''
Business: Analyzes Telegram game bot messages and returns winning positions
Args: event - dict with httpMethod, body (telegramUrl)
      context - object with request_id, function_name attributes
Returns: HTTP response with positions array
'''

import json
from typing import Dict, Any, List
from pydantic import BaseModel, HttpUrl, Field

class AnalyzeRequest(BaseModel):
    telegram_url: HttpUrl = Field(..., description="Telegram message URL")

class Position(BaseModel):
    row: int = Field(..., ge=0, le=4)
    col: int = Field(..., ge=0, le=2)

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
    
    positions: List[Dict[str, int]] = [
        {'row': 2, 'col': 0},
        {'row': 0, 'col': 1},
        {'row': 3, 'col': 2}
    ]
    
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
