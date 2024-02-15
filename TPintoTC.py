import argparse
from ast import List
from dataclasses import dataclass
import logging
import os
import pathlib
import re
import sys


project_directory: pathlib.Path
suite_name_pattern: str = ""
new_folder: str = ""
existing_folder: str = ""
location_folder: str = ""
folder: str = "../verification/documentation/x-pas_test_plans/test_plans"
test_plan_file: str
robot_file: str
logger = logging.getLogger("TPintoTC")


class TPParserError(Exception):
    """
    Custom exception for TP tool.
    """


def get_test_plan_file(file_name_pattern: str) -> str:
    """get TC from the Test plan"""
    # folder = "../verification/documentation/x-pas_test_plans/test_plans"

    test_plan_files = [
        f for f in os.listdir(folder) if file_name_pattern in f and "TestPlan" in f
    ]
    if test_plan_files:
        test_plan_file = test_plan_files[0]
    else:
        raise TPParserError(f"No TestPlan file including {file_name_pattern} found.")

    logger.warning(f"File found : {test_plan_file}")
    rep = input("Is this the correct file ? [y/n]   ")
    if rep == "n":
        new_file = input("Enter a new file pattern : ")
        test_plan_file = get_test_case_from_test_plan(new_file)

    return test_plan_file


def get_test_case_from_test_plan(test_plan_file: str):
    """"""

    with open(f"{folder}/{test_plan_file}", "r") as file:
        adoc_content = file.read()
    pattern = r"\| (.+)"
    param_test_case: List[dict[str, str]] = []
    matches = re.findall(pattern, adoc_content)
    column_titles = matches[0].split(".1+^.^|")
    nb_column = matches[0].count("^.^") + 1
    rows = [match for match in matches if "Test title" not in match]
    test_cases = [rows[i : i + nb_column] for i in range(0, len(rows), nb_column)]
    print(test_cases[0])
    # sys.exit(1)
    dict_tc = {}
    for tc in test_cases:
        for index in range(nb_column):
            if "Req" in column_titles[index]:
                dict_tc[column_titles[index].strip()] = re.findall(
                    r"\[(.*)\]", tc[index]
                )[0]
            else:
                dict_tc[column_titles[index].strip()] = tc[index]
        cp = dict_tc.copy()
        param_test_case.append(cp)
    print(param_test_case)

    return param_test_case


def create_robot_file(test_plan_file: str, folder_path: str, test_cases):
    """Get Test plan name and create robot file matching this name"""
    regex = r"TestPlan_(?:Arctic_)*(.*).adoc"
    test_plan_file = re.findall(regex, test_plan_file)[0]
    test_plan_file = test_plan_file.replace("_", "")
    robot_file = re.findall("[A-Z][^A-Z]*", test_plan_file)
    robot_file = [w.lower() for w in robot_file]
    print(folder_path)
    if not (os.path.exists(folder_path)):
        os.mkdir(folder_path)
    nb_file = len(os.listdir(folder_path)) + 1
    robot_file_name = f"{nb_file:02}__{'_'.join(robot_file)}_tests2.robot"
    print(robot_file_name)
    with open(f"{folder_path}/{robot_file_name}", "w") as fichier:
        fichier.write("*** Test Cases ***\n")
        for tc in test_cases:
            fichier.write(f"{tc['Test title']}\n")
            fichier.write(f"\t[Documentation]    EM12-SEVC-\n")
            fichier.write(f"\t...    Requirement {tc['Req']}\n")
            fichier.write(f"\t...\n")
            fichier.write(f"\t...    {tc['Comment']}\n")
            fichier.write(f"\t[Tags]    {tc['Test type'].replace(', ','   ')}\n")
            fichier.write(f"\tNo Operation\n\n")

    # print(robot_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "--verification-path",
        dest="verification_path",
        default="../verification/",
        help="Path of the verification folder",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        dest="verbose_mode",
        required=False,
        help="Will print more info",
    )
    parser.add_argument(
        "-f",
        "--filename",
        dest="file_name_pattern",
        required=True,
        type=str,
        help="file name or sub-part name of the Test Plan file",
    )
    parser.add_argument(
        "-d",
        "--folder",
        dest="folder",
        help="name of the folder where the robot file will be created. Type None if you do not want "
        "to create a folder",
        required=False,
        default="None",
    )

    args = parser.parse_args()

    test_plan_file = get_test_plan_file(args.file_name_pattern)
    logger.warning(f"File chosen : {test_plan_file}")
    test_cases = get_test_case_from_test_plan(test_plan_file)
    folder_path = f"{args.verification_path}BPas_verification/{args.folder}"
    create_robot_file(
        test_plan_file=test_plan_file, folder_path=folder_path, test_cases=test_cases
    )
