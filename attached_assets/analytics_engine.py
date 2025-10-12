"""
AlphaVox - Analytics Engine
-------------------------
Author: Everett Christman & Python AI
Project: The Christman AI Project - AlphaVox
Mission: Legends are our only option

This module provides robust data tracking and analytics capabilities for AlphaVox,
allowing comprehensive tracking of user interactions, progress, and communication patterns.
It serves as the foundation for evidence-based assessment and personalized adaptations.
"""

import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd


class AnalyticsEngine:
    """A comprehensive analytics engine for tracking user interactions with
    AlphaVox.

    Uses pandas DataFrames for efficient data processing and analysis.
    """

    def __init__(self, data_dir="data"):
        """Initialize the analytics engine.

        Args:
            data_dir: Directory for storing data files
        """
        self.data_dir = data_dir
        Path(data_dir).mkdir(exist_ok=True)

        # Initialize DataFrames for tracking different interaction types
        self.interactions_df = self._load_or_create_df(
            "interactions.csv",
            columns=[
                "user_id",
                "interaction_type",
                "input",
                "output",
                "confidence",
                "timestamp",
            ],
        )

        self.symbol_selections_df = self._load_or_create_df(
            "symbol_selections.csv",
            columns=["user_id", "symbol", "context", "timestamp"],
        )

        self.games_df = self._load_or_create_df(
            "games.csv",
            columns=["user_id", "game_type", "score", "duration", "timestamp"],
        )

        self.training_access_df = self._load_or_create_df(
            "training_access.csv",
            columns=["user_id", "tutorial_id", "completion_status", "timestamp"],
        )

        self.points_df = self._load_or_create_df(
            "points.csv", columns=["user_id", "points", "reason", "timestamp"]
        )

        self.sessions_df = self._load_or_create_df(
            "sessions.csv",
            columns=[
                "user_id",
                "session_id",
                "start_time",
                "end_time",
                "duration",
                "interaction_count",
            ],
        )

    def _load_or_create_df(self, filename, columns):
        """Load a DataFrame from CSV or create a new one if it doesn't
        exist."""
        filepath = os.path.join(self.data_dir, filename)
        if os.path.exists(filepath):
            return pd.read_csv(filepath)
        else:
            return pd.DataFrame(columns=columns)

    def _save_df(self, df, filename):
        """Save a DataFrame to CSV."""
        filepath = os.path.join(self.data_dir, filename)
        df.to_csv(filepath, index=False)

    def log_interaction(
        self,
        user_id,
        interaction_type,
        input_data=None,
        output_data=None,
        confidence=None,
    ):
        """Log a user interaction.

        Args:
            user_id: User identifier
            interaction_type: Type of interaction (e.g., 'gesture', 'vocalization', 'eye_movement')
            input_data: Input data (optional)
            output_data: Output response (optional)
            confidence: Confidence score (optional)
        """
        new_row = pd.DataFrame(
            [
                {
                    "user_id": user_id,
                    "interaction_type": interaction_type,
                    "input": str(input_data) if input_data is not None else None,
                    "output": str(output_data) if output_data is not None else None,
                    "confidence": confidence,
                    "timestamp": datetime.now(),
                }
            ]
        )

        self.interactions_df = pd.concat(
            [self.interactions_df, new_row], ignore_index=True
        )
        self._save_df(self.interactions_df, "interactions.csv")
        return True

    def log_symbol_selection(self, user_id, symbol, context=None):
        """Log an AAC symbol selection.

        Args:
            user_id: User identifier
            symbol: Selected symbol
            context: Context of selection (optional)
        """
        new_row = pd.DataFrame(
            [
                {
                    "user_id": user_id,
                    "symbol": symbol,
                    "context": context,
                    "timestamp": datetime.now(),
                }
            ]
        )

        self.symbol_selections_df = pd.concat(
            [self.symbol_selections_df, new_row], ignore_index=True
        )
        self._save_df(self.symbol_selections_df, "symbol_selections.csv")
        return True

    def log_game_activity(self, user_id, game_type, score=None, duration=None):
        """Log a game activity.

        Args:
            user_id: User identifier
            game_type: Type of game
            score: Game score (optional)
            duration: Game duration in seconds (optional)
        """
        new_row = pd.DataFrame(
            [
                {
                    "user_id": user_id,
                    "game_type": game_type,
                    "score": score,
                    "duration": duration,
                    "timestamp": datetime.now(),
                }
            ]
        )

        self.games_df = pd.concat([self.games_df, new_row], ignore_index=True)
        self._save_df(self.games_df, "games.csv")
        return True

    def log_training_access(self, user_id, tutorial_id, completion_status=None):
        """Log access to training materials.

        Args:
            user_id: User identifier
            tutorial_id: Training material identifier
            completion_status: Completion status (optional)
        """
        new_row = pd.DataFrame(
            [
                {
                    "user_id": user_id,
                    "tutorial_id": tutorial_id,
                    "completion_status": completion_status,
                    "timestamp": datetime.now(),
                }
            ]
        )

        self.training_access_df = pd.concat(
            [self.training_access_df, new_row], ignore_index=True
        )
        self._save_df(self.training_access_df, "training_access.csv")
        return True

    def log_points(self, user_id, points, reason=None):
        """Log points earned.

        Args:
            user_id: User identifier
            points: Number of points
            reason: Reason for points (optional)
        """
        new_row = pd.DataFrame(
            [
                {
                    "user_id": user_id,
                    "points": points,
                    "reason": reason,
                    "timestamp": datetime.now(),
                }
            ]
        )

        self.points_df = pd.concat([self.points_df, new_row], ignore_index=True)
        self._save_df(self.points_df, "points.csv")
        return True

    def start_session(self, user_id):
        """Start a new session.

        Args:
            user_id: User identifier

        Returns:
            session_id: Unique session identifier
        """
        session_id = f"{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        new_row = pd.DataFrame(
            [
                {
                    "user_id": user_id,
                    "session_id": session_id,
                    "start_time": datetime.now(),
                    "end_time": None,
                    "duration": None,
                    "interaction_count": 0,
                }
            ]
        )

        self.sessions_df = pd.concat([self.sessions_df, new_row], ignore_index=True)
        self._save_df(self.sessions_df, "sessions.csv")
        return session_id

    def end_session(self, session_id):
        """End a session.

        Args:
            session_id: Session identifier
        """
        if session_id in self.sessions_df["session_id"].values:
            idx = self.sessions_df[self.sessions_df["session_id"] == session_id].index[
                0
            ]
            start_time = pd.to_datetime(self.sessions_df.at[idx, "start_time"])
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # Get interaction count for this session
            user_id = self.sessions_df.at[idx, "user_id"]
            if not pd.isna(start_time):
                interactions = self.interactions_df[
                    (self.interactions_df["user_id"] == user_id)
                    & (pd.to_datetime(self.interactions_df["timestamp"]) >= start_time)
                    & (pd.to_datetime(self.interactions_df["timestamp"]) <= end_time)
                ]
                interaction_count = len(interactions)
            else:
                interaction_count = 0

            # Update session record
            self.sessions_df.at[idx, "end_time"] = end_time
            self.sessions_df.at[idx, "duration"] = duration
            self.sessions_df.at[idx, "interaction_count"] = interaction_count
            self._save_df(self.sessions_df, "sessions.csv")
            return True
        return False

    def get_user_stats(self, user_id):
        """Get statistics for a specific user.

        Args:
            user_id: User identifier

        Returns:
            Dictionary with user statistics
        """
        user_interactions = self.interactions_df[
            self.interactions_df["user_id"] == user_id
        ]
        user_sessions = self.sessions_df[self.sessions_df["user_id"] == user_id]
        user_games = self.games_df[self.games_df["user_id"] == user_id]
        user_symbols = self.symbol_selections_df[
            self.symbol_selections_df["user_id"] == user_id
        ]
        user_points = self.points_df[self.points_df["user_id"] == user_id]

        # Calculate statistics
        interaction_count = len(user_interactions)
        session_count = len(user_sessions)
        avg_session_duration = (
            user_sessions["duration"].mean()
            if not user_sessions.empty and "duration" in user_sessions
            else 0
        )
        total_points = user_points["points"].sum() if not user_points.empty else 0

        # Calculate most used interaction type
        most_used_type = None
        if not user_interactions.empty and "interaction_type" in user_interactions:
            type_counts = user_interactions["interaction_type"].value_counts()
            if not type_counts.empty:
                most_used_type = type_counts.index[0]

        # Calculate most selected symbol
        most_used_symbol = None
        if not user_symbols.empty and "symbol" in user_symbols:
            symbol_counts = user_symbols["symbol"].value_counts()
            if not symbol_counts.empty:
                most_used_symbol = symbol_counts.index[0]

        # Calculate game performance
        avg_score = (
            user_games["score"].mean()
            if not user_games.empty and "score" in user_games
            else 0
        )

        # Create and return stats dictionary
        stats = {
            "user_id": user_id,
            "total_interactions": interaction_count,
            "total_sessions": session_count,
            "avg_session_duration": avg_session_duration,
            "total_points": total_points,
            "most_used_interaction": most_used_type,
            "most_used_symbol": most_used_symbol,
            "avg_game_score": avg_score,
        }

        return stats

    def get_progress_report(self, user_id, days=30):
        """Generate a progress report for a user over the specified time
        period.

        Args:
            user_id: User identifier
            days: Number of days to include in the report (default: 30)

        Returns:
            Dictionary with progress report data
        """
        cutoff_date = datetime.now() - pd.Timedelta(days=days)

        # Filter data for the specified time period
        user_interactions = self.interactions_df[
            (self.interactions_df["user_id"] == user_id)
            & (pd.to_datetime(self.interactions_df["timestamp"]) >= cutoff_date)
        ]

        user_symbols = self.symbol_selections_df[
            (self.symbol_selections_df["user_id"] == user_id)
            & (pd.to_datetime(self.symbol_selections_df["timestamp"]) >= cutoff_date)
        ]

        user_games = self.games_df[
            (self.games_df["user_id"] == user_id)
            & (pd.to_datetime(self.games_df["timestamp"]) >= cutoff_date)
        ]

        # Calculate daily statistics
        if not user_interactions.empty and "timestamp" in user_interactions:
            user_interactions["date"] = pd.to_datetime(
                user_interactions["timestamp"]
            ).dt.date
            daily_interactions = (
                user_interactions.groupby("date").size().reset_index(name="count")
            )
            daily_interactions["date"] = pd.to_datetime(daily_interactions["date"])
        else:
            daily_interactions = pd.DataFrame(columns=["date", "count"])

        if not user_symbols.empty and "timestamp" in user_symbols:
            user_symbols["date"] = pd.to_datetime(user_symbols["timestamp"]).dt.date
            daily_symbols = (
                user_symbols.groupby("date").size().reset_index(name="count")
            )
            daily_symbols["date"] = pd.to_datetime(daily_symbols["date"])
        else:
            daily_symbols = pd.DataFrame(columns=["date", "count"])

        if not user_games.empty and "timestamp" in user_games and "score" in user_games:
            user_games["date"] = pd.to_datetime(user_games["timestamp"]).dt.date
            daily_scores = (
                user_games.groupby("date")["score"].mean().reset_index(name="avg_score")
            )
            daily_scores["date"] = pd.to_datetime(daily_scores["date"])
        else:
            daily_scores = pd.DataFrame(columns=["date", "avg_score"])

        # Convert DataFrames to lists for JSON serialization
        daily_interactions_list = (
            daily_interactions.to_dict("records")
            if not daily_interactions.empty
            else []
        )
        daily_symbols_list = (
            daily_symbols.to_dict("records") if not daily_symbols.empty else []
        )
        daily_scores_list = (
            daily_scores.to_dict("records") if not daily_scores.empty else []
        )

        # Create progress report
        report = {
            "user_id": user_id,
            "period_days": days,
            "daily_interactions": daily_interactions_list,
            "daily_symbols": daily_symbols_list,
            "daily_scores": daily_scores_list,
            "total_interactions": len(user_interactions),
            "total_symbols": len(user_symbols),
            "avg_game_score": (
                user_games["score"].mean()
                if not user_games.empty and "score" in user_games
                else 0
            ),
        }

        return report

    def get_therapeutic_insights(self, user_id):
        """Generate therapeutic insights based on user data.

        Args:
            user_id: User identifier

        Returns:
            Dictionary with therapeutic insights
        """
        user_interactions = self.interactions_df[
            self.interactions_df["user_id"] == user_id
        ]
        user_symbols = self.symbol_selections_df[
            self.symbol_selections_df["user_id"] == user_id
        ]

        insights = {
            "user_id": user_id,
            "communication_preferences": {},
            "progress_indicators": [],
            "challenge_areas": [],
            "recommendations": [],
        }

        # Analyze communication preferences
        if not user_interactions.empty and "interaction_type" in user_interactions:
            type_counts = user_interactions["interaction_type"].value_counts()
            for interaction_type, count in type_counts.items():
                insights["communication_preferences"][interaction_type] = count

        # Analyze symbol usage patterns
        if not user_symbols.empty and "symbol" in user_symbols:
            symbols_used = user_symbols["symbol"].nunique()
            most_used = user_symbols["symbol"].value_counts().head(5).to_dict()

            insights["symbol_usage"] = {
                "unique_symbols_used": symbols_used,
                "most_frequent": most_used,
            }

            # Generate progress indicators
            if symbols_used > 10:
                insights["progress_indicators"].append("Diverse symbol vocabulary")

            # Generate challenge areas
            if symbols_used < 5:
                insights["challenge_areas"].append("Limited symbol vocabulary")
                insights["recommendations"].append("Introduce new symbols gradually")

        # Analyze interaction patterns over time
        if not user_interactions.empty and "timestamp" in user_interactions:
            user_interactions["timestamp"] = pd.to_datetime(
                user_interactions["timestamp"]
            )
            user_interactions = user_interactions.sort_values("timestamp")

            # Check for increased interaction frequency
            if len(user_interactions) >= 10:
                first_half = user_interactions.iloc[: len(user_interactions) // 2]
                second_half = user_interactions.iloc[len(user_interactions) // 2 :]

                first_half_days = (
                    first_half["timestamp"].max() - first_half["timestamp"].min()
                ).days or 1
                second_half_days = (
                    second_half["timestamp"].max() - second_half["timestamp"].min()
                ).days or 1

                first_rate = len(first_half) / first_half_days
                second_rate = len(second_half) / second_half_days

                if second_rate > first_rate * 1.2:  # 20% increase
                    insights["progress_indicators"].append(
                        "Increasing interaction frequency"
                    )
                elif second_rate < first_rate * 0.8:  # 20% decrease
                    insights["challenge_areas"].append(
                        "Decreasing interaction frequency"
                    )
                    insights["recommendations"].append(
                        "Consider introducing new motivating activities"
                    )

        return insights

    def generate_user_report(self, user_id, format="json"):
        """Generate a comprehensive user report.

        Args:
            user_id: User identifier
            format: Output format ('json' or 'html')

        Returns:
            Report in the specified format
        """
        stats = self.get_user_stats(user_id)
        progress = self.get_progress_report(user_id)
        insights = self.get_therapeutic_insights(user_id)

        report = {
            "user_id": user_id,
            "generated_at": datetime.now().isoformat(),
            "statistics": stats,
            "progress": progress,
            "insights": insights,
        }

        if format == "json":
            return json.dumps(report, indent=2)
        elif format == "html":
            # Simple HTML report (could be enhanced with more styling)
            html = "<html><head><title>User Report</title></head><body>"
            html += f"<h1>AlphaVox User Report: {user_id}</h1>"
            html += f"<p>Generated: {report['generated_at']}</p>"

            html += "<h2>Statistics</h2>"
            html += "<ul>"
            for key, value in stats.items():
                if key != "user_id":
                    html += f"<li>{key}: {value}</li>"
            html += "</ul>"

            html += "<h2>Progress Indicators</h2>"
            html += "<ul>"
            for indicator in insights["progress_indicators"]:
                html += f"<li>{indicator}</li>"
            html += "</ul>"

            html += "<h2>Challenge Areas</h2>"
            html += "<ul>"
            for challenge in insights["challenge_areas"]:
                html += f"<li>{challenge}</li>"
            html += "</ul>"

            html += "<h2>Recommendations</h2>"
            html += "<ul>"
            for recommendation in insights["recommendations"]:
                html += f"<li>{recommendation}</li>"
            html += "</ul>"

            html += "</body></html>"
            return html
        else:
            raise ValueError(f"Unsupported format: {format}")


# Create a single instance to be used across the application
analytics = AnalyticsEngine()
