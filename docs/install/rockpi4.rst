.. _RockPi4:

RockPi4
#######

LEDGE Reference Platform (ledge-os-manifest) is a Linux distro based on
Yocto/OpenEmbedded. It also uses firmware from Linaro :ref:`Trusted Substrate`
(meta-ts). This document describes how to build and run for target RockPi4.

Building
********

Build meta-ts
=============
.. code-block:: bash

	$ pip install kas
	$ git clone https://git.codelinaro.org/linaro/dependable-boot/meta-ts.git
	$ cd meta-ts
	$ kas build ci/rockpi4b.yml

Build ledge-oe or download prebuilt rootfs image
================================================
.. code-block:: bash

	$ mkdir ledge-oe
	$ cd ledge-oe
	$ repo init -u https://github.com/Linaro/ledge-oe-manifest.git
	$ repo sync -j20
	$ MACHINE=ledge-multi-armv8 DISTRO=rpb source ./setup-environment build-rpb-mc
	# (changes dir to build-rpb-mc automatically)
	# Note: the rootfs is common with other arm64 targets, so the same .wic image can be used
	# e.g. on RockPi4 too (name is legacy)
	$ bitbake mc:qemuarm64:ledge-gateway

Run
***
How to prepare the images to run on the RockPi 4 board is explained here, copied/annotated below:

“Firmware boots from an SD card. While rootfs and ESP partition are on a USB stick.

Prepare SD with
===============

..
	[NEEDS_TO_BE_FIXED] - Currently describeds Jeromes way of setting this up

.. code-block:: bash

	$ scp jerome.forissier@hackbox2.linaro.org:meta-ts/build/tmp/deploy/images/rockpi4b/ts-firmware-rockpi4b.wic.gz .
	zcat ts-firmware-rockpi4b.wic.gz >/dev/sdX
	# (on my laptop it’s >/dev/mmcblk0)

.. warning::

	Make sure the device in ``/dev`` is present before doing this or you will
	create a file in ``/dev`` and put nothing on the SD card, and the card will
	not be seen until you delete the file!

Prepare USB stick with
======================

..
	[NEEDS_TO_BE_FIXED] - Currently describeds Jeromes way of setting this up and mentions LEDGE RP

You can use LEDGE RP for example:

.. code-block:: bash

	$ wget https://snapshots.linaro.org/components/ledge/oe/ledge-multi-armv8/1322/rpb/ledge-qemuarm64/ledge-gateway-lava-ledge-qemuarm64-20220413003518.rootfs.wic.gz .

Or custom built:

..
	[NEEDS_TO_BE_FIXED] - Currently describeds Jeromes way of setting this up

.. code-block:: bash

	$ scp jerome.forissier@hackbox2.linaro.org:ledge-oe/build-rpb-mc/arm64-glibc/deploy/images/ledge-qemuarm64/ledge-gateway-ledge-qemuarm64.wic.gz .
	$ zcat <rootfs>.wic.gz > /dev/sdY

.. note::

	The ``qemuarm64`` above not a typo, the rootfs is multi-platform. If you
	used USB stick in other machine with current firmware before booting delete
	``ubootefi.var`` file for ESP (first one) partition.

Attach USB stick and SD card
============================

Plug both USB stick and SD card into the board. The USB stick has to be in one
of the black USB ports (at least for me it wouldn’t be detected by U-Boot when
in one of the blue USB3 ports; I’m using a CF card in a USB adapter). Power it
on and wait for the U-boot prompt.

Add kernel board specific kernel parameters and EFI boot order
==============================================================

.. code-block:: bash

	$ efidebug boot add -b 1 BootLedge usb 0:1 efi/boot/bootaa64.efi -i usb 0:1 ledge-initramfs.rootfs.cpio.gz -s 'console=ttyS2,1500000 console=tty0 root=UUID=6091b3a4-ce08-3020-93a6-f755a22ef03b rootwait panic=60' ; efidebug boot order 1


Restart
=======

Power cycle board it and it has to boot automatically now.

