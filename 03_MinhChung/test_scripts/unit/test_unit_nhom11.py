"""Unit test nhóm 11 - Kiểm thử ứng dụng RAG (PrivateGPT).

Chạy từ thư mục source_code:
    .venv/Scripts/python -m pytest ../03_MinhChung/test_scripts/unit -v

Mỗi class tương ứng với chức năng của một thành viên:
  - TestIngest_Tien      : Nạp tài liệu (IngestBody, FileArtifact, TextArtifact)
  - TestDocMgmt_Vinh     : Quản lý tài liệu (DeleteIngestedDocumentBody, ContextFilter)
  - TestRagChat_Duy      : Hỏi đáp RAG có trích dẫn (ChatBody, citation parser)
  - TestSession_Manh     : Hội thoại & mô hình (ChatBody nhiều lượt, tham số sinh)
"""

import base64

import pytest
from pydantic import ValidationError

from private_gpt.server.ingest.ingest_router import (
    DeleteIngestedDocumentBody,
    IngestBody,
)
from private_gpt.server.utils.artifact_input import (
    FileArtifact,
    _is_valid_base64,
    _is_valid_uri,
)
from private_gpt.server.chat.chat_models import ChatBody
from private_gpt.components.engines.citations.types import Document
from private_gpt.components.engines.citations.utils import (
    extract_citations_by_original_text,
    format_cite,
)


def b64(text: str) -> str:
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


# ---------------------------------------------------------------------------
# Nguyễn Minh Tiến - Nạp tài liệu (Ingest)
# ---------------------------------------------------------------------------
class TestIngest_Tien:
    def test_UT_TIEN_01_base64_hop_le(self):
        assert _is_valid_base64(b64("Xin chào RAG")) is True

    def test_UT_TIEN_02_base64_rong(self):
        assert _is_valid_base64("") is False

    def test_UT_TIEN_03_base64_sai_ky_tu(self):
        assert _is_valid_base64("@@@###") is False

    def test_UT_TIEN_04_base64_thieu_padding(self):
        assert _is_valid_base64("YWJj ZA") is False

    def test_UT_TIEN_05_base64_data_uri_bi_tu_choi(self):
        assert _is_valid_base64("data:text/plain;base64," + b64("abc")) is False

    def test_UT_TIEN_06_ingest_body_hop_le_mac_dinh_collection(self):
        body = IngestBody(artifact="doc1", input={"type": "text", "value": "abc"})
        assert body.collection == "pgpt_collection"

    def test_UT_TIEN_07_artifact_rong_bi_tu_choi(self):
        with pytest.raises(ValidationError):
            IngestBody(artifact="", input={"type": "text", "value": "abc"})

    def test_UT_TIEN_08_artifact_255_ky_tu_bien_tren(self):
        body = IngestBody(artifact="a" * 255, input={"type": "text", "value": "x"})
        assert len(body.artifact) == 255

    def test_UT_TIEN_09_artifact_256_ky_tu_vuot_bien(self):
        with pytest.raises(ValidationError):
            IngestBody(artifact="a" * 256, input={"type": "text", "value": "x"})

    def test_UT_TIEN_10_input_type_khong_ho_tro(self):
        with pytest.raises(ValidationError):
            IngestBody(artifact="d", input={"type": "video", "value": "x"})

    def test_UT_TIEN_11_file_artifact_giai_ma_dung_noi_dung(self):
        art = FileArtifact(value=b64("Nội dung tiếng Việt"))
        content = art.to_binary_content("a.txt")
        assert content.data.read().decode("utf-8") == "Nội dung tiếng Việt"
        assert content.filename == "a.txt"

    def test_UT_TIEN_12_artifact_chua_path_traversal_van_duoc_chap_nhan(self):
        """Phát hiện lỗi: không có ràng buộc pattern cho artifact/collection."""
        body = IngestBody(
            artifact="../../etc/passwd",
            collection="../outside",
            input={"type": "text", "value": "x"},
        )
        # Kỳ vọng theo checklist bảo mật: phải bị từ chối -> test ghi nhận hành vi thực tế
        assert body.artifact == "../../etc/passwd"

    def test_UT_TIEN_13_uri_hop_le(self):
        assert _is_valid_uri("https://example.com/a.pdf") is True
        assert _is_valid_uri("C:\\Windows\\win.ini") is False


