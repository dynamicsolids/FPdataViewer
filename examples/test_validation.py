import os
import subprocess
import pytest

def create_test_functions():
    """Dynamically creates test functions for fpdataviewer validation."""
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    data_files = [f for f in files if f.startswith("ML_")]

    for data_file in data_files:
        # Define a unique name for each test function
        test_name = f"{data_file}"

        # Define the test function dynamically
        def test_data(data_file=data_file):
            result = subprocess.run(["fpdataviewer", "validate", "-i", data_file], capture_output=True)
            output = result.stdout.decode("utf-8")
            assert "format ok\nno problems found" in output
            assert result.returncode == 0

        # Set the test function as an attribute of the current module
        setattr(create_test_functions, test_name, test_data)

# Call the function to create test functions dynamically
create_test_functions()

# Ensure that pytest discovers the dynamically created test functions
@pytest.mark.parametrize("data_file", [f for f in os.listdir('.') if f.startswith("ML_")])
def test_fpdataviewer_validation(data_file):
    test_function_name = f"{data_file}"
    assert hasattr(create_test_functions, test_function_name), f"No test function found for {data_file}"
    getattr(create_test_functions, test_function_name)(data_file)

# Use pytest to run the dynamically created test functions
if __name__ == "__main__":
    pytest.main()
