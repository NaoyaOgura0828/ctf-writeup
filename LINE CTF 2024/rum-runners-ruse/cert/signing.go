package main

import (
	"crypto/rsa"
	"crypto/x509"
	"encoding/pem"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"time"

	"go.mozilla.org/pkcs7"
)

func main() {

	content := []byte("Misc challenge")

	privkey, err := loadPrivateKey("key.pem")
	if err != nil {
		log.Fatalf("Failed to load private key: %v", err)
	}

	cert, err := loadCertificate("cert.pem")
	if err != nil {
		log.Fatalf("Failed to load certificate: %v", err)
	}

	toBeSigned, err := pkcs7.NewSignedData(content)
	if err != nil {
		log.Fatalf("Cannot initialize signed data: %s", err)
		return
	}

	signerInfoConfig := pkcs7.SignerInfoConfig{
		ExtraSignedAttributes: []pkcs7.Attribute{
			{
				Type:  pkcs7.OIDAttributeSigningTime,
				Value: time.Date(2000, 1, 1, 1, 1, 1, 0, time.UTC),
			},
		},
	}

	if err = toBeSigned.AddSigner(cert, privkey, signerInfoConfig); err != nil {
		log.Fatalf("Cannot add signer: %s", err)
		return
	}

	signed, err := toBeSigned.Finish()
	if err != nil {
		log.Fatalf("Cannot finish signing data: %s", err)
		return
	}

	signFile, err := os.Create("sign.der")
	if err != nil {
		panic(err)
	}
	pem.Encode(os.Stdout, &pem.Block{Type: "PKCS7", Bytes: signed})
	signFile.Write(signed)
	signFile.Close()

	fmt.Print("Save: signed data -> sign.der")

}

func loadPrivateKey(path string) (*rsa.PrivateKey, error) {
	keyBytes, err := ioutil.ReadFile(path)
	if err != nil {
		return nil, err
	}

	block, _ := pem.Decode(keyBytes)
	if block == nil {
		return nil, fmt.Errorf("failed to decode PEM block containing private key")
	}

	privateKey, err := x509.ParsePKCS1PrivateKey(block.Bytes)
	if err != nil {
		return nil, fmt.Errorf("failed to parse private key: %v", err)
	}

	return privateKey, nil
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
