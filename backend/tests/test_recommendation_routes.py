from unittest.mock import patch

from app import create_app
from app.utils.fpl_api import FPLAPIError, FPLResourceNotFound


def test_recommendation_route_maps_missing_team_to_404():
    app = create_app()
    with patch("app.routes.recommendation_routes.RecommendationEngine", side_effect=FPLResourceNotFound("Not found")):
        response = app.test_client().get("/api/recommendations/1/transfers")
    assert response.status_code == 404
    assert response.get_json()["error"]["code"] == "not_found"


def test_recommendation_route_maps_fpl_outage_to_502():
    app = create_app()
    with patch("app.routes.recommendation_routes.RecommendationEngine", side_effect=FPLAPIError("Unavailable")):
        response = app.test_client().get("/api/recommendations/1/transfers")
    assert response.status_code == 502
    assert response.get_json()["error"]["retryable"] is True