.. note::
	First boot with a fresh root fs is slow, please wait for a couple of minutes
	(really) when no output is shown:

Serial port info: https://wiki.radxa.com/Rockpi4/dev/serial-console. We've been
using this script:

.. code-block:: bash

	#!/bin/bash
	#
	# miniterm.py is in Ubuntu package python-serial
	# $ sudo apt-get install python-serial
	#
	# Adjust USB device as needed

	DEV=${1:-/dev/ttyUSB0}
	pyserial-miniterm --raw --eol CR ${DEV} 1500000


FAQ
***

Q: How to increase OP-TEE core log level?
=========================================
Add ``CFG_TEE_CORE_LOG_LEVEL=3`` to ``EXTRA_OEMAKE`` in
``meta-ts/meta-arm/recipes-security/optee/optee-os.inc`` and rebuild (kas
build…)

Q: How to modify optee-os sources locally and rebuild?
======================================================

	#. Remove line ``INHERIT += rm_work`` in ``ci/base.yml``
	#. Run ``$ kas shell ci/rockpi4b.yml``
		#. ``bitbake -c cleansstate optee-os`` # WARNING removes source in work directory
		#. ``$ bitbake optee-os``
		#. Edit source files in ``build/tmp/work/rockpi4b-poky-linux/optee-os/<ver>/git``
		   ``$ bitbake -c compile -f optee-os`` # mandatory before kas build below it seems
	#. Exit kas shell and run ``$ kas build ci/rockpi4b.yml``

Q: Why is the internal eMMC not detected?
=========================================
Try a different USB-C power supply. We use a Dell one. I have another no-name PS
supposedly rated PD 100W which doesn’t work reliably.

Q: How to skip initramfs and boot to rootfs directly?
=====================================================

.. code-block:: bash

	$ efidebug boot add -b 1 BootLedge usb 0:1 efi/boot/bootaa64.efi -s 'console=ttyS2,1500000 console=tty0 root=UUID=6091b3a4-ce08-3020-93a6-f755a22ef03b rootwait panic=60 root=/dev/sda2' ; efidebug boot order 1 ; bootefi bootmgr

Q: On boot, the kernel logs warnings about GPT, how to fix them?
================================================================
They are harmless, they are caused by the fact that the actual device (USB key)
is larger than the image copied to it. The warnings can be removed by running
``gparted /dev/sdaX`` and accepting the prompt to fix the GPT info.

Q: On boot, the kernel logs “EXT4 … recovery complete”, what’s wrong?
=====================================================================
Usually harmless. The board was not powered off or rebooted cleanly. Use
``systemctl halt`` or ``systemctl reboot``.

Q: symbolize.py on hb2 (on e.g., the fTPM TA) prints DWARF warnings and no source file/line info. Why?
======================================================================================================
The default toolchains (``aarch64-linux-gnu-*``) is too old (7.2). Put a more
recent one in your ``PATH`` before invoking ``symbolize.py`` (Note: some source/file
line info are still missing, could be due to build flags)

Q: How can I modify, rebuild and test the kernel?
=================================================
Edit source in

.. code-block:: bash

	build-rpb-mc/arm64-glibc/work/ledge_qemuarm64-linaro-linux/linux-ledge/mainline-5.15-r4.ledge/linux-5.15.34/

and then build with:

.. code-block:: bash

	$ MACHINE=ledge-multi-armv8 DISTRO=rpb source ./setup-environment build-rpb-mc
	$ bitbake -f -c compile mc:qemuarm64:linux-ledge

Then transfer the file

.. code-block:: bash

	build-rpb-mc/arm64-glibc/work/ledge_qemuarm64-linaro-linux/linux-ledge/mainline-5.15-r4.ledge/build/arch/arm64/boot/Image

to the USB stick partition 1 with name: ``EFI/BOOT/bootaa64.efi``.

Q: How can I modify and regenerate the initramfs?
=================================================

.. code-block:: bash

	bitbake mc:qemuarm64:ledge-initramfs

then copy ``ledge-initramfs.rootfs.cpio.gz`` to partition 1 of the USB stick


