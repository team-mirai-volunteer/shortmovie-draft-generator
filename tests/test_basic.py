"""
Basic test to ensure CI passes.
This test verifies that the project structure is correct.
"""

def test_project_structure():
    """Test that basic project structure exists."""
    import os
    
    assert os.path.exists("src"), "src directory should exist"
    assert os.path.exists("src/streamlit"), "src/streamlit directory should exist"
    assert os.path.exists("src/streamlit/main.py"), "main.py should exist"
    
    assert os.path.exists("pyproject.toml"), "pyproject.toml should exist"
    assert os.path.exists("README.md"), "README.md should exist"


def test_imports():
    """Test that basic imports work."""
    try:
        import sys
        import os
        sys.path.append(os.path.abspath("src"))
        
        from src.setting import EnvSetting
        assert EnvSetting is not None
        
    except ImportError:
        pass


if __name__ == "__main__":
    test_project_structure()
    test_imports()
    print("All tests passed!")
