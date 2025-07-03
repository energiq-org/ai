import numpy as np
import pandas as pd
from sqlalchemy import create_engine, inspect, text

database_file_path = "db/ev_charging.db"
engine = create_engine(f"sqlite:///{database_file_path}")


def getMonthlySpending(user_id: str, start_of_period: str, end_of_period: str):
    """
    Calculate the total amount the user spent on charging sessions in a specific period month.
    """
    try:
        query = f"""
        SELECT SUM(amount) AS total_spent
        FROM transactions
        WHERE user_id = '{user_id}'
            AND DATE(created_at) BETWEEN '{start_of_period}' AND '{end_of_period}';
        """
        query = text(query)

        with engine.connect() as connection:
            result = pd.read_sql_query(query, connection)
        if not result.empty:
            return result.to_dict("records")[0]
        else:
            return np.nan
    except Exception as e:
        print(e)
        return np.nan


def getAvgTransactionAmount(user_id: str, today: str, n_months: str):
    """
    Get the average transaction amount for the user over the past n months.
    """
    try:
        query = f"""
        SELECT AVG(amount) AS avg_transaction_amount
        FROM transactions
        WHERE user_id = '{user_id}'
            AND DATE(created_at) >= DATE('{today}', '-{n_months} months');

        """
        query = text(query)

        with engine.connect() as connection:
            result = pd.read_sql_query(query, connection)
        if not result.empty:
            return result.to_dict("records")[0]
        else:
            return np.nan
    except Exception as e:
        print(e)
        return np.nan


def getMaxTransactions(user_id: str, n_highest: str):
    """
    Retrieve the highest n transaction (by amount) the user has ever made.
    """
    try:
        query = f"""
        SELECT transactions.created_at, transactions.amount, transactions.created_at, vehicles.model AS vehicle_model
        FROM transactions, vehicles
        WHERE transactions.vehicle_id = vehicles.id
            AND user_id = '{user_id}'
        ORDER BY amount DESC
        LIMIT {n_highest};
        """
        query = text(query)

        with engine.connect() as connection:
            result = pd.read_sql_query(query, connection)
        if not result.empty:
            return result.to_dict("records")[0]
        else:
            return np.nan
    except Exception as e:
        print(e)
        return np.nan


def getMonthlyEnergyUsage(user_id: str, st_date: str, n_months: str):
    """
    Get the total kilowatt-hours (kWh) consumed by the user for each of the last n months.
    """
    try:
        query = f"""
        SELECT strftime('%Y-%m', created_at) AS month,
            SUM(kw_consumed) AS total_kwh
        FROM sessions
        WHERE user_id = '{user_id}'
            AND DATE(created_at) >= DATE('{st_date}', '-{n_months} months')
        GROUP BY month
        ORDER BY month;
        """
        query = text(query)

        with engine.connect() as connection:
            result = pd.read_sql_query(query, connection)
        if not result.empty:
            return result.to_dict("records")[0]
        else:
            return np.nan
    except Exception as e:
        print(e)
        return np.nan


def getMonthlyEnergyPerVehicle(
    user_id: str, today: str, n_months: str, n_vehicles: str = 50
):
    """
    Get the total kilowatt-hours (kWh) consumed by the user for each of the last n months.
    """
    try:
        query = f"""
        SELECT vehicles.model AS vehicle_model,
            SUM(sessions.kw_consumed) AS total_kwh
        FROM sessions, vehicles
        WHERE sessions.user_id = '{user_id}'
            AND sessions.vehicle_id = vehicles.id
            AND DATE(sessions.created_at) >= DATE('{today}', '-{n_months} months')
        GROUP BY vehicle_id
        ORDER BY total_kwh
        LIMIT {n_vehicles};
        """
        query = text(query)

        with engine.connect() as connection:
            result = pd.read_sql_query(query, connection)
        if not result.empty:
            return result.to_dict("records")[0]
        else:
            return np.nan
    except Exception as e:
        print(e)
        return np.nan


