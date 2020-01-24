FROM python:3 AS install
ARG proj

COPY ./repo /repo
COPY ./app/${proj}/ /

ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install --upgrade pip
RUN pip install wheel
RUN pip install --find-links=/repo -r /requirements.txt


FROM python:3 AS app
ARG time=now
ARG rate=rt

ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY --from=install /app.yml /
COPY --from=install $VIRTUAL_ENV $VIRTUAL_ENV

EXPOSE 8888

ENV OB_PORT 5000
ENV OB_TIME ${time}
ENV OB_RATE ${rate}

CMD python -m ouroboros -vv -r -a -t${OB_TIME} -x${OB_RATE} /app.yml
