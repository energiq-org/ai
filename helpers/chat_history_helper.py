from sqlalchemy import create_engine, text
import json

database_file_path = 'ev_charging.db'
engine = create_engine(f'sqlite:///{database_file_path}')

def append_message(user_id, role, content):
    with engine.begin() as conn:
        result = conn.execute(
            text("SELECT history_json FROM chat_history WHERE user_id = :uid"),
            {"uid": user_id}
        ).first()

        messages = json.loads(result.history_json) if result and result.history_json else []

        # 🔍 Determine correct message format
        if isinstance(content, dict):
            message = content.copy()
            if "role" not in message:
                message["role"] = role
            # ⚠ Ensure `content=None` if it's a tool_call assistant message
            if "tool_calls" in message:
                message["content"] = None
        else:
            message = {"role": role, "content": content}

        messages.append(message)

        conn.execute(text("""
            INSERT INTO chat_history (user_id, history_json)
            VALUES (:uid, :hist)
            ON CONFLICT (user_id) DO UPDATE
              SET history_json = EXCLUDED.history_json
        """), {"uid": user_id, "hist": json.dumps(messages)})


def get_history(user_id: str):
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT history_json FROM chat_history WHERE user_id = :uid"),
            {"uid": user_id}
        ).first()

        if result and result.history_json:
            return json.loads(result.history_json)  # ✅ Parse string to list[dict]
        return []


if __name__ == "__main__":
    history = get_history("1")
    history.append({"role": "user", "content": "hi"})
    assistant_msg = "hello"
    append_message("1", "assistant", assistant_msg)