# ---------------------------------------------------------------------------
# Nguyễn Bá Quang Vinh - Quản lý tài liệu (List / Delete / Content)
# ---------------------------------------------------------------------------
class TestDocMgmt_Vinh:
    def test_UT_VINH_01_delete_body_hop_le(self):
        b = DeleteIngestedDocumentBody(collection="c1", artifact="a1")
        assert (b.collection, b.artifact) == ("c1", "a1")

    def test_UT_VINH_02_delete_thieu_collection(self):
        with pytest.raises(ValidationError):
            DeleteIngestedDocumentBody(artifact="a1")

    def test_UT_VINH_03_delete_collection_rong(self):
        with pytest.raises(ValidationError):
            DeleteIngestedDocumentBody(collection="", artifact="a1")

    def test_UT_VINH_04_delete_artifact_rong(self):
        with pytest.raises(ValidationError):
            DeleteIngestedDocumentBody(collection="c", artifact="")

    def test_UT_VINH_05_delete_artifact_bien_255(self):
        assert DeleteIngestedDocumentBody(collection="c", artifact="x" * 255)

    def test_UT_VINH_06_delete_artifact_256_vuot_bien(self):
        with pytest.raises(ValidationError):
            DeleteIngestedDocumentBody(collection="c", artifact="x" * 256)

    def test_UT_VINH_07_delete_artifact_sai_kieu(self):
        with pytest.raises(ValidationError):
            DeleteIngestedDocumentBody(collection="c", artifact=["a"])

    def test_UT_VINH_08_collection_ky_tu_dac_biet_khong_bi_chan(self):
        """Phát hiện lỗi: collection '../x' được chấp nhận (nguy cơ path traversal)."""
        b = DeleteIngestedDocumentBody(collection="../x", artifact="a")
        assert b.collection == "../x"


# ---------------------------------------------------------------------------
# Vũ Đức Duy - Hỏi đáp RAG có trích dẫn
# ---------------------------------------------------------------------------
def _doc(cid: str) -> Document:
    return Document(
        type="document",
        id_=f"source-{cid}",
        shorter_id=cid,
        document_id=f"artifact-{cid}",
        text=f"Content for {cid}",
    )


RAG_TOOLS = [{"name": "semantic_search", "type": "semantic_search_v1"}]
RAG_CTX = [
    {
        "type": "ingested_artifact",
        "context_filter": {"collection": "nhom11", "artifacts": []},
    }
]


