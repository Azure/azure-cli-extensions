#!/bin/bash
# Following guide from: https://www.golinuxcloud.com/openssl-create-certificate-chain-linux/
OriginalPath=`pwd`

RootPath=`realpath $(dirname $0)`
cd $RootPath

# create dirs for root CA
mkdir -p $RootPath/rootCA/{certs,crl,newcerts,private,csr}
mkdir -p $RootPath/intermediateCA/{certs,crl,newcerts,private,csr}

# create index files
echo 1000 > $RootPath/rootCA/serial
echo 1000 > $RootPath/intermediateCA/serial

# create crlnumbers
echo 0100 > $RootPath/rootCA/crlnumber
echo 0100 > $RootPath/intermediateCA/crlnumber

# create index files
touch $RootPath/rootCA/index.txt
touch $RootPath/intermediateCA/index.txt
# NOTE: needed for testing
echo "unique_subject = no" >> $RootPath/rootCA/index.txt.attr
echo "unique_subject = no" >> $RootPath/intermediateCA/index.txt.attr

# generate root key
openssl genrsa -out $RootPath/rootCA/private/ca.key.pem 4096
chmod 400 $RootPath/rootCA/private/ca.key.pem

# view the key
# openssl rsa -noout -text -in $RootPath/rootCA/private/ca.key.pem

# generate root cert
openssl req -config openssl_root.cnf -key $RootPath/rootCA/private/ca.key.pem -new -x509 -days 7300 -sha256 -extensions v3_ca -out $RootPath/rootCA/certs/ca.cert.pem -subj "/C=US/ST=Georgia/L=Atlanta/O=Microsoft/OU=ACCCT/CN=Root CA"

# change permissions on root key so it's not globally readable
chmod 644 $RootPath/rootCA/certs/ca.cert.pem

# verify root cert
openssl x509 -noout -text -in $RootPath/rootCA/certs/ca.cert.pem

# generate intermediate key
openssl genrsa -out $RootPath/intermediateCA/private/intermediate.key.pem 4096
chmod 600 $RootPath/intermediateCA/private/intermediate.key.pem

# make CSR for intermediate
openssl req -config openssl_intermediate.cnf -key $RootPath/intermediateCA/private/intermediate.key.pem -new -sha256 -out $RootPath/intermediateCA/certs/intermediate.csr.pem -subj "/C=US/ST=Georgia/L=Atlanta/O=Microsoft/OU=ACCCT/CN=Intermediate CA"

# sign intermediate cert with root
openssl ca -config openssl_root.cnf -extensions v3_intermediate_ca -days 3650 -notext -md sha256 -in $RootPath/intermediateCA/certs/intermediate.csr.pem -out $RootPath/intermediateCA/certs/intermediate.cert.pem -batch

# make it readable by everyone
chmod 644 $RootPath/intermediateCA/certs/intermediate.cert.pem

# print the cert
# openssl x509 -noout -text -in $RootPath/intermediateCA/certs/intermediate.cert.pem

# verify intermediate cert
openssl verify -CAfile $RootPath/rootCA/certs/ca.cert.pem $RootPath/intermediateCA/certs/intermediate.cert.pem

# create chain file
cat $RootPath/intermediateCA/certs/intermediate.cert.pem $RootPath/rootCA/certs/ca.cert.pem > $RootPath/intermediateCA/certs/ca-chain.cert.pem

# verify chain
openssl verify -CAfile $RootPath/intermediateCA/certs/ca-chain.cert.pem $RootPath/intermediateCA/certs/intermediate.cert.pem

# create server key
openssl ecparam -out $RootPath/intermediateCA/private/www.contoso.com.key.pem -name secp384r1 -genkey
openssl pkcs8 -topk8 -nocrypt -in $RootPath/intermediateCA/private/www.contoso.com.key.pem -out $RootPath/intermediateCA/private/ec_p384_private.pem

chmod 600 $RootPath/intermediateCA/private/www.contoso.com.key.pem

# create csr for server
openssl req -config openssl_intermediate.cnf -key $RootPath/intermediateCA/private/www.contoso.com.key.pem -new -sha384 -out $RootPath/intermediateCA/csr/www.contoso.com.csr.pem -batch

# sign server cert with intermediate key
openssl ca -config openssl_intermediate.cnf -extensions server_cert -days 375 -notext -md sha384 -in $RootPath/intermediateCA/csr/www.contoso.com.csr.pem -out $RootPath/intermediateCA/certs/www.contoso.com.cert.pem -batch

# print the cert
# openssl x509 -noout -text -in $RootPath/intermediateCA/certs/www.contoso.com.cert.pem

# make a public key
# openssl x509 -pubkey -noout -in $RootPath/intermediateCA/certs/www.contoso.com.cert.pem -out $RootPath/intermediateCA/certs/pubkey.pem

# create chain file
cat $RootPath/intermediateCA/certs/www.contoso.com.cert.pem $RootPath/intermediateCA/certs/intermediate.cert.pem $RootPath/rootCA/certs/ca.cert.pem > $RootPath/intermediateCA/certs/www.contoso.com.chain.cert.pem

cd $OriginalPath