def getAvgSessionDurationPerVehicle(user_id: str):
    """
    Compute the average duration of charging sessions for each of the user's vehicles.
    """
    try:
        query = f"""
        SELECT vehicles.model AS vehicle_model,
            AVG(sessions.duration) AS avg_duration_minutes
        FROM sessions, vehicles
        WHERE user_id = '{user_id}'
            AND sessions.vehicle_id = vehicles.id
        GROUP BY vehicle_id;
        """
        query = text(query)

        with engine.connect() as connection:
            result = pd.read_sql_query(query, connection)
        if not result.empty:
            return result.to_dict("records")[0]
        else:
            return np.nan
    except Exception as e:
        print(e)
        return np.nan


def getMostFrequentChargingWeekdays(user_id: str):
    """
    Identify the days of the week when the user most frequently charges their vehicles.
    """
    try:
        query = f"""
        SELECT strftime('%w', created_at) AS weekday,
            COUNT(*) AS session_count
        FROM sessions
        WHERE user_id = '{user_id}'
        GROUP BY weekday
        ORDER BY session_count DESC;
        """
        query = text(query)

        with engine.connect() as connection:
            result = pd.read_sql_query(query, connection)
        if not result.empty:
            return result.to_dict("records")[0]
        else:
            return np.nan
    except Exception as e:
        print(e)
        return np.nan


def getMonthlyUsageTrends(user_id: str):
    """
    Track the user's monthly usage trends in terms of session count, energy consumption, and total spend.
    """
    try:
        query = f"""
        SELECT strftime('%Y-%m', s.created_at) AS month,
            COUNT(s.id) AS total_sessions,
            SUM(s.kw_consumed) AS total_kwh,
            SUM(t.amount) AS total_spent
        FROM sessions s
        JOIN transactions t ON s.id = t.session_id
        WHERE s.user_id = '{user_id}'
        GROUP BY month
        ORDER BY month;
        """
        query = text(query)

        with engine.connect() as connection:
            result = pd.read_sql_query(query, connection)
        if not result.empty:
            return result.to_dict("records")[0]
        else:
            return np.nan
    except Exception as e:
        print(e)
        return np.nan


def getMostEfficientMonth(user_id: str, n_months: str):
    """
    Find the user's most efficient n months based on kWh consumed per minute of session time.
    """
    try:
        query = f"""
        SELECT strftime('%Y-%m', created_at) AS month,
            ROUND(SUM(kw_consumed) * 1.0 / SUM(duration), 3) AS efficiency_kwh_per_min
        FROM sessions
        WHERE user_id = '{user_id}'
        GROUP BY month
        ORDER BY efficiency_kwh_per_min DESC
        LIMIT {n_months};
        """
        query = text(query)

        with engine.connect() as connection:
            result = pd.read_sql_query(query, connection)
        if not result.empty:
            return result.to_dict("records")[0]
        else:
            return np.nan
    except Exception as e:
        print(e)
        return np.nan


def getAvgSessionStats(user_id: str):
    """
    Return the average duration and energy consumption rate (kWh/minute) for the user's sessions.
    """
    try:
        query = f"""
        SELECT AVG(duration) AS avg_duration,
            ROUND(AVG(kw_consumed * 1.0 / duration), 3) AS avg_kwh_per_minute
        FROM sessions
        WHERE user_id = '{user_id}';
        """
        query = text(query)

        with engine.connect() as connection:
            result = pd.read_sql_query(query, connection)
        if not result.empty:
            return result.to_dict("records")[0]
        else:
            return np.nan
    except Exception as e:
        print(e)
        return np.nan


def getNearestStations(n_stations: int):
    # Todo
    # An API from frontend
    pass


