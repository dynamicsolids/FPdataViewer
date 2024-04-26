import subprocess
import pytest

def test_fpdataviewer_inspect_DIAMOND():
    # Execute the command and capture the output
    result = subprocess.run(["fpdataviewer", "inspect", "-i", "ML_AB_DIAMOND"], capture_output=True, text=True)
    actual_output = result.stdout.splitlines()  # Split the output into lines

    # Define the expected output
    expected_output = [
        "file contains 1 group of structures",
        "",
        "[1/1] name       : cubic",
        "[1/1] atoms      : 128",
        "[1/1] atom types : C (128)",
        "[1/1] structures : 618 / 618"
    ]

    # Compare each line in the expected output with the corresponding line in the actual output
    for expected_line, actual_line in zip(expected_output, actual_output):
        print ("expected line::", expected_line)
        print ("actual line  ::", actual_line)
        assert expected_line.strip() == actual_line.strip(), f"Expected: {expected_line}, Actual: {actual_line}"


def test_fpdataviewer_inspect_BiO():
    # Execute the command and capture the output
    result = subprocess.run(["fpdataviewer", "inspect", "-i", "ML_AB_BiO"], capture_output=True, text=True)
    actual_output = result.stdout.splitlines()  # Split the output into lines

    # Define the expected output
    expected_output = [
        "file contains 1 group of structures",
        "",
        "[1/1] name       : Bi2",
        "[1/1] atoms      : 160",
        "[1/1] atom types : Bi (64), O (96)",
        "[1/1] structures : 957 / 957"
    ]

    # Compare each line in the expected output with the corresponding line in the actual output
    for expected_line, actual_line in zip(expected_output, actual_output):
        print ("expected line::", expected_line)
        print ("actual line  ::", actual_line)
        assert expected_line.strip() == actual_line.strip(), f"Expected: {expected_line}, Actual: {actual_line}"


def test_fpdataviewer_inspect_BiO_small():
    # Execute the command and capture the output
    result = subprocess.run(["fpdataviewer", "inspect", "-i", "ML_AB_BiO_small"], capture_output=True, text=True)
    actual_output = result.stdout.splitlines()  # Split the output into lines

    # Define the expected output
    expected_output = [
        "file contains 1 group of structures",
        "",
        "[1/1] name       : Bi2",
        "[1/1] atoms      : 160",
        "[1/1] atom types : Bi (64), O (96)",
        "[1/1] structures : 15 / 15"
    ]

    # Compare each line in the expected output with the corresponding line in the actual output
    for expected_line, actual_line in zip(expected_output, actual_output):
        print ("expected line::", expected_line)
        print ("actual line  ::", actual_line)
        assert expected_line.strip() == actual_line.strip(), f"Expected: {expected_line}, Actual: {actual_line}"


def test_fpdataviewer_inspect_BN():
    # Execute the command and capture the output
    result = subprocess.run(["fpdataviewer", "inspect", "-i", "ML_AB_BN"], capture_output=True, text=True)
    actual_output = result.stdout.splitlines()  # Split the output into lines

    # Define the expected output
    expected_output = [
        "file contains 1 group of structures",
        "",
        "[1/1] name       : hBN",
        "[1/1] atoms      : 128",
        "[1/1] atom types : N (64), B (64)",
        "[1/1] structures : 1197 / 1197"
    ]

    # Compare each line in the expected output with the corresponding line in the actual output
    for expected_line, actual_line in zip(expected_output, actual_output):
        print ("expected line::", expected_line)
        print ("actual line  ::", actual_line)
        assert expected_line.strip() == actual_line.strip(), f"Expected: {expected_line}, Actual: {actual_line}"


def test_fpdataviewer_inspect_MAPbBr3():
    # Execute the command and capture the output
    result = subprocess.run(["fpdataviewer", "inspect", "-i", "ML_ABCAR-MAPbBr3"], capture_output=True, text=True)
    actual_output = result.stdout.splitlines()  # Split the output into lines

    # Define the expected output
    expected_output = [
        "file contains 1 group of structures",
        "",
        "[1/1] name       : Cubic-(SSHS-MAPbBr3)",
        "[1/1] atoms      : 96",
        "[1/1] atom types : Pb (8), Br (24), C (8), N (8), H (48)",
        "[1/1] structures : 853 / 853"
    ]

    # Compare each line in the expected output with the corresponding line in the actual output
    for expected_line, actual_line in zip(expected_output, actual_output):
        print ("expected line::", expected_line)
        print ("actual line  ::", actual_line)
        assert expected_line.strip() == actual_line.strip(), f"Expected: {expected_line}, Actual: {actual_line}"



