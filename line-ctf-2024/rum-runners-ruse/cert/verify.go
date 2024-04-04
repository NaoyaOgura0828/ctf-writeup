package main

import (
	"crypto/x509"
	"encoding/pem"
	"fmt"
	"io/ioutil"
	"log"

	"go.mozilla.org/pkcs7"
)

func main() {

	cert, err := loadCertificate("cert.pem")
	if err != nil {
		log.Fatalf("Failed to load certificate: %v", err)
	}

	signed, err := ioutil.ReadFile("sign.der")
	if err != nil {
		log.Fatalf("Failed to read signed data: %v", err)
	}

	p7, err := pkcs7.Parse(signed)
	if err != nil {
		log.Fatalf("Cannot parse our signed data: %v", err)
		return
	}

	certPool := x509.NewCertPool()
	certPool.AddCert(cert)

	if err = p7.VerifyWithChain(certPool); err != nil {
		log.Fatalf("Failed to verify signature: %v", err)
	}
	fmt.Println("Signature verified successfully")

}

func loadCertificate(path string) (*x509.Certificate, error) {
	certBytes, err := ioutil.ReadFile(path)
	if err != nil {
		return nil, err
	}

	block, _ := pem.Decode(certBytes)
	if block == nil {
		return nil, fmt.Errorf("failed to decode PEM block containing certificate")
	}

	cert, err := x509.ParseCertificate(block.Bytes)
	if err != nil {
		return nil, fmt.Errorf("failed to parse certificate: %v", err)
	}

	return cert, nil
}
