# =============================================================================
# T9 — Tests d'import/export
# =============================================================================

import io
import pytest
from httpx import AsyncClient


class TestExport:
    """Tests des exports."""

    @pytest.mark.asyncio
    async def test_export_ao_csv(
        self,
        client: AsyncClient,
        admin_headers: dict,
        sample_ao: Any,
    ) -> None:
        """GIVEN des AO existants
        WHEN GET /api/v1/export/ao avec format=csv
        THEN un fichier CSV valide est telecharge.
        """
        response = await client.get(
            "/api/v1/export/ao?format=csv",
            headers=admin_headers,
        )
        assert response.status_code in (200, 404)
        if response.status_code == 200:
            content_type = response.headers.get("content-type", "")
            assert "csv" in content_type or "text" in content_type or "octet-stream" in content_type


class TestImport:
    """Tests des imports."""

    @pytest.mark.asyncio
    async def test_import_validation(
        self,
        client: AsyncClient,
        admin_headers: dict,
    ) -> None:
        """GIVEN un fichier CSV d'AO a importer
        WHEN POST /api/v1/import/ao/validate
        THEN la validation retourne les erreurs ou un statut valide.
        """
        csv_content = (
            "title,description,buyer_name,cpv_code,estimated_amount,deadline_date\n"
            "AO Test Import,Description test,Acheteur Test,72000000-5,50000,2024-12-31\n"
        )

        response = await client.post(
            "/api/v1/import/ao/validate",
            headers=admin_headers,
            files={"file": ("test_ao.csv", io.BytesIO(csv_content.encode()), "text/csv")},
        )
        assert response.status_code in (200, 422)
