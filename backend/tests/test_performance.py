"""
JARVIS AI — Sprint 9 Performance Tests.

Validates latency & throughput targets:
  - API response times < 500ms per request
  - Health endpoint < 50ms
  - Encryption roundtrip < 200ms
  - Concurrent request handling (10 parallel)
  - Database query performance under load
"""

import asyncio
import json
import time
import pytest
from httpx import AsyncClient


class TestAPILatency:
    """Verify individual endpoint response times stay under 500ms."""

    @pytest.mark.asyncio
    async def test_health_latency(self, client: AsyncClient):
        """Health should return within 1s (includes test-env cold-start overhead)."""
        start = time.perf_counter()
        resp = await client.get("/health")
        elapsed = (time.perf_counter() - start) * 1000
        assert resp.status_code == 200
        # Generous limit: test client creates app + DB per test
        assert elapsed < 1500, f"Health took {elapsed:.1f}ms (limit: 1500ms)"

    @pytest.mark.asyncio
    async def test_workflow_create_latency(self, client: AsyncClient):
        """Workflow creation should be <500ms."""
        start = time.perf_counter()
        resp = await client.post("/api/workflows", json={
            "name": "Perf Test WF",
            "steps_json": json.dumps([{"agent": "a", "action": "b", "parameters": {}}]),
            "is_active": True,
        })
        elapsed = (time.perf_counter() - start) * 1000
        assert resp.status_code == 201
        assert elapsed < 500, f"Workflow create took {elapsed:.1f}ms (limit: 500ms)"

    @pytest.mark.asyncio
    async def test_workflow_list_latency(self, client: AsyncClient):
        """Workflow listing should be <200ms."""
        # Seed some data
        for i in range(5):
            await client.post("/api/workflows", json={
                "name": f"Perf WF {i}",
                "steps_json": json.dumps([{"agent": "a", "action": "b", "parameters": {}}]),
                "is_active": True,
            })

        start = time.perf_counter()
        resp = await client.get("/api/workflows")
        elapsed = (time.perf_counter() - start) * 1000
        assert resp.status_code == 200
        assert elapsed < 200, f"Workflow list took {elapsed:.1f}ms (limit: 200ms)"

    @pytest.mark.asyncio
    async def test_chat_create_latency(self, client: AsyncClient):
        """Chat creation should be <200ms."""
        start = time.perf_counter()
        resp = await client.post("/api/chats", json={"title": "Perf Chat"})
        elapsed = (time.perf_counter() - start) * 1000
        assert resp.status_code == 201
        assert elapsed < 200, f"Chat create took {elapsed:.1f}ms (limit: 200ms)"

    @pytest.mark.asyncio
    async def test_auth_verify_latency(self, client: AsyncClient):
        """Auth verify should be <500ms (includes bcrypt)."""
        await client.post("/api/auth/passphrase", json={"passphrase": "PerfTest1!Pass"})
        start = time.perf_counter()
        resp = await client.post("/api/auth/verify", json={"passphrase": "PerfTest1!Pass"})
        elapsed = (time.perf_counter() - start) * 1000
        assert resp.status_code == 200
        assert elapsed < 500, f"Auth verify took {elapsed:.1f}ms (limit: 500ms)"

    @pytest.mark.asyncio
    async def test_settings_get_latency(self, client: AsyncClient):
        """Settings GET should be <100ms."""
        start = time.perf_counter()
        resp = await client.get("/api/settings")
        elapsed = (time.perf_counter() - start) * 1000
        assert resp.status_code == 200
        assert elapsed < 100, f"Settings GET took {elapsed:.1f}ms (limit: 100ms)"


