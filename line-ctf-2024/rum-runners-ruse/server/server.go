package main

import (
	"bufio"
	"crypto/x509"
	"encoding/hex"
	"encoding/pem"
	"fmt"
	"io"
	"io/ioutil"
	"net"
	"os"

	"go.mozilla.org/pkcs7"
)

const PORT = ":11224"

func verifySignature(signed []byte, certPool *x509.CertPool) (err error) {

	p7, err := pkcs7.Parse(signed)
	if err != nil {
		err = fmt.Errorf("{\"error\": \"Cannot parse signed data\"}")
		return
	}

	if err = p7.VerifyWithChain(certPool); err != nil {
		err = fmt.Errorf("{\"error\": \"Failed to verify signature\"}")
		return
	}
	return nil
}

func handleConnection(c net.Conn, certPool *x509.CertPool, flag string) {
	defer c.Close()
	netData, err := bufio.NewReader(c).ReadString('\n')
	if err != nil {
		//fmt.Print("{\"error\": \"cannot read data from connection\"}")
		io.WriteString(c, "{\"error\": \"cannot read data from connection\"}")
		return
	}

	data, err := hex.DecodeString(netData)
	err = verifySignature(data, certPool)
	if err != nil {
		//fmt.Print(err.Error())
		io.WriteString(c, err.Error())
	} else {
		io.WriteString(c, flag)
	}
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

func loadFlag() (string, error) {
	flagBytes, err := ioutil.ReadFile("secret/flag.txt")
	if err != nil {
		return "", err
	}
	return string(flagBytes), nil

}

func main() {
	flag, err := loadFlag()
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
	cert, err := loadCertificate("cert.pem")
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
	certPool := x509.NewCertPool()
	certPool.AddCert(cert)

	l, err := net.Listen("tcp", PORT)
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
	defer l.Close()

	for {
		conn, err := l.Accept()
		if err != nil {
			//fmt.Println(err)
			continue
		}
		go handleConnection(conn, certPool, flag)
	}
}
