FROM tiangolo/uwsgi-nginx-flask:python2.7


#RUN apt update
RUN pip install requests pymongo xlsxwriter numpy pandas scikit-learn matplotlib nltk pillow pytesseract opencv-python requests celery redis -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com
#RUN pip3 install pymongo -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com
#RUN pip3 install xlsxwriter -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com
#RUN pip3 install numpy -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com
#RUN pip3 install pandas -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com
#RUN pip3 install scikit-learn -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com
#RUN pip3 install matplotlib -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com
#RUN pip3 install nltk -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com
#RUN pip3 install pillow -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com
#RUN pip3 install pytesseract -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com
#RUN pip3 install opencv-python -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com
#RUN pip3 install requests -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com
RUN cp /usr/share/zoneinfo/Asia/Shanghai  /etc/localtime
COPY somaxconn /proc/sys/net/core/somaxconn
#RUN echo 500 > /proc/sys/net/core/somaxconn
#COPY sources.list /etc/apt/sources.list

#RUN apt clean && apt update
#RUN apt install -y \
#software-properties-common gnuplot \
#python3-pip \
#wget unzip \
#build-essential \
#cmake git libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev \
#libbson-1.0 \
#libboost-all-dev \
#libjsoncpp-dev \
#ffmpeg \
#htop \
#gdb \
#vim \
#libcurl4-openssl-dev pkg-config libssl-dev python-dev python-numpy libtbb2 libtbb-dev \
#pkg-config zip zlib1g-dev unzip
#
##RUN apt clean
##RUN apt update
#RUN apt install -y htop unzip gnupg
#RUN wget -qO - https://www.mongodb.org/static/pgp/server-4.0.asc | apt-key add - && \
#echo "deb [ arch=amd64 ] https://repo.mongodb.org/apt/ubuntu bionic/mongodb-org/4.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-4.0.list
##RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 68818C72E52529D4 && \
##echo "deb http://repo.mongodb.org/apt/ubuntu bionic/mongodb-org/4.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-4.0.list
#RUN apt update
#RUN apt install -y libcurl4-openssl-dev mongodb-org-server mongodb-org
#
##RUN apt install cmake libpcre3-dev zlib1g-dev libgcrypt11-dev libicu-dev python -y
##RUN cd /home/zoul15 && wget https://astuteinternet.dl.sourceforge.net/project/cppcms/cppcms/1.2.1/cppcms-1.2.1.tar.bz2 \
##&& tar -xvjf cppcms-1.2.1.tar.bz2 && cd /home/zoul15/cppcms-1.2.1 && mkdir -p /home/zoul15/cppcms-1.2.1/build \
##&& cd /home/zoul15/cppcms-1.2.1/build && cmake .. && make && make install
#
#
#RUN cp /usr/share/zoneinfo/Asia/Shanghai  /etc/localtime
#
#RUN mkdir -p /home/zoul15/pylib && cd /home/zoul15/pylib && git clone https://github.com/zoulei/hunlgame.git
#ENV PYTHONPATH=$PATHONPATH:/home/zoul15/pylib
#
#RUN apt install -y python-setuptools python-pip
#RUN pip3 install pymongo flask
#
#RUN mkdir -p /home/zoul15/testdir/
#RUN mkdir -p /home/zoul15/testdirdata/TESTPARALLELLEARNDIR

#RUN pip3 install \
#pymongo numpy scipy sympy pandas tables scikit-learn matplotlib tqdm \
#seaborn pillow imageio PyYAML sqlalchemy pymongo jinja2 scikit-image scipy progressbar2 mock pep8 coverage \
#mako Flask GitPython tinydb tinydb-serialization hashfs fs \
#tensorflow==1.5 keras

ENV NGINX_MAX_UPLOAD 2048m
ENV NGINX_WORKER_PROCESSES auto
#ENV STATIC_INDEX 1
#ENV STATIC_PATH /app/static
#ENV STATIC_URL /static
#COPY ./app/custom.conf /etc/nginx/conf.d/