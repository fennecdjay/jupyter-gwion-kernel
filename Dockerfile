FROM jupyter/minimal-notebook
MAINTAINER Jérémie Astor <astor.jeremie@wanadoo.fr>

WORKDIR /tmp

COPY ./ jupyter_gwion_kernel/
RUN pip install --no-cache-dir jupyter_gwion_kernel/
RUN cd jupyter_gwion_kernel && install_gwion_kernel --user

RUN git clone https://github.com/fennecdjay/gwion
WORKDIR /tmp/gwion
RUN git submodule update --init util ast
RUN make

USER root
RUN make install

WORKDIR /home/$NB_USER/
USER $NB_USER
