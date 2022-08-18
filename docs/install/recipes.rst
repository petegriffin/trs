.. _recipes:

Recipes
#######
TRS levarage various layers and recipes to build firmware, root filesystem and
various images. These can be found after doing a build according to the build
instructions in this TRS documentation.

Helper scripts
**************

Recipe finder
=============
The script below comes from ``scripts/list_recipies.py`` in the TRS
documentation. This script will find the packages that are being compiled and
the belong bb-file for it. To run this script you first need to generate the a
file called ``task-depends.dot``. You generate that by doing:

.. code-block:: bash

    $ bitbake -e <image-name>

For Trusted Substrate with QEMU for example this can be achieved by running

.. code-block:: bash

    $ kas shell ci/qemuarm64-secureboot.yml
    $ bitbake -e ts-firmware

Once that has completed you should be able to find ``.../build/task-depends.dot``.
With that available, go the folder where ``list_recipies.py`` is located and run
the script:

.. code-block:: bash

    $ ./list_recipies.py -f <full-path-to>/task-depends.dot

If you're searching for a certain package, you can use the ``-p`` parameter.

.. code-block:: bash

    $ ./list_recipies.py -f <full-path-to>/task-depends.dot -p op-tee

If you also want to see the content of the specified package you can use the
``-d`` parameter.

.. code-block:: bash

    $ ./list_recipies.py -f <full-path-to>/task-depends.dot -p op-tee -d


.. literalinclude:: ../../scripts/list_recipies.py
    :language: python
    :linenos:
