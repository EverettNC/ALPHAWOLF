"""Additional API endpoint registrations for Derek Dashboard."""

from flask import Blueprint, jsonify

bp = Blueprint("derek_extra_endpoints", __name__)


@bp.route("/api/ping", methods=["GET"])
def ping():
    """Simple liveness probe."""
    return jsonify({"status": "ok", "message": "Derek Dashboard heartbeat"})