class TestRagChat_Duy:
    def test_UT_DUY_01_chatbody_rag_hop_le(self):
        body = ChatBody(
            model="llama3.2",
            messages=[{"role": "user", "content": "Số ngày phép năm?"}],
            tools=RAG_TOOLS,
            tool_context=RAG_CTX,
            system={"citations": {"enabled": True}},
        )
        assert body.tools and body.tool_context

    def test_UT_DUY_02_messages_rong_bi_tu_choi(self):
        with pytest.raises(ValidationError):
            ChatBody(model="llama3.2", messages=[])

    def test_UT_DUY_03_content_rong_bi_tu_choi(self):
        with pytest.raises(ValidationError):
            ChatBody(model="llama3.2", messages=[{"role": "user", "content": ""}])

    def test_UT_DUY_04_role_khong_hop_le(self):
        with pytest.raises(ValidationError):
            ChatBody(model="llama3.2", messages=[{"role": "hacker", "content": "x"}])

    def test_UT_DUY_05_semantic_search_thieu_tool_context(self):
        with pytest.raises((ValidationError, ValueError)):
            ChatBody(
                model="llama3.2",
                messages=[{"role": "user", "content": "x"}],
                tools=RAG_TOOLS,
            )

    def test_UT_DUY_06_citation_hop_le_duoc_chuyen_doi(self):
        d = _doc("AB12")
        out, cits, _ = extract_citations_by_original_text("Câu trả lời [AB12].", [d])
        assert out == f"Câu trả lời {format_cite(0, d, 0)}."
        assert len(cits) == 1

    def test_UT_DUY_07_citation_khong_phan_biet_hoa_thuong(self):
        d = _doc("AB12")
        _, cits, _ = extract_citations_by_original_text("x [ab12].", [d])
        assert len(cits) == 1

    def test_UT_DUY_08_citation_bia_dat_bi_loai(self):
        d = _doc("AB12")
        _, cits, _ = extract_citations_by_original_text("x [ZZ99, AB12].", [d])
        assert len(cits) == 1

    def test_UT_DUY_09_citation_hoan_toan_bia_dat(self):
        """Ghi nhận: id bịa đặt hoàn toàn bị giữ nguyên dạng text thô."""
        d = _doc("AB12")
        out, cits, _ = extract_citations_by_original_text("x [ZZ99].", [d])
        assert len(cits) == 0
        assert "ZZ99" in out

    def test_UT_DUY_10_trich_dan_lap_lai_giu_index(self):
        d = _doc("AB12")
        _, cits, _ = extract_citations_by_original_text("a [AB12] b [AB12].", [d])
        assert [c.value["index"] for c in cits] == ["0", "0"]


# ---------------------------------------------------------------------------
# Bùi Văn Mạnh - Quản lý hội thoại, mô hình & tham số
# ---------------------------------------------------------------------------
class TestSession_Manh:
    def _msgs(self, n):
        out = []
        for i in range(n):
            out.append({"role": "user", "content": f"Câu hỏi {i}"})
            out.append({"role": "assistant", "content": f"Trả lời {i}"})
        out.append({"role": "user", "content": "Câu cuối"})
        return out

    def test_UT_MANH_01_hoi_thoai_nhieu_luot(self):
        b = ChatBody(model="llama3.2", messages=self._msgs(5))
        assert len(b.messages) == 11

    def test_UT_MANH_02_model_mac_dinh_khi_bo_trong(self):
        """Ghi nhận: thiếu model -> tự gán 'default' (tài liệu ghi là bắt buộc)."""
        b = ChatBody(messages=[{"role": "user", "content": "hi"}])
        assert b.model == "default"

    def test_UT_MANH_03_temperature_bien_duoi(self):
        assert ChatBody(model="m", messages=self._msgs(0), temperature=0.0)

    def test_UT_MANH_04_temperature_bien_tren(self):
        assert ChatBody(model="m", messages=self._msgs(0), temperature=1.0)

    def test_UT_MANH_05_temperature_vuot_bien(self):
        with pytest.raises(ValidationError):
            ChatBody(model="m", messages=self._msgs(0), temperature=1.5)

    def test_UT_MANH_06_temperature_am(self):
        with pytest.raises(ValidationError):
            ChatBody(model="m", messages=self._msgs(0), temperature=-0.1)

    def test_UT_MANH_07_top_p_vuot_bien(self):
        with pytest.raises(ValidationError):
            ChatBody(model="m", messages=self._msgs(0), top_p=1.01)

    def test_UT_MANH_08_tin_nhan_cuoi_la_system(self):
        with pytest.raises((ValidationError, ValueError)):
            ChatBody(model="m", messages=[{"role": "system", "content": "x"}])

    def test_UT_MANH_09_max_tokens_bang_0(self):
        """Ghi nhận: max_tokens=0 bị bỏ qua âm thầm thay vì báo lỗi."""
        b = ChatBody(model="m", messages=self._msgs(0), max_tokens=0)
        assert b.max_tokens in (None, 0)
