#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#   User: john
#   Date: 5/29/15
#   Time: 3:32 PM
#


from pybuilder.core import init, task, description, depends
from pybuilder.plugins.python.python_plugin_helper import execute_tool_on_source_files


@init
def initialize(project, logger):
    """

    :type project: pybuilder.core.Project
    :type logger: logging
    :return:
    :rtype:
    """

    pass


@task
@depends('analyze')
@description('Run the python coverage html report')
def html_cover(project, logger):
    """
    Run the python coverage html report
    """

    execute_tool_on_source_files(project=project,
                                 name="html_cover",
                                 command_and_arguments=[
                                     "coverage", 'html',
                                     '-d', 'target/reports/html',
                                 ],
                                 logger=logger)