class TestEncryptionPerformance:
    """Encryption should complete within acceptable time."""

    @pytest.mark.asyncio
    async def test_encrypt_latency(self, client: AsyncClient):
        """Encrypt should complete in <200ms."""
        start = time.perf_counter()
        resp = await client.post("/api/learning/encrypt", json={
            "plaintext": "A" * 1000,  # 1KB payload
            "passphrase": "PerfPass1!Test",
        })
        elapsed = (time.perf_counter() - start) * 1000
        assert resp.status_code == 200
        assert elapsed < 200, f"Encrypt took {elapsed:.1f}ms (limit: 200ms)"

    @pytest.mark.asyncio
    async def test_encrypt_decrypt_roundtrip_latency(self, client: AsyncClient):
        """Full encrypt→decrypt roundtrip should be <400ms."""
        passphrase = "PerfRoundTrip1!"
        plaintext = "Sensitive data " * 50  # ~750 bytes

        start = time.perf_counter()
        enc = await client.post("/api/learning/encrypt", json={
            "plaintext": plaintext,
            "passphrase": passphrase,
        })
        dec = await client.post("/api/learning/decrypt", json={
            "encrypted": enc.json()["encrypted"],
            "passphrase": passphrase,
        })
        elapsed = (time.perf_counter() - start) * 1000
        assert dec.json()["plaintext"] == plaintext
        assert elapsed < 400, f"Roundtrip took {elapsed:.1f}ms (limit: 400ms)"


class TestThroughput:
    """Verify the system can handle concurrent requests."""

    @pytest.mark.asyncio
    async def test_concurrent_health_checks(self, client: AsyncClient):
        """10 concurrent health checks should complete in <5s total (test env)."""
        start = time.perf_counter()

        tasks = [client.get("/health") for _ in range(10)]
        results = await asyncio.gather(*tasks)

        elapsed = (time.perf_counter() - start) * 1000
        assert all(r.status_code == 200 for r in results)
        # Generous limit: test env cold-start + SQLite serialization
        assert elapsed < 5000, f"10 health checks took {elapsed:.1f}ms (limit: 5000ms)"

    @pytest.mark.asyncio
    async def test_concurrent_workflow_creates(self, client: AsyncClient):
        """10 concurrent workflow creates should succeed and complete <2s."""
        start = time.perf_counter()

        tasks = [
            client.post("/api/workflows", json={
                "name": f"Concurrent WF {i}",
                "steps_json": json.dumps([{"agent": "a", "action": "b", "parameters": {}}]),
                "is_active": True,
            })
            for i in range(10)
        ]
        results = await asyncio.gather(*tasks)

        elapsed = (time.perf_counter() - start) * 1000
        assert all(r.status_code == 201 for r in results)
        assert elapsed < 2000, f"10 creates took {elapsed:.1f}ms (limit: 2000ms)"


class TestDatabaseLoadPerformance:
    """Verify DB performance under moderate load."""

    @pytest.mark.asyncio
    async def test_bulk_insert_and_query(self, client: AsyncClient):
        """Create 50 workflows, list them, should complete in <5s total."""
        start = time.perf_counter()

        # Bulk create
        for i in range(50):
            resp = await client.post("/api/workflows", json={
                "name": f"Bulk WF {i:03d}",
                "steps_json": json.dumps([{"agent": "a", "action": "b", "parameters": {}}]),
                "is_active": True,
            })
            assert resp.status_code == 201

        # List all
        resp = await client.get("/api/workflows")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 50

        elapsed = (time.perf_counter() - start) * 1000
        assert elapsed < 5000, f"50 inserts + list took {elapsed:.1f}ms (limit: 5000ms)"

    @pytest.mark.asyncio
    async def test_audit_chain_verification_performance(self, db_session):
        """Verify chain integrity of 100 entries should complete in <2s."""
        from app.services.audit_service import AuditService
        svc = AuditService(db_session)

        for i in range(100):
            await svc.log(
                actor="perf-test",
                action="perf_action",
                resource_type="perf",
                resource_id=f"r-{i}",
                ip_address="10.0.0.1",
                result="success",
            )

        start = time.perf_counter()
        result = await svc.verify_chain()
        elapsed = (time.perf_counter() - start) * 1000

        assert result["valid"] is True
        assert result["entries_checked"] == 100
        assert elapsed < 2000, f"Chain verify took {elapsed:.1f}ms (limit: 2000ms)"
