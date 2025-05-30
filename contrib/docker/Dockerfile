#FROM alpine:3.15
FROM alpine:3.18
#ARG CKAN_VERSION=ckan-2.9.11
ARG CKAN_VERSION=ckan-2.10.5

# Internals, you probably don't need to change these
ENV TZ=UTC
ENV APP_DIR=/srv/app
ENV SRC_DIR=/srv/app/src
ENV CKAN_INI=${APP_DIR}/ckan.ini
ENV PIP_SRC=${SRC_DIR}
ENV CKAN_STORAGE_PATH=/var/lib/ckan
ENV GIT_URL=https://github.com/ckan/ckan.git
# CKAN version to build
ENV GIT_BRANCH=${CKAN_VERSION}
# Customize these on the .env file if needed
ENV CKAN_SITE_URL=http://localhost:5000
ENV CKAN__PLUGINS image_view text_view recline_view datastore envvars dcat dcat_json_interface oidc_pkce structured_data scheming_datasets
ENV CKANEXT_KEYCLOAK_SERVER_URL=https://platform.beopendep.it/auth/realms/master/.well-known/openid-configuration
ENV CKANEXT_KEYCLOAK_CLIENT_ID=ckan
ENV CKANEXT_KEYCLOAK_REALM_NAME=master
ENV CKANEXT_KEYCLOAK_REDIRECT_URI=https://platform.beopendep.it/ckan
ENV CKANEXT_KEYCLOAK_CLIENT_SECRET_KEY=W2lBktmbDOZFYlpc3i0RVGxQDgyqzhq9
ENV CKANEXT_KEYCLOAK_BUTTON_STYLE=google
ENV CKANEXT_KEYCLOAK_ENABLE_CKAN_INTERNAL_LOGIN=True

# UWSGI options
ENV UWSGI_HARAKIRI=50

WORKDIR ${APP_DIR}

# Set up timezone
RUN apk add --no-cache tzdata
RUN echo ${TZ} > /etc/timezone
# Make sure both files are not exactly the same
RUN if ! [ /usr/share/zoneinfo/${TZ} -ef /etc/localtime ]; then \
        cp /usr/share/zoneinfo/${TZ} /etc/localtime ;\
    fi ;


# Install necessary packages to run CKAN
RUN apk add --no-cache git \
        gettext \
        postgresql-client \
        python3 \
        libxml2 \
        libxslt \
        musl-dev \
        uwsgi \
        uwsgi-http \
        uwsgi-corerouter \
        uwsgi-python \
        py3-gevent \
        uwsgi-gevent \
        libmagic \
        curl \
        patch && \
    # Packages to build CKAN requirements and plugins
    apk add --no-cache --virtual .build-deps \
        postgresql-dev \
        gcc \
        make \
        g++ \
        autoconf \
        automake \
    	libtool \
        python3-dev \
        libxml2-dev \
        libxslt-dev \
        linux-headers \
        openssl-dev \
        libffi-dev \
        cargo && \
    # Create SRC_DIR
    mkdir -p ${SRC_DIR} && \
    # Install pip, supervisord and uwsgi
    curl -o ${SRC_DIR}/get-pip.py https://bootstrap.pypa.io/get-pip.py && \
    python3 ${SRC_DIR}/get-pip.py && \
    pip3 install supervisor && \
    mkdir /etc/supervisord.d && \
    #pip wheel --wheel-dir=/wheels uwsgi gevent && \
    rm -rf ${SRC_DIR}/get-pip.py

COPY setup/supervisord.conf /etc

RUN pip3 install --upgrade pip setuptools && \
    pip3 install -e git+${GIT_URL}@${GIT_BRANCH}#egg=ckan && \

# Install CKAN
#RUN pip3 install -e git+${GIT_URL}@${GIT_BRANCH}#egg=ckan && \
    cd ${SRC_DIR}/ckan && \
    cp who.ini ${APP_DIR} && \
    # Workaround, can be removed when 2.10.2 is released
    # https://github.com/ckan/ckan/pull/7864
    #sed -i 's/pyyaml==6.0/pyyaml==6.0.1/' requirements.txt && \
    # begin workaround
    #sed -i '/pyyaml==5.4.1/d' requirements.txt && \
    echo 'Cython < 3.0' > /tmp/constraint.txt && \
    PIP_CONSTRAINT=/tmp/constraint.txt pip3 install PyYAML==5.4.1 && \
    # end workaround
    pip3 install -r requirement-setuptools.txt && \
    pip3 install --no-binary markdown -r requirements.txt && \
    # Install CKAN envvars to support loading config from environment variables
    pip3 install -e git+https://github.com/okfn/ckanext-envvars.git#egg=ckanext-envvars && \
    # Create and update CKAN config
    ckan generate config ${CKAN_INI} && \
    ckan config-tool ${CKAN_INI} "beaker.session.secret = " && \
    ckan config-tool ${CKAN_INI} "ckan.plugins = ${CKAN__PLUGINS}"

