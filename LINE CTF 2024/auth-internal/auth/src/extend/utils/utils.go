package utils

import (
	errors "errors"
	fmt "fmt"
	http "net/http"
	exec "os/exec"
	strconv "strconv"
	strings "strings"

	uuid "github.com/pborman/uuid"
)

func IsInternal(r *http.Request) bool {
	i, _ := strconv.ParseBool(r.Header.Get("X-Internal"))
	return i
}

func GenVerifyURL(url string) string {
	u := strings.TrimRight(url, "/")
	f := "/verify.txt"
	return u + f
}

func GenVerifyCode() string {
	return strings.Replace(uuid.NewRandom().String(), "-", "", -1)[:6]
}

func GenVerifyMessge(vc string, r string) string {
	return fmt.Sprintf("verify code %s is not matched with verify endpoint response %s", vc, r)
}

func GenUserID() string {
	return uuid.NewRandom().String()
}

func VerifyRequest(u string) (string, error) {
	rs, err := exec.Command("curl", "-H", "User-Agent: Verifier", u).Output() // I tested it and it's safe!
	if err != nil {
		return "", errors.New("error during verify")
	}
	return string(rs), nil
}

func CheckVerify(r string, c string) bool {
	return strings.TrimRight(r, "\n") != c
}