def test_fpdataviewer_inspect_MAPbI15Br15():
    # Execute the command and capture the output
    result = subprocess.run(["fpdataviewer", "inspect", "-i", "ML_ABCAR-MAPbI1.5Br1.5"], capture_output=True, text=True)
    actual_output = result.stdout.splitlines()  # Split the output into lines

    # Define the expected output
    expected_output = [
        "file contains 2 groups of structures",
        "",
        "[1/2] name       : Cubic-(SSHS-MAPbIBr-4-4)",
        "[1/2] atoms      : 96",
        "[1/2] atom types : Pb (8), I (12), Br (12), C (8), N (8), H (48)",
        "[1/2] structures : 2723 / 3267",
        "",
        "[2/2] name       : MAPbBr3",
        "[2/2] atoms      : 96",
        "[2/2] atom types : Pb (8), I (12), Br (12), C (8), N (8), H (48)",
        "[2/2] structures : 544 / 3267"
    ]

    # Compare each line in the expected output with the corresponding line in the actual output
    for expected_line, actual_line in zip(expected_output, actual_output):
        print ("expected line::", expected_line)
        print ("actual line  ::", actual_line)
        assert expected_line.strip() == actual_line.strip(), f"Expected: {expected_line}, Actual: {actual_line}"


def test_fpdataviewer_inspect_MAPbI3():
    # Execute the command and capture the output
    result = subprocess.run(["fpdataviewer", "inspect", "-i", "ML_ABCAR-MAPbI3"], capture_output=True, text=True)
    actual_output = result.stdout.splitlines()  # Split the output into lines

    # Define the expected output
    expected_output = [
        "file contains 1 group of structures",
        "",
        "[1/1] name       : Cubic-(SSHS-MAPbI3)",
        "[1/1] atoms      : 96",
        "[1/1] atom types : Pb (8), I (24), C (8), N (8), H (48)",
        "[1/1] structures : 777 / 777"
    ]

    # Compare each line in the expected output with the corresponding line in the actual output
    for expected_line, actual_line in zip(expected_output, actual_output):
        print ("expected line::", expected_line)
        print ("actual line  ::", actual_line)
        assert expected_line.strip() == actual_line.strip(), f"Expected: {expected_line}, Actual: {actual_line}"



def test_fpdataviewer_inspect_GRAPHENE():
    # Execute the command and capture the output
    result = subprocess.run(["fpdataviewer", "inspect", "-i", "ML_AB_GRAPHENE"], capture_output=True, text=True)
    actual_output = result.stdout.splitlines()  # Split the output into lines

    # Define the expected output
    expected_output = [
        "file contains 1 group of structures",
        "",
        "[1/1] name       : C4",
        "[1/1] atoms      : 72",
        "[1/1] atom types : C (72)",
        "[1/1] structures : 281 / 281"
    ]

    # Compare each line in the expected output with the corresponding line in the actual output
    for expected_line, actual_line in zip(expected_output, actual_output):
        print ("expected line::", expected_line)
        print ("actual line  ::", actual_line)
        assert expected_line.strip() == actual_line.strip(), f"Expected: {expected_line}, Actual: {actual_line}"


def test_fpdataviewer_inspect_KAgSe():
    # Execute the command and capture the output
    result = subprocess.run(["fpdataviewer", "inspect", "-i", "ML_AB_KAgSe"], capture_output=True, text=True)
    actual_output = result.stdout.splitlines()  # Split the output into lines

    # Define the expected output
    expected_output = [
        "file contains 1 group of structures",
        "",
        "[1/1] name       : New",
        "[1/1] atoms      : 144",
        "[1/1] atom types : K (24), Ag (72), Se (48)",
        "[1/1] structures : 549 / 549"
    ]

    # Compare each line in the expected output with the corresponding line in the actual output
    for expected_line, actual_line in zip(expected_output, actual_output):
        print ("expected line::", expected_line)
        print ("actual line  ::", actual_line)
        assert expected_line.strip() == actual_line.strip(), f"Expected: {expected_line}, Actual: {actual_line}"


def test_fpdataviewer_inspect_LiN3():
    # Execute the command and capture the output
    result = subprocess.run(["fpdataviewer", "inspect", "-i", "ML_AB_Li3N"], capture_output=True, text=True)
    actual_output = result.stdout.splitlines()  # Split the output into lines

    # Define the expected output
    expected_output = [
        "file contains 1 group of structures",
        "",
        "[1/1] name       : alpha-LiN3",
        "[1/1] atoms      : 108",
        "[1/1] atom types : Li (81), N (27)",
        "[1/1] structures : 654 / 654"
    ]

    # Compare each line in the expected output with the corresponding line in the actual output
    for expected_line, actual_line in zip(expected_output, actual_output):
        print ("expected line::", expected_line)
        print ("actual line  ::", actual_line)
        assert expected_line.strip() == actual_line.strip(), f"Expected: {expected_line}, Actual: {actual_line}"


# Use pytest to run the test
if __name__ == "__main__":
    pytest.main()