# Install dependencies for ckanext-dcat
RUN pip3 install -e git+https://github.com/ckan/ckanext-dcat.git#egg=ckanext-dcat && \
    ckan config-tool ${CKAN_INI} "ckan.plugins = ${CKAN__PLUGINS} dcat dcat_json_interface"
RUN pip install --upgrade rdflib geomet future
RUN pip install "isodate<1.0.0,>=0.7.2"

RUN ckan config-tool ${CKAN_INI} "ckanext.dcat.catalog_endpoint = /dcat/catalog.rdf"
RUN ckan config-tool ${CKAN_INI} "ckanext.dcat.enable_content_negotiation = true"
# ENV CKAN__PLUGINS="dcat"

# Install CKAN OIDC PKCE extension
RUN pip3 install ckanext-oidc-pkce && \
    ckan config-tool ${CKAN_INI} "ckan.plugins = ${CKAN__PLUGINS} oidc_pkce"
# Install CKAN ckanext-scheming extension
RUN pip install -e git+https://github.com/ckan/ckanext-scheming.git#egg=ckanext-scheming
 
# Install the keycloak module 
RUN pip install python-keycloak==0.24.0 blinker
 
# Check if the plugin is installed correctly
RUN if ! pip3 show ckanext-oidc-pkce; then echo "ckanext-oidc-pkce not installed"; exit 1; fi
 
# Configurazione di OIDC PKCE per Keycloak
RUN ckan config-tool ${CKAN_INI} "ckanext.oidc_pkce.base_url = https://platform.beopendep.it" && \
    ckan config-tool ${CKAN_INI} "ckanext.oidc_pkce.client_id = ckan" && \
    ckan config-tool ${CKAN_INI} "ckanext.oidc_pkce.client_secret = W2lBktmbDOZFYlpc3i0RVGxQDgyqzhq9" && \
    ckan config-tool ${CKAN_INI} "ckanext.oidc_pkce.auth_path = /auth/realms/master/protocol/openid-connect/auth" && \
    ckan config-tool ${CKAN_INI} "ckanext.oidc_pkce.token_path = /auth/realms/master/protocol/openid-connect/token" && \
    ckan config-tool ${CKAN_INI} "ckanext.oidc_pkce.userinfo_path = /auth/realms/master/protocol/openid-connect/userinfo" && \
    ckan config-tool ${CKAN_INI} "ckanext.oidc_pkce.redirect_path = /user/login/oidc-pkce/callback" && \
    ckan config-tool ${CKAN_INI} "ckanext.oidc_pkce.error_redirect = /user/register" && \
    ckan config-tool ${CKAN_INI} "ckanext.oidc_pkce.scope = openid email profile" && \
    ckan config-tool ${CKAN_INI} "ckanext.oidc_pkce.use_same_id = true" && \
    ckan config-tool ${CKAN_INI} "ckanext.oidc_pkce.munge_password = true"

# Find and modify the plugin to use the new directive new
RUN sed -i 's/dashboard.index/dashboard.datasets/' /usr/lib/python3.11/site-packages/ckanext/oidc_pkce/views.py

# Create a local user and group to run the app
RUN addgroup -g 92 -S ckan && \
    adduser -u 92 -h /home/ckan -s /bin/bash -D -G ckan ckan

# Create local storage folder
RUN mkdir -p ${CKAN_STORAGE_PATH} && \
    chown -R ckan:ckan ${CKAN_STORAGE_PATH}
##    
COPY setup/prerun.py ${APP_DIR}
COPY setup/start_ckan.sh ${APP_DIR}
ADD https://raw.githubusercontent.com/ckan/ckan/${GIT_BRANCH}/wsgi.py ${APP_DIR}
RUN chmod 644 ${APP_DIR}/wsgi.py
##
 
# Create entrypoint directory for children image scripts
ONBUILD RUN mkdir /docker-entrypoint.d

EXPOSE 5000

HEALTHCHECK --interval=60s --timeout=5s --retries=5 CMD curl --fail http://localhost:5000/api/3/action/status_show || exit 1

CMD ["sh","/srv/app/start_ckan.sh"]
