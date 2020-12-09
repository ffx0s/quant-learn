FROM jcrist/alpine-conda:4.6.8

ENV PATH=/opt/conda/bin:$PATH
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/lib
COPY .condarc /home/anaconda

RUN conda install --yes --freeze-installed \
        numpy \
        pandas \
        apscheduler \
        nomkl \
    && conda clean -afy \
    && find /opt/conda/ -follow -type f -name '*.a' -delete \
    && find /opt/conda/ -follow -type f -name '*.pyc' -delete \
    && find /opt/conda/ -follow -type f -name '*.js.map' -delete

USER root
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories \ 
    && apk add --no-cache g++ gcc make && rm -rf /var/cache/apk/* \
    && wget -c http://static.webfed.cn/ta-lib-0.4.0-src.tar.gz -O - | tar -xz \
    && cd ta-lib && ./configure --prefix=/usr && make && make install && make distclean \
    && pip install --no-cache-dir TA-Lib futu-api -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com \
    && apk del g++ gcc make \
    && ln -s /opt/conda/lib/libstdc++.so.6 /usr/lib/libstdc++.so.6
USER anaconda
