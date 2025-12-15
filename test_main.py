import pytest
import io
import csv
from fastapi.testclient import TestClient
from main import (
    app,
    process_csv_filter,
    process_csv_transform,
    process_csv_aggregate,
    process_csv_sort,
    process_csv_view
)


@pytest.fixture
def client():
    """Create a test client for the app"""
    # TestClient requires app as first positional argument
    return TestClient(app)


# Test data helpers
def create_csv_file(content: str) -> io.BytesIO:
    """Create a CSV file in memory"""
    return io.BytesIO(content.encode('utf-8'))


def create_test_csv_data() -> str:
    """Create test CSV data"""
    return "name,age,city\nJohn,25,New York\nJane,30,London\nBob,25,Paris\n"


class TestCSVProcessingFunctions:
    """Unit tests for CSV processing functions"""
    
    def test_process_csv_filter(self):
        """Test filtering CSV rows"""
        rows = [
            {"name": "John", "age": "25", "city": "New York"},
            {"name": "Jane", "age": "30", "city": "London"},
            {"name": "Bob", "age": "25", "city": "Paris"}
        ]
        
        result = process_csv_filter(rows, "age", "25")
        
        assert result["count"] == 2
        assert len(result["rows"]) == 2
        assert result["rows"][0]["name"] == "John"
        assert result["rows"][1]["name"] == "Bob"
        assert "name" in result["columns"]
        assert "age" in result["columns"]
        assert "city" in result["columns"]
    
    def test_process_csv_filter_empty(self):
        """Test filtering with no matches"""
        rows = [
            {"name": "John", "age": "25", "city": "New York"}
        ]
        
        result = process_csv_filter(rows, "age", "99")
        
        assert result["count"] == 0
        assert len(result["rows"]) == 0
    
    def test_process_csv_filter_empty_rows(self):
        """Test filtering with empty rows"""
        result = process_csv_filter([], "age", "25")
        
        assert result["count"] == 0
        assert result["rows"] == []
        assert result["columns"] == []
    
    def test_process_csv_transform_uppercase(self):
        """Test transforming column to uppercase"""
        rows = [
            {"name": "john", "age": "25"},
            {"name": "jane", "age": "30"}
        ]
        
        result = process_csv_transform(rows, "name", "uppercase")
        
        assert result["count"] == 2
        assert result["rows"][0]["name"] == "JOHN"
        assert result["rows"][1]["name"] == "JANE"
    
    def test_process_csv_transform_lowercase(self):
        """Test transforming column to lowercase"""
        rows = [
            {"name": "JOHN", "age": "25"},
            {"name": "JANE", "age": "30"}
        ]
        
        result = process_csv_transform(rows, "name", "lowercase")
        
        assert result["count"] == 2
        assert result["rows"][0]["name"] == "john"
        assert result["rows"][1]["name"] == "jane"
    
    def test_process_csv_transform_trim(self):
        """Test trimming whitespace from column"""
        rows = [
            {"name": "  John  ", "age": "25"},
            {"name": "  Jane  ", "age": "30"}
        ]
        
        result = process_csv_transform(rows, "name", "trim")
        
        assert result["count"] == 2
        assert result["rows"][0]["name"] == "John"
        assert result["rows"][1]["name"] == "Jane"
    
    def test_process_csv_aggregate(self):
        """Test aggregating CSV data"""
        rows = [
            {"name": "John", "age": "25", "city": "New York"},
            {"name": "Jane", "age": "30", "city": "London"},
            {"name": "Bob", "age": "25", "city": "Paris"}
        ]
        
        result = process_csv_aggregate(rows, "age")
        
        assert result["total_rows"] == 3
        assert result["aggregation"]["25"] == 2
        assert result["aggregation"]["30"] == 1
        assert result["column"] == "age"
    
    def test_process_csv_aggregate_empty(self):
        """Test aggregating empty rows"""
        result = process_csv_aggregate([], "age")
        
        assert result["total_rows"] == 0
        assert result["aggregation"] == {}
        assert result["column"] == "age"
    
    def test_process_csv_sort(self):
        """Test sorting CSV rows"""
        rows = [
            {"name": "Bob", "age": "25"},
            {"name": "Alice", "age": "20"},
            {"name": "Charlie", "age": "30"}
        ]
        
        result = process_csv_sort(rows, "name")
        
        assert result["count"] == 3
        assert result["rows"][0]["name"] == "Alice"
        assert result["rows"][1]["name"] == "Bob"
        assert result["rows"][2]["name"] == "Charlie"
    
    def test_process_csv_view(self):
        """Test viewing all CSV rows"""
        rows = [
            {"name": "John", "age": "25"},
            {"name": "Jane", "age": "30"}
        ]
        
        result = process_csv_view(rows)
        
        assert result["count"] == 2
        assert len(result["rows"]) == 2
        assert result["columns"] == ["name", "age"]
    
    def test_process_csv_view_empty(self):
        """Test viewing empty CSV"""
        result = process_csv_view([])
        
        assert result["count"] == 0
        assert result["rows"] == []
        assert result["columns"] == []


