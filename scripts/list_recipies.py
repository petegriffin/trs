#!/usr/bin/env python

from argparse import ArgumentParser
import os


def get_parser():
    """ Takes care of script argument parsing. """
    parser = ArgumentParser(description='Script used to find the location of '
                                        'recipes in Yocto builds')

    parser.add_argument('-d', '--dump', required=False, action="store_true",
                        help='Dump contents of the found recipe(s)')

    parser.add_argument('-p', '--package', required=False, action="store",
                        help='Query for a single package')

    parser.add_argument('-f', '--file', required=False, action="store",
                        default="task-depends.dot",
                        help='File generated by bitbake -g <image-name>')

    return parser


def dump_recipe_content(recipe):
    with open(recipe, encoding='utf-8') as f:
        data = f.readlines()
        print("-" * 80)
        for line in data:
            line.strip()
            print("    {}".format(line))
        print("-" * 80)


def parse_dependencies(filename, search=None, dump=None):
    tasks = None
    with open(filename, encoding='utf-8') as f:
        tasks = f.readlines()

    print("{}{}".format("Package".ljust(40), "recipe"))
    print("{}{}".format("=======".ljust(40), "======="))
    for task in tasks:
        task = task.strip()
        if "do_compile" in task and "label" in task:
            data = task.split()

            package = data[0].replace('\"', '')
            package = package.replace('.do_compile', '')

            recipe = data[2].split(':')[-1]
            recipe = recipe.split('\\n')[-1]
            recipe = recipe.replace('"]', '')
            tmp = recipe.split('/')
            count = 0
            for j in tmp:
                if j == "..":
                    break
                count += 1
            del tmp[count-1:count+1]
            recipe = '/'.join(tmp)
            if search is None:
                print("{}{}".format(package.ljust(40), recipe))
            elif search in package:
                print("{}{}".format(package.ljust(40), recipe))
                if dump:
                    dump_recipe_content(recipe)


def main():
    args = get_parser().parse_args()
    parse_dependencies(args.file, args.package, args.dump)


if __name__ == '__main__':
    main()
