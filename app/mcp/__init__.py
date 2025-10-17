from flask import Blueprint

mcp_bp = Blueprint('mcp', __name__)

from . import routes  # noqa: F401
