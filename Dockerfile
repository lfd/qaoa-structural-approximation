FROM python:3.11

ENV USER=user

RUN groupadd -r ${USER} && useradd -m -r -g ${USER} ${USER}

COPY lib /tmp/lib
COPY requirements.txt /tmp/requirements.txt
COPY install.R /tmp/install.R

RUN pip install /tmp/lib/pyalma && \
    pip install -r /tmp/requirements.txt


RUN apt-get update && \
    apt-get install -y texlive-full

RUN apt-get install -y r-base r-base-dev && \
    Rscript /tmp/install.R


USER ${USER}
ENV HOME=/home/${USER}

WORKDIR /home/${USER}

COPY --chown=${USER} experiments experiments
COPY --chown=${USER} paper paper
COPY --chown=${USER} run.sh run.sh

RUN mkdir experiments/out && \
    mkdir experiments/out/uniform && \
    mkdir experiments/out/uniform_preopt && \
    mkdir experiments/out/clustered && \
    mkdir experiments/out/clustered_preopt && \
    mkdir experiments/out/sat && \
    mkdir experiments/out/sat_preopt && \
    mkdir experiments/out/qrfactoring_approx && \
    mkdir experiments/out/qrf_preopt && \
    #
    cd paper && \
    bash link_data.sh ${HOME}/experiments && \
    cd ${HOME}
    
ENTRYPOINT bash run.sh

