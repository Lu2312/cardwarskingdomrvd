#!/usr/bin/env python3
"""
Migration script to update Player table columns from String to Text type.
This is needed because SQLite doesn't support ALTER COLUMN directly.
"""

import sqlite3
import shutil
from datetime import datetime

def migrate_player_table():
    db_path = "instance/cardwarskingdom.db"
    backup_path = f"instance/cardwarskingdom_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

    # Create backup
    print(f"Creating backup: {backup_path}")
    shutil.copy2(db_path, backup_path)

    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Start transaction
        cursor.execute("BEGIN TRANSACTION;")

        # Create new table with Text columns
        cursor.execute("""
            CREATE TABLE player_new (
                username VARCHAR(80) NOT NULL,
                game TEXT,
                multiplayer_name VARCHAR(128),
                icon VARCHAR(128),
                deck VARCHAR(1024),
                deck_rank VARCHAR(16),
                landscapes VARCHAR(1024),
                helper_creature VARCHAR(1024),
                leader VARCHAR(128),
                leader_level INTEGER,
                allyboxspace INTEGER,
                level INTEGER,
                friends TEXT,
                friend_requests TEXT,
                last_online INTEGER,
                helpcount INTEGER,
                anonymoushelpcount INTEGER,
                devicename VARCHAR(128),
                PRIMARY KEY (username),
                UNIQUE (username)
            );
        """)

        # Copy data from old table to new table
        cursor.execute("""
            INSERT INTO player_new (
                username, game, multiplayer_name, icon, deck, deck_rank,
                landscapes, helper_creature, leader, leader_level, allyboxspace,
                level, friends, friend_requests, last_online, helpcount,
                anonymoushelpcount, devicename
            )
            SELECT
                username, game, multiplayer_name, icon, deck, deck_rank,
                landscapes, helper_creature, leader, leader_level, allyboxspace,
                level, friends, friend_requests, last_online, helpcount,
                anonymoushelpcount, devicename
            FROM player;
        """)

        # Drop old table
        cursor.execute("DROP TABLE player;")

        # Rename new table
        cursor.execute("ALTER TABLE player_new RENAME TO player;")

        # Create indexes if they existed (check what indexes exist)
        # For now, assuming no specific indexes beyond primary key

        # Commit transaction
        conn.commit()

        print("Migration completed successfully!")
        print(f"Backup created at: {backup_path}")

    except Exception as e:
        # Rollback on error
        conn.rollback()
        print(f"Migration failed: {str(e)}")
        print("Database has been rolled back to original state.")
        raise

    finally:
        conn.close()

if __name__ == "__main__":
    migrate_player_table()