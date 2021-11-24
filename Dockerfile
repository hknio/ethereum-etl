FROM --platform=linux/amd64 python:3.8
ENV PROJECT_DIR=ethereum-etl
ENV PROVIDER_URI=https://

RUN mkdir /$PROJECT_DIR
WORKDIR /$PROJECT_DIR
COPY . .
RUN pip install --upgrade pip && pip install -e /$PROJECT_DIR/[streaming]

# Add Tini
ENV TINI_VERSION v0.18.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini

# command line working like so
# docker run --rm --name ethereum-etl ethereum-etl:f9296f0573111f8200e65ade27a986f2dbe8d620  stream --chain ethereum --output s3://poap-scan-v2-data --environment test --provider-uri https://blue-aged-sky.quiknode.pro/c61b75ade31005d16b540da23759a45a9d4db7a9/ -e block,transaction --batch-size 10 --start-block 12345678

ENTRYPOINT ["/tini", "--", "python", "ethereumetl", "stream", "--chain", "ethereum", "--output", "s3://poap-scan-v2-data", "--environment", "test", "--provider-uri", "https://blue-aged-sky.quiknode.pro/c61b75ade31005d16b540da23759a45a9d4db7a9/", "-e", "block,transaction,log,trace,token_transfer,contract,receipt,token", "--batch-size", "10", "--start-block", "12345678"]
