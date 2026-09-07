from app.models.analysis_result import AnalysisResult


def test_analysis_result_table_name():
    assert AnalysisResult.__tablename__ == "analysis_results"


def test_analysis_result_columns():
    columns = {c.name for c in AnalysisResult.__table__.columns}
    assert columns == {
        "id",
        "profile_id",
        "five_elements",
        "missing_elements",
        "excess_elements",
        "sinsal",
        "created_at",
        "updated_at",
    }


def test_profile_id_is_unique():
    profile_id_col = AnalysisResult.__table__.columns["profile_id"]
    assert profile_id_col.unique is True