def reserveSession(
    user_id: str,
    vehicle_id: str,
    duration: int,
    kw_consumed: float,
    created_at: str,
    session_id: str,
):
    """
    reserve a charging session for a specific vehicle for the user.

    Args:
        user_id (str): UUID of the user.
        vehicle_id (str): ID of the vehicle.
        duration (int): Duration of the session in minutes.
        kw_consumed (float): Energy consumed in kWh.
        created_at (str): Timestamp when the session occurred (format: 'YYYY-MM-DD HH:MM:SS').
        session_id (str): Unique ID of the session.
    """
    try:
        query = f"""
        INSERT INTO sessions (
            user_id, vehicle_id, duration, kw_consumed, created_at, id
        )
        VALUES (
            '{user_id}', '{vehicle_id}', {duration}, {kw_consumed}, '{created_at}', '{session_id}'
        );
        """
        query = text(query)
        with engine.connect() as connection:
            connection.execute(query)
            connection.commit()
        return {"status": "success", "session_id": session_id}
    except Exception as e:
        print(e)
        return {"status": "error", "message": str(e)}


tools_sql = [
    {
        "type": "function",
        "function": {
            "name": "getMonthlySpending",
            "description": getMonthlySpending.__doc__,
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The unique identifier of the user.",
                    },
                    "start_of_period": {
                        "type": "string",
                        "description": "The start date of the period in the format 'YYYY-MM-DD'.",
                    },
                    "end_of_period": {
                        "type": "string",
                        "description": "The end date of the period in the format 'YYYY-MM-DD'.",
                    },
                },
                "required": ["user_id", "start_of_period", "end_of_period"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "getAvgTransactionAmount",
            "description": getAvgTransactionAmount.__doc__,
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The unique identifier of the user.",
                    },
                    "today": {
                        "type": "string",
                        "description": "The current date in the format 'YYYY-MM-DD'.",
                    },
                    "n_months": {
                        "type": "string",
                        "description": "The number of months to consider for calculating the average transaction amount.",
                    },
                },
                "required": ["user_id", "today", "n_months"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "getMaxTransactions",
            "description": getMaxTransactions.__doc__,
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The unique identifier of the user.",
                    },
                    "n_highest": {
                        "type": "string",
                        "description": "The number of highest transactions to retrieve.",
                    },
                },
                "required": ["user_id", "n_highest"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "getMonthlyEnergyUsage",
            "description": getMonthlyEnergyUsage.__doc__,
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The unique identifier of the user.",
                    },
                    "st_date": {
                        "type": "string",
                        "description": "The start date of the period in the format 'YYYY-MM-DD'.",
                    },
                    "n_months": {
                        "type:": "string",
                        "description": "The number of months to consider for calculating the monthly energy usage.",
                    },
                },
                "required": ["user_id", "st_date", "n_months"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "getMonthlyEnergyPerVehicle",
            "description": getMonthlyEnergyPerVehicle.__doc__,
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The unique identifier of the user.",
                    },
                    "today": {
                        "type": "string",
                        "description": "The current date in the format 'YYYY-MM-DD'.",
                    },
                    "n_months": {
                        "type": "string",
                        "description": "The number of months to consider for calculating the monthly energy usage per vehicle.",
                    },
                    "n_vehicles": {
                        "type": "string",
                        "description": "The number of vehicles to consider for calculating the monthly energy usage per vehicle.",
                    },
                },
                "required": ["user_id", "today", "n_months", "n_vehicles"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "getAvgSessionDurationPerVehicle",
            "description": getAvgSessionDurationPerVehicle.__doc__,
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The unique identifier of the user.",
                    }
                },
                "required": ["user_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "getMostFrequentChargingWeekdays",
            "description": getMostFrequentChargingWeekdays.__doc__,
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The unique identifier of the user.",
                    }
                },
                "required": ["user_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "getMonthlyUsageTrends",
            "description": getMonthlyUsageTrends.__doc__,
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The unique identifier of the user.",
                    }
                },
                "required": ["user_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "getMostEfficientMonth",
            "description": getMostEfficientMonth.__doc__,
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The unique identifier of the user.",
                    },
                    "n_months": {
                        "type": "string",
                        "description": "The number of months to consider for calculating the most efficient month.",
                    },
                },
                "required": ["user_id", "n_months"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "getAvgSessionStats",
            "description": getAvgSessionStats.__doc__,
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The unique identifier of the user.",
                    }
                },
                "required": ["user_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "reserveSession",
            "description": reserveSession.__doc__,
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The unique identifier of the user.",
                    },
                    "vehicle_id": {
                        "type": "string",
                        "description": "The unique identifier of the vehicle.",
                    },
                    "duration": {
                        "type": "integer",
                        "description": "The duration of the session in minutes.",
                    },
                    "kw_consumed": {
                        "type": "number",
                        "description": "The energy consumed in kWh.",
                    },
                    "created_at": {
                        "type": "string",
                        "description": "The timestamp when the session occurred (format: 'YYYY-MM-DD HH:MM:SS').",
                    },
                    "session_id": {
                        "type": "string",
                        "description": "The unique identifier of the session.",
                    },
                },
                "required": [
                    "user_id",
                    "vehicle_id",
                    "duration",
                    "kw_consumed",
                    "created_at",
                    "session_id",
                ],
            },
        },
    },
]


