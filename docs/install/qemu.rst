.. _QEMU:

QEMU
####

This document describes how to build and run for QEMU target.

Building
********

.. code-block:: bash

    $ cd
    $ git clone https://gitlab.com/Linaro/ewaol/meta-ewaol-machine.git
    $ cd meta-ewaol-machine
    $ ./build.sh ledge-secure-qemuarm64 baremetal

    $ cd
    $ git clone https://gitlab.com/Linaro/trustedsubstrate/meta-ts.git
    $ cd meta-ts
    $ kas build ci/qemuarm64-secureboot.yml

Run
***

.. code-block:: bash

    $ cd ~/meta-ts/build/tmp/deploy/images/tsqemuarm64-secureboot
    # Start QEMU. 'Ctrl-A x' to quit (or kill the qemu-system-aarch64 process)
    $ qemu-system-aarch64 -m 2048 -smp 4 -nographic -cpu cortex-a57 \
      -bios flash.bin -machine virt,secure=on \
      -drive id=os,if=none,file=$HOME/meta-ewaol-machine/build/ledge-secure-qemuarm64/tmp_baremetal/deploy/images/ledge-secure-qemuarm64/ewaol-baremetal-image-ledge-secure-qemuarm64.wic \
      -device virtio-blk-device,drive=os

    # On first boot, enter the following command at the U-Boot prompt (=>)
    => efidebug boot add -b 1 BootLedge virtio 0:1 efi/boot/bootaa64.efi -i virtio 0:1 ledge-initramfs.rootfs.cpio.gz -s 'console=ttyAMA0,115200 console=tty0 root=UUID=6091b3a4-ce08-3020-93a6-f755a22ef03b rootwait panic=60' ; efidebug boot order 1 ; bootefi bootmgr

    ledge-secure-qemuarm64 login: ewaol
    ewaol@ledge-secure-qemuarm64:~$

FAQ
***

..
  [NEEDS_TO_BE_FIXED] - Empty section, see Rockpi4 as an example

TBD
