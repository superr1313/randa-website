#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#   User: john
#   Date: 5/26/15
#   Time: 7:12 PM


from pybuilder.core import use_bldsup
from pybuilder.core import init, use_plugin


use_plugin('filter_resources')

use_plugin("python.core")
use_plugin("python.distutils")
use_plugin("python.install_dependencies")

# use_plugin('python.unittest')
use_plugin("python.coverage")
use_plugin("python.pyfix_unittest")
# use_plugin("python.integrationtest")

use_plugin('python.pylint')
use_plugin("python.flake8")
use_plugin("python.snakefood")

use_plugin('pypi:pybuilder_header_plugin')
use_bldsup()
use_plugin('html_cover')

name = 'randa-website'
license = 'Apache License, Version 2.0'
summary = 'randa-website'
version = '2.0.0'

default_task = ['html_cover']


@init
def initialize(project):
    """ Method that runs when executing cli pyb

    """

    project.build_depends_on('coverage')
    project.build_depends_on('darth')
    project.build_depends_on('flake8')
    project.build_depends_on('httmock')
    project.build_depends_on('mockito')
    project.build_depends_on("pyfix")
    project.build_depends_on("pyassert")
    project.build_depends_on('pylint')

    project.depends_on("bleach")
    project.depends_on("decorator")

    project.set_property("verbose", True)
    project.set_property('flake8_break_build', False)
    project.set_property('flake8_include_test_sources', True)
    project.set_property('flake8_include_scripts', True)

    project.set_property('run_unit_tests_propagate_stdout', True)
    project.set_property('run_unit_tests_propagate_stderr', True)
    # project.set_property("run_unit_tests", "py.test %s" % project.expand_path("$dir_source_unittest_python"))
    project.set_property('install_dependencies_upgrade', True)

    project.set_property('coverage_break_build', True)

    project.get_property('filter_resources_glob').append('**/randa_website/__init__.py')

    project.set_property('pybuilder_header_plugin_break_build', True)
    project.set_property('pybuilder_header_plugin_expected_header', "# Copyright\n")

    project.set_property("install_dependencies_local_mapping",
                         {runtime_dependency.name: "libs" for runtime_dependency in project.dependencies})

