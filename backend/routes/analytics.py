from flask import Blueprint, jsonify, request
from db import get_connection
import jwt
import os

analytics_bp = Blueprint('analytics', __name__)

def verify_token(request):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return None
    try:
        payload = jwt.decode(token, os.environ.get('JWT_SECRET'), algorithms=['HS256'])
        return payload['user_id']
    except:
        return None

@analytics_bp.route('/analytics', methods=['GET'])
def get_analytics():
    user_id = verify_token(request)
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                l.short_code,
                l.long_url,
                l.click_count,
                l.created_at,
                COUNT(c.id) as total_clicks
            FROM links l
            LEFT JOIN clicks c ON c.link_id = l.id
            WHERE l.user_id = %s
            GROUP BY l.id
            ORDER BY l.created_at DESC
        """, (user_id,))

        rows = cur.fetchall()

        cur.execute("""
            SELECT
                c.clicked_at,
                c.ip_address,
                c.user_agent,
                l.short_code
            FROM clicks c
            JOIN links l ON l.id = c.link_id
            WHERE l.user_id = %s
            ORDER BY c.clicked_at DESC
            LIMIT 50
        """, (user_id,))

        recent_clicks = cur.fetchall()

        cur.close()
        conn.close()

        links_data = []
        for row in rows:
            links_data.append({
                'short_code': row[0],
                'long_url': row[1],
                'click_count': row[2],
                'created_at': str(row[3]),
                'total_clicks': row[4]
            })

        clicks_data = []
        for click in recent_clicks:
            clicks_data.append({
                'clicked_at': str(click[0]),
                'ip_address': click[1],
                'user_agent': click[2],
                'short_code': click[3]
            })

        return jsonify({
            'links': links_data,
            'recent_clicks': clicks_data
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500