#!/usr/bin/env python3
"""Import incidents from a JSON file into the app.

Usage:
  //python scripts/import_incidents.py --json incidents.json --mode api --url http://10.0.2.2:8000/api
  python scripts/import_incidents.py --json incidents.json --mode db

Modes:
  api - POST to the running API's /incidents endpoint (requires server running). You can pass --token for Bearer auth.
  db  - Insert directly into the database using the repository and SQLAlchemy session.

The JSON file may be either a single object or a list of objects. Each object should match IncidentCreateDTO shape:
  title, latitude, longitude are required; description, category, severity optional.
"""

import argparse
import json
import os
import sys
from datetime import datetime

def ensure_repo_importable():
    # Add project root to sys.path so we can import src.* modules
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if isinstance(data, dict):
        return [data]
    return data


def post_to_api(items, base_url, token=None):
    import requests

    url = base_url.rstrip('/') + '/incidents'
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'

    for i, item in enumerate(items, 1):
        resp = requests.post(url, json=item, headers=headers)
        if resp.status_code in (200, 201):
            print(f"[{i}] Posted successfully: {resp.status_code}")
        else:
            print(f"[{i}] Failed: {resp.status_code} - {resp.text}")


def insert_via_db(items):
    ensure_repo_importable()
    from src.infrastructure.database.sql.database import create_db_and_tables, SessionLocal
    from src.infrastructure.incident.repository_impl import IncidentRepository
    from src.domain.incident.entities import Incident as IncidentEntity

    # ensure DB and tables exist
    try:
        create_db_and_tables()
    except Exception as e:
        print(f"Warning: could not auto-create DB/tables: {e}")

    repo = IncidentRepository()
    session = SessionLocal()
    created = 0
    try:
        for i, item in enumerate(items, 1):
            entity = IncidentEntity(
                title=item.get('title'),
                description=item.get('description'),
                category=item.get('category'),
                latitude=float(item.get('latitude')),
                longitude=float(item.get('longitude')),
                severity=item.get('severity'),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            repo.create(session, entity)
            created += 1
            print(f"[{i}] Inserted into DB")
    except Exception as e:
        print(f"Error inserting: {e}")
    finally:
        session.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--json', required=True, help='Path to incidents.json')
    parser.add_argument('--mode', choices=['api', 'db'], default='api', help='Insert mode')
    parser.add_argument('--url', default='http://127.0.0.1:8000/api', help='Base API URL for api mode')
    parser.add_argument('--token', help='Bearer token for API authentication')
    parser.add_argument('--create-user', action='store_true', help='Create a user account before posting')
    parser.add_argument('--username', help='Username to create/use for posting')
    parser.add_argument('--password', help='Password for the user (min 8 chars)')
    parser.add_argument('--email', help='Email for the created user')
    parser.add_argument('--full-name', dest='full_name', help='Full name for the created user')

    args = parser.parse_args()

    items = load_json(args.json)
    if not items:
        print('No incidents found in JSON.')
        return

    if args.mode == 'api':
        print(f"Posting {len(items)} incident(s) to {args.url}")
        token = args.token
        if args.create_user:
            # require username and password and full_name
            if not args.username or not args.password or not args.full_name:
                print('When using --create-user you must provide --username, --password and --full-name')
                return
            # create user via API
            import requests
            reg_url = args.url.rstrip('/') + '/register'
            reg_body = {
                'username': args.username,
                'password': args.password,
                'full_name': args.full_name,
            }
            if args.email:
                reg_body['email'] = args.email
            print(f"Creating user {args.username} via {reg_url}")
            r = requests.post(reg_url, json=reg_body)
            if r.status_code not in (200, 201):
                print(f"Failed to create user: {r.status_code} - {r.text}")
                return
            print('User created successfully')
            # login to get token
            login_url = args.url.rstrip('/') + '/login'
            login_data = {'username': args.username, 'password': args.password}
            lr = requests.post(login_url, data=login_data)
            if lr.status_code != 200:
                print(f"Login failed: {lr.status_code} - {lr.text}")
                return
            td = lr.json()
            token = td.get('access_token')
            if not token:
                print('Login response did not contain access_token')
                return
            print('Obtained access token')

        post_to_api(items, args.url, token=token)
    else:
        print(f"Inserting {len(items)} incident(s) directly into DB")
        insert_via_db(items)


if __name__ == '__main__':
    main()
