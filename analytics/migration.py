"""
Migration script for existing user data
"""

import json
import os
from datetime import datetime
from sqlalchemy.orm import Session as DBSession

from database import SessionLocal, User, CADEvent


def migrate_existing_data(json_file_path: str):
    """Migrate data from collected_user_emails.json to PostgreSQL"""
    if not os.path.exists(json_file_path):
        print(f"Migration file not found: {json_file_path}")
        return

    db = SessionLocal()

    try:
        # Load existing data
        with open(json_file_path, "r") as f:
            data = json.load(f)

        print(f"📦 Migrating {len(data)} users...")

        for user_id, user_data in data.items():
            # Check if user already exists
            existing_user = db.query(User).filter(User.id == user_id).first()
            if existing_user:
                print(f"⏩ User {user_id} already migrated, skipping...")
                continue

            # Create user
            user = User(
                id=user_id,
                email=user_data.get("email", "unknown@example.com"),
                name=user_data.get("name", "Unknown"),
                created_at=datetime.fromisoformat(
                    user_data.get("created_at", datetime.utcnow().isoformat())
                ),
                last_activity=datetime.fromisoformat(
                    user_data.get("last_activity", datetime.utcnow().isoformat())
                ),
                model_count=user_data.get("model_count", 0),
            )
            db.add(user)

            # Migrate prompts as CAD events
            prompts = user_data.get("prompts", [])
            for prompt_data in prompts:
                event = CADEvent(
                    user_id=user_id,
                    session_id=f"migrated_{user_id}",  # Placeholder session
                    event_type=prompt_data.get("type", "generate"),
                    prompt=prompt_data.get("prompt"),
                    success=True,
                    timestamp=datetime.fromisoformat(
                        prompt_data.get("timestamp", datetime.utcnow().isoformat())
                    ),
                    ip_address="migrated",
                )
                db.add(event)

            print(
                f"✅ Migrated user {user_data.get('email')} with {len(prompts)} events"
            )

        db.commit()
        print("🎉 Migration completed successfully!")

        # Rename file to indicate it's been migrated
        os.rename(json_file_path, f"{json_file_path}.migrated")

    except Exception as e:
        print(f"❌ Migration error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # Run migration if executed directly
    migrate_existing_data("/app/collected_user_emails.json")
