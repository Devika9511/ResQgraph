def test_project_has_parameterized_driver_queries():
    from pathlib import Path
    text=Path('services/incident_service.py').read_text()
    assert 'session.run' in text and 'incident_id=incident_id' in text
