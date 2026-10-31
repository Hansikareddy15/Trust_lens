"""
Integration tests for FastAPI endpoints: /api/health, /api/samples, /api/analyze-json, and /api/export/markdown.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "model_configured" in data
    assert "has_api_key" in data


@pytest.mark.asyncio
async def test_samples_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/samples")
    assert response.status_code == 200
    samples = response.json()
    assert len(samples) >= 4
    sample_ids = [s["id"] for s in samples]
    assert "sample_fake_internship_fee" in sample_ids
    assert "sample_legitimate_offer" in sample_ids


@pytest.mark.asyncio
async def test_analyze_text_json_endpoint():
    transport = ASGITransport(app=app)
    payload = {
        "text": "Offer from Tech Corp. Please pay Rs. 3000 registration fee within 24 hours. Contact on WhatsApp: +919876543210. Email: hr@gmail.com",
        "source_label": "Test Payload"
    }
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/analyze-json", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert "analysis_id" in res
    assert "score" in res
    assert res["score"]["risk_level"] in ("High", "Medium")
    assert len(res["rule_hits"]) > 0


@pytest.mark.asyncio
async def test_export_markdown_endpoint():
    transport = ASGITransport(app=app)
    # First analyze
    payload = {
        "text": "Standard legitimate offer with no registration fee. Contact hr@decodelabs.com. Headquarters: Austin TX.",
        "source_label": "Legitimate Test"
    }
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        analysis_res = await ac.post("/api/analyze-json", json=payload)
        analysis_data = analysis_res.json()

        # Now export
        export_res = await ac.post("/api/export/markdown", json=analysis_data)
    assert export_res.status_code == 200
    md = export_res.text
    assert "# TrustLens AI - Document Risk Assessment Report" in md
    assert "Preliminary assessment, not proof of fraud" in md


@pytest.mark.asyncio
async def test_graph_and_tree_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        graph_res = await ac.get("/graph")
        assert graph_res.status_code == 200
        assert "vis-network" in graph_res.text

        tree_res = await ac.get("/tree")
        assert tree_res.status_code == 200
        assert "d3" in tree_res.text.lower()

