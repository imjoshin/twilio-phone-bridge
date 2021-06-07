from asyncpg import Connection

from . import upgrade_table


@upgrade_table.register(description="Initial asyncpg revision", transaction=False)
async def upgrade_v1(conn: Connection):
    create_table_queries = [
        """
        CREATE TABLE "user" (
            mxid            TEXT PRIMARY KEY,
            li_member_urn   TEXT UNIQUE,
            cookies         jsonb,
            notice_room     TEXT
        )
        """,
        """
        CREATE TABLE portal (
            li_thread_urn   TEXT,
            li_receiver_urn TEXT,
            mxid            TEXT UNIQUE,
            name            TEXT,
            photo_id        TEXT,
            avatar_url      TEXT,
            encrypted       BOOLEAN NOT NULL DEFAULT false,

            PRIMARY KEY (li_thread_urn, li_receiver_urn)
        )
        """,
        """
        CREATE TABLE puppet (
            li_member_urn   TEXT PRIMARY KEY,
            name            TEXT,
            photo_id        TEXT,
            photo_mxc       TEXT,

            name_set        BOOLEAN NOT NULL DEFAULT false,
            avatar_set      BOOLEAN NOT NULL DEFAULT false,
            is_registered   BOOLEAN NOT NULL DEFAULT false,

            custom_mxid     TEXT,
            next_batch      TEXT
        )
        """,
        """
        CREATE TABLE message (
            mxid                TEXT,
            mx_room             TEXT,
            li_message_urn      TEXT,
            li_thread_urn       TEXT,
            li_sender_urn       TEXT,
            li_receiver_urn     TEXT,
            index               SMALLINT,
            timestamp           BIGINT,

            PRIMARY KEY (li_thread_urn, li_receiver_urn, index),

            FOREIGN KEY (li_thread_urn, li_receiver_urn)
             REFERENCES portal (li_thread_urn, li_receiver_urn)
                     ON UPDATE CASCADE
                     ON DELETE CASCADE,

            UNIQUE (mxid, mx_room),
            UNIQUE (li_thread_urn, li_receiver_urn, index),
            UNIQUE (li_message_urn, li_sender_urn, li_receiver_urn, index)
        )
        """,
        """
        CREATE TABLE reaction (
            mxid            TEXT,
            mx_room         TEXT,
            li_message_urn  TEXT,
            li_receiver_urn TEXT,
            li_sender_urn   TEXT,
            reaction        TEXT,

            PRIMARY KEY (li_message_urn, li_receiver_urn, li_sender_urn),

            UNIQUE (mxid, mx_room)
        )
        """,
        """
        CREATE TABLE user_portal (
            "user"          TEXT,
            portal          TEXT,
            portal_receiver TEXT,

            PRIMARY KEY ("user", portal, portal_receiver),

            FOREIGN KEY (portal, portal_receiver)
             REFERENCES portal (li_thread_urn, li_receiver_urn)
                     ON UPDATE CASCADE
                     ON DELETE CASCADE,

            FOREIGN KEY ("user")
             REFERENCES "user"(li_member_urn)
                     ON UPDATE CASCADE
                     ON DELETE CASCADE
        )
        """,
    ]

    for query in create_table_queries:
        await conn.execute(query)
