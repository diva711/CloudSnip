from flask import Blueprint, request, jsonify, redirect
from db import get_connection
import jwt
import os
import string
import random
import boto3

links_bp = Blueprint('links', __name__)

def verify_token(request):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return None
    try:
        payload = jwt.decode(token, os.environ.get('JWT_SECRET'), algorithms=['HS256'])
        return payload['user_id']
    except:
        return None

def generate_short_code():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=6))

@links_bp.route('/shorten', methods=['POST'])
def shorten():
    user_id = verify_token(request)
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    long_url = data.get('long_url')

    if not long_url:
        return jsonify({'error': 'long_url is required'}), 400

    short_code = generate_short_code()

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO links (user_id, long_url, short_code) VALUES (%s, %s, %s)",
            (user_id, long_url, short_code)
        )
        conn.commit()
        cur.close()
        conn.close()

        short_url = f"http://{os.environ.get('EC2_HOST')}:5000/{short_code}"
        return jsonify({
            'short_url': short_url,
            'short_code': short_code,
            'long_url': long_url
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@links_bp.route('/<short_code>', methods=['GET'])
def redirect_to_url(short_code):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, long_url FROM links WHERE short_code = %s",
            (short_code,)
        )
        link = cur.fetchone()

        if not link:
            return jsonify({'error': 'Link not found'}), 404

        cur.execute(
            "UPDATE links SET click_count = click_count + 1 WHERE id = %s",
            (link[0],)
        )

        cur.execute(
            "INSERT INTO clicks (link_id, ip_address, user_agent) VALUES (%s, %s, %s)",
            (link[0], request.remote_addr, request.headers.get('User-Agent'))
        )

        conn.commit()
        cur.close()
        conn.close()

        # Trigger Lambda asynchronously
        try:
            lambda_client = boto3.client('lambda', region_name='ap-south-1')
            lambda_client.invoke(
                FunctionName='cloudsnip-click-logger',
                InvocationType='Event',
                Payload=str({
                    'link_id': link[0],
                    'ip_address': request.remote_addr,
                    'user_agent': request.headers.get('User-Agent')
                }).encode()
            )
        except:
            pass

        return redirect(link[1], code=302)

    except Exception as e:
        return jsonify({'error': str(e)}), 500