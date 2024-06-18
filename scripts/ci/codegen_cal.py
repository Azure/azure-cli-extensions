#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
import os
import re
import argparse
from util import get_repo_root

output_file = os.environ.get('output_file', None)
result_path = os.environ.get('result_path', None)

cli_ext_path = get_repo_root()
cli_ext_src_path = os.path.join(cli_ext_path, "src")
print("cli_ext_path: ", cli_ext_path)
print("cli_ext_src_path: ", cli_ext_src_path)

DEFAULT_SURVEY_MESSAGE = "Thank you for using our CodeGen tool. We value your feedback, and we would like to know how we can improve our product. Please take a few minutes to fill our [codegen survey](https://forms.office.com/r/j6rQuFUqUf?origin=lprLink) "

def check_is_module_aaz_related(mod):
    codegen_aaz_folder_pattern = re.compile(r"src/%s/azext_.*?/aaz/" % mod)
    module_path = os.path.join(cli_ext_src_path, mod)
    print("module_path: ", module_path)
    for root, subdir, files in os.walk(module_path):
        codegen_aaz_match = re.findall(codegen_aaz_folder_pattern, root)
        if codegen_aaz_match:
            print(codegen_aaz_match)
            return True
    return False 
    
def save_comment_pr_survey(comment_pr_survey):
    print("check comment_pr_survey: ", comment_pr_survey)
    with open(os.path.join(cli_ext_path, result_path, output_file), "w") as f:
        f.write(str(comment_pr_survey) + "\n")

def check_aaz_module():
    comment_pr_survey = 0
    changed_module_list = os.environ.get('changed_module_list', "").split()
    for mod in changed_module_list:
        if check_is_module_aaz_related(mod):
            comment_pr_survey = 1
            break
    save_comment_pr_survey(comment_pr_survey)
    if comment_pr_survey == 1:
        comment_message = []
        add_survey_hint_message(comment_message)
        save_comment_message(comment_message)

def add_survey_hint_message(comment_message):
    comment_message.append("## CodeGen Tools Feedback Collection")
    comment_message.append(DEFAULT_SURVEY_MESSAGE)

def save_comment_message(comment_message):
    print("comment_message:")
    print(comment_message)
    survey_comment_file = os.environ.get('survey_comment_file', "")
    with open(os.path.join(cli_ext_path, result_path, survey_comment_file), "w") as f:
        for line in comment_message:
            f.write(line + "\n")

def save_gh_output():
    with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
        print(f'CommentAAZSurvey={comment_pr_survey}', file=fh)

def set_aaz_comment():
    if not os.path.exists(os.path.join(cli_ext_path, result_path, output_file)):
        print("error in file dowdload")
        return
    comment_pr_survey = 0
    with open(os.path.join(cli_ext_path, result_path, output_file), "r") as f:
        for line in f:
            comment_pr_survey = int(line.strip())
    print("comment_pr_survey: ", comment_pr_survey)
    save_gh_output()
    if comment_pr_survey:
        comment_message = []
        add_survey_hint_message(comment_message)
        save_comment_message(comment_message)

def main(job):
    if job == "check":
        check_aaz_module()
    elif job == "set":
        set_aaz_comment()
    else:
        print("unsupported job type")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--job", choices=["check", "set"], required=True, help="job type")
    args = parser.parse_args()
    print(vars(args))
    main(args.job)