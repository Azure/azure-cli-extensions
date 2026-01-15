#!/bin/bash
# Following guide from: https://www.golinuxcloud.com/openssl-create-certificate-chain-linux/
OriginalPath=`pwd`

RootPath=`realpath $(dirname $0)`
OutPath=${1:-$RootPath}

mkdir -p $OutPath

cd $OutPath

# create dirs for root CA
mkdir -p $OutPath/rootCA/{certs,crl,newcerts,private,csr}
mkdir -p $OutPath/intermediateCA/{certs,crl,newcerts,private,csr}

# create index files
echo 1000 > $OutPath/rootCA/serial
echo 1000 > $OutPath/intermediateCA/serial

# create crlnumbers
echo 0100 > $OutPath/rootCA/crlnumber
echo 0100 > $OutPath/intermediateCA/crlnumber

# create index files
touch $OutPath/rootCA/index.txt
touch $OutPath/intermediateCA/index.txt
# NOTE: needed for testing
echo "unique_subject = no" >> $OutPath/rootCA/index.txt.attr
echo "unique_subject = no" >> $OutPath/intermediateCA/index.txt.attr

# generate root key
openssl genrsa -out $OutPath/rootCA/private/ca.key.pem 4096
chmod 400 $OutPath/rootCA/private/ca.key.pem

# view the key
# openssl rsa -noout -text -in $OutPath/rootCA/private/ca.key.pem

# generate root cert
openssl req -config $RootPath/openssl_root.cnf -key $OutPath/rootCA/private/ca.key.pem -new -x509 -days 7300 -sha256 -extensions v3_ca -out $OutPath/rootCA/certs/ca.cert.pem -subj "/C=US/ST=Georgia/L=Atlanta/O=Microsoft/OU=ACCCT/CN=Root CA"

# change permissions on root key so it's not globally readable
chmod 644 $OutPath/rootCA/certs/ca.cert.pem

# verify root cert
openssl x509 -noout -text -in $OutPath/rootCA/certs/ca.cert.pem

# generate intermediate key
openssl genrsa -out $OutPath/intermediateCA/private/intermediate.key.pem 4096
chmod 600 $OutPath/intermediateCA/private/intermediate.key.pem

# make CSR for intermediate
openssl req -config $RootPath/openssl_intermediate.cnf -key $OutPath/intermediateCA/private/intermediate.key.pem -new -sha256 -out $OutPath/intermediateCA/certs/intermediate.csr.pem -subj "/C=US/ST=Georgia/L=Atlanta/O=Microsoft/OU=ACCCT/CN=Intermediate CA"

# sign intermediate cert with root
openssl ca -config $RootPath/openssl_root.cnf -extensions v3_intermediate_ca -days 3650 -notext -md sha256 -in $OutPath/intermediateCA/certs/intermediate.csr.pem -out $OutPath/intermediateCA/certs/intermediate.cert.pem -batch

# make it readable by everyone
chmod 644 $OutPath/intermediateCA/certs/intermediate.cert.pem

# print the cert
# openssl x509 -noout -text -in $OutPath/intermediateCA/certs/intermediate.cert.pem

# verify intermediate cert
openssl verify -CAfile $OutPath/rootCA/certs/ca.cert.pem $OutPath/intermediateCA/certs/intermediate.cert.pem

# create chain file
cat $OutPath/intermediateCA/certs/intermediate.cert.pem $OutPath/rootCA/certs/ca.cert.pem > $OutPath/intermediateCA/certs/ca-chain.cert.pem

# verify chain
openssl verify -CAfile $OutPath/intermediateCA/certs/ca-chain.cert.pem $OutPath/intermediateCA/certs/intermediate.cert.pem

# create server key
openssl ecparam -out $OutPath/intermediateCA/private/www.contoso.com.key.pem -name secp384r1 -genkey
openssl pkcs8 -topk8 -nocrypt -in $OutPath/intermediateCA/private/www.contoso.com.key.pem -out $OutPath/intermediateCA/private/ec_p384_private.pem

chmod 600 $OutPath/intermediateCA/private/www.contoso.com.key.pem

# create csr for server
openssl req -config $RootPath/openssl_intermediate.cnf -key $OutPath/intermediateCA/private/www.contoso.com.key.pem -new -sha384 -out $OutPath/intermediateCA/csr/www.contoso.com.csr.pem -batch

# sign server cert with intermediate key
openssl ca -config $RootPath/openssl_intermediate.cnf -extensions server_cert -days 375 -notext -md sha384 -in $OutPath/intermediateCA/csr/www.contoso.com.csr.pem -out $OutPath/intermediateCA/certs/www.contoso.com.cert.pem -batch

# print the cert
# openssl x509 -noout -text -in $OutPath/intermediateCA/certs/www.contoso.com.cert.pem

# make a public key
# openssl x509 -pubkey -noout -in $OutPath/intermediateCA/certs/www.contoso.com.cert.pem -out $OutPath/intermediateCA/certs/pubkey.pem

# create chain file
cat $OutPath/intermediateCA/certs/www.contoso.com.cert.pem $OutPath/intermediateCA/certs/intermediate.cert.pem $OutPath/rootCA/certs/ca.cert.pem > $OutPath/intermediateCA/certs/www.contoso.com.chain.cert.pem

cd $OriginalPath