instructions = """
You are an AI assistant specialized in electric vehicle topics and user-specific reservation services. You must strictly follow these rules:

1. **Domain Scope**
   • Only answer questions related to electric vehicles (models, charging types, stations), user driving history, session reservations, connectors, pricing, availability, and related dataset information.
   • Do not answer any questions outside this scope.

2. **Data Source Enforcement**
   • All your responses must come exclusively from our database, accessed via the provided predefined functions.
   • Use our Retrieval‑Augmented Generation (RAG) system to look up data in real time.
   • Do not reference or hallucinate any external knowledge.

3. **Privacy & Abstraction**
   • You must not mention or expose user identifiers like user_id in the chat. All user-specific context is handled implicitly by the system. Respond naturally as if you already know which user is speaking.
   • Never expose internal identifiers like user_id, station_id, car_id, reservation_id, tokens, etc.
   • Replace these with human‑readable labels (e.g., “this vehicle”, “your reserved session at a station”).
   • Only reveal information directly relevant to the user’s query.

4. **Function Calling**
   • Detect user intent (e.g., “reserve a session”, “show my charging history”, “find nearby stations”).
   • Call the appropriate function(s) with correct parameters.
   • Use the returned structured data to should craft your answer.

5. **Answer Style**
   • Use concise, user-centered language.
   • Format answers with markdown headings and bullet points as appropriate.
   • Cite your RAG‑retrieved facts with inline references using the retrieval function metadata.

7. **Reservation Flow Example**
   • User: “Reserve a charging session at Station A tomorrow 3 pm.”
   • Assistant:
     1. Calls `find_station(name="Station A")` → returns station object.
     2. Calls `reserve_session(user, station, datetime)` → returns session details.
     3. Responds:
        ## ✅ Reservation Confirmed
        - Station: Station A
        - Time: July 2, 2025 – 3:00 pm
        - Connector: CCS
        - Enjoy your charging session!

8. **Session History Example**
   • User: “Show my last five charging sessions.”
   • Assistant:
     1. Calls `list_user_sessions(user, limit=5)` → returns session list.
     2. Formats a table:
        | Date | Station | Duration | Energy (kWh) | Cost |
        etc.

9. **Station Search Example**
   • User: “Where are nearby fast‑charge stations?”
   • Assistant:
     1. Calls `find_nearby_stations(user_location, connector="DC fast", radius_km=10)`
     2. Lists stations with availability, distance, connectors.

Always ground your answer in data returned by our database and functions, without revealing any internal IDs.
"""

if __name__ == "__main__":
    inspector = inspect(engine)
    # 3. List all tables in the public schema
    table_names = inspector.get_table_names()
    print("Tables:", table_names)

    # 4. For each table, list its columns
    for table in table_names:
        columns = inspector.get_columns(table)
        col_names = [col["name"] for col in columns]
        print(f"Table {table!r} columns: {col_names}")
