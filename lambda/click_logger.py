import json
import pg8000
import os
import datetime

def lambda_handler(event, context):
    link_id = event.get('link_id')
    ip_address = event.get('ip_address')
    user_agent = event.get('user_agent')

    if not link_id:
        return {
            'statusCode': 400,
            'body': json.dumps('link_id is required')
        }

    try:
        conn = pg8000.connect(
            host=os.environ.get('DB_HOST'),
            database=os.environ.get('DB_NAME'),
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASSWORD'),
            port=5432
        )

        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO clicks (link_id, ip_address, user_agent, clicked_at) VALUES (%s, %s, %s, %s)",
            (link_id, ip_address, user_agent, datetime.datetime.utcnow())
        )

        conn.commit()
        cursor.close()
        conn.close()

        return {
            'statusCode': 200,
            'body': json.dumps('Click logged successfully')
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(str(e))
        }