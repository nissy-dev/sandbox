FROM ubuntu:22.04

# コンテナ内のタイムゾーン
ENV TZ=Asia/Tokyo

RUN apt update && apt install sudo

# 上記のタイムゾーンを設定する
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN sudo apt update
RUN sudo apt install binutils build-essential golang sysstat python3-matplotlib python3-pil fonts-takao fio qemu-kvm virt-manager libvirt-clients virtinst jq docker.io containerd libvirt-daemon-system strace -y
RUN sudo adduser `id -un` libvirt
RUN sudo adduser `id -un` libvirt-qemu
RUN sudo adduser `id -un` kvm