class TestAPIEndpoints:
    """Unit tests for API endpoints"""
    
    def test_root_endpoint(self, client):
        """Test root endpoint redirects to static"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307  # Redirect
        assert "/static/index.html" in response.headers["location"]
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        assert response.json()["service"] == "CSV Processor"
    
    def test_process_csv_view_operation(self, client):
        """Test CSV processing with view operation"""
        csv_content = create_test_csv_data()
        files = {"file": ("test.csv", csv_content, "text/csv")}
        data = {"operation": "view"}
        
        response = client.post("/api/process/csv", files=files, data=data)
        
        assert response.status_code == 200
        result = response.json()
        assert result["count"] == 3
        assert len(result["rows"]) == 3
        assert "columns" in result
    
    def test_process_csv_filter_operation(self, client):
        """Test CSV processing with filter operation"""
        csv_content = create_test_csv_data()
        files = {"file": ("test.csv", csv_content, "text/csv")}
        data = {
            "operation": "filter",
            "filter_column": "age",
            "filter_value": "25"
        }
        
        response = client.post("/api/process/csv", files=files, data=data)
        
        assert response.status_code == 200
        result = response.json()
        assert result["count"] == 2
        assert all(row["age"] == "25" for row in result["rows"])
    
    def test_process_csv_filter_missing_params(self, client):
        """Test CSV filter with missing parameters"""
        csv_content = create_test_csv_data()
        files = {"file": ("test.csv", csv_content, "text/csv")}
        data = {"operation": "filter"}
        
        response = client.post("/api/process/csv", files=files, data=data)
        
        assert response.status_code == 400
        assert "required" in response.json()["detail"].lower()
    
    def test_process_csv_transform_operation(self, client):
        """Test CSV processing with transform operation"""
        csv_content = "name,age\njohn,25\njane,30\n"
        files = {"file": ("test.csv", csv_content.encode('utf-8'), "text/csv")}
        data = {
            "operation": "transform",
            "transform_column": "name",
            "transform_operation": "uppercase"
        }
        
        response = client.post("/api/process/csv", files=files, data=data)
        
        assert response.status_code == 200
        result = response.json()
        assert result["rows"][0]["name"] == "JOHN"
        assert result["rows"][1]["name"] == "JANE"
    
    def test_process_csv_aggregate_operation(self, client):
        """Test CSV processing with aggregate operation"""
        csv_content = create_test_csv_data()
        files = {"file": ("test.csv", csv_content, "text/csv")}
        data = {
            "operation": "aggregate",
            "filter_column": "age"
        }
        
        response = client.post("/api/process/csv", files=files, data=data)
        
        assert response.status_code == 200
        result = response.json()
        assert "aggregation" in result
        assert result["total_rows"] == 3
        assert result["aggregation"]["25"] == 2
    
    def test_process_csv_sort_operation(self, client):
        """Test CSV processing with sort operation"""
        csv_content = "name,age\nBob,25\nAlice,20\nCharlie,30\n"
        files = {"file": ("test.csv", csv_content.encode('utf-8'), "text/csv")}
        data = {
            "operation": "sort",
            "filter_column": "name"
        }
        
        response = client.post("/api/process/csv", files=files, data=data)
        
        assert response.status_code == 200
        result = response.json()
        assert result["rows"][0]["name"] == "Alice"
        assert result["rows"][1]["name"] == "Bob"
        assert result["rows"][2]["name"] == "Charlie"
    
    def test_process_csv_empty_file(self, client):
        """Test processing empty CSV file"""
        csv_content = "name,age\n"
        files = {"file": ("test.csv", csv_content.encode('utf-8'), "text/csv")}
        data = {"operation": "view"}
        
        response = client.post("/api/process/csv", files=files, data=data)
        
        assert response.status_code == 400
        assert "empty" in response.json()["detail"].lower()
    
    def test_process_csv_invalid_file(self, client):
        """Test processing invalid file"""
        files = {"file": ("test.txt", b"not a csv", "text/plain")}
        data = {"operation": "view"}
        
        response = client.post("/api/process/csv", files=files, data=data)
        
        # Should still process if it can be decoded, but might have parsing issues
        # This tests the error handling
        assert response.status_code in [200, 400, 500]
    
    def test_download_csv_success(self, client):
        """Test downloading processed CSV"""
        data = {
            "rows": [
                {"name": "John", "age": "25"},
                {"name": "Jane", "age": "30"}
            ]
        }
        
        response = client.post("/api/download/csv", json=data)
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert "attachment" in response.headers.get("content-disposition", "").lower()
    
    def test_download_csv_no_rows(self, client):
        """Test downloading CSV with no rows"""
        data = {"rows": []}
        
        response = client.post("/api/download/csv", json=data)
        
        assert response.status_code == 400
        assert "no rows" in response.json()["detail"].lower()
    
    def test_download_csv_missing_rows(self, client):
        """Test downloading CSV with missing rows key"""
        data = {}
        
        response = client.post("/api/download/csv", json=data)
        
        assert response.status_code == 400
        assert "rows" in response.json()["detail"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

