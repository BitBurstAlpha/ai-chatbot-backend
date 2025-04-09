from datetime import datetime
from . import api_v1_bp
from typing import Dict, Any
from flask import current_app

from flask import jsonify


@api_v1_bp.route("/health", methods=["GET"])
def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for monitoring and load balancers.
    
    Returns:
        dict: Health status information
    """
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "app_name": current_app.config["APP_NAME"],
        "version": "1.0.0"  # Should be loaded from package version
    })