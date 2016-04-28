/* 
Rob Casale
This will:
 - Validate user does not exist and if it does throw Error
 - Validate repo does not exist and if it does throw Error
 - Create user
 - Create Repo
Return codes:
 - 0 success
 - 1 user exist
 - 2 repo exist
 - 4 error create user
 - 5 error create repo
 - 8 others
*/

package main

import (
	"fmt"				// used for printing messages
	"strings"			// used for string editing
	"bufio"				// used to read in input
	"os"				// used to setup proxy settings
	"io/ioutil"			// used to read in files and http responses
    "net/http"			// used for http requests
    // "encoding/json"
    "crypto/tls"		// used for certificate
    "crypto/x509"		// used for certificate
    "bytes"				// used to send json messages
)

type User struct {
	username string
	password string
}
type Users []User

func main() {
	admin_username := "casaler"
	admin_password := <password>
	// API responses
	//success := "200 OK"
	account_exists := "400 Bad Request"
	
	// exit statuses
	//exit_success := "exit(0): success"
	exit_user_exists := "exit(1): username already exists"
	//exit_repo_exists := "exits(2): repository already exists"
	//exit_error_create_user := "exit(4): could not create username"
	//exit_error_create_repo := "exit(5): could not create repository"
	//exit_other := "exit(8): unknown error"
	
	// Create read buffer 
	reader := bufio.NewReader(os.Stdin)
	// Read in username
	fmt.Printf("Enter username: ")
	input_username, _ := reader.ReadString('\n')
	username := strings.TrimSpace(input_username)
	// Read in image name
	fmt.Printf("Enter name of image: ")
	// input_image, _ := reader.ReadString('\n')
	// image := strings.TrimSpace(input_image)
	
	setupProxy()
	
	// Request urls
	// list_accounts_url := "https://<dtr-hostname>/api/v0/accounts?start=0&limit=10"
	create_account_url := "https://<dtr-hostname>/api/v0/accounts/"
	// activate_account_url := "https://<dtr-hostname>/api/v0/accounts/<username>/activate"
	// create_repo_url := "https://<dtr-hostname>/api/v0/repositories/<username>/"
	
	var jsonCreateUser = []byte(`{"type":"user","name":"`+username+`","password":"`+admin_password+`"}`)
	
	// official version - var jsonCreateRepo = []byte(`{"name": "string","shortDescription": "string","longDescription": "string","visibility": "public"}`)
	// var jsonCreateRepo = []byte(`{"name": "`+image+`","visibility":"public"}`)
	
	// response, err := getContent(create_account_url+username,admin_username,admin_password)
	response, err := postContent(create_account_url,admin_username,admin_password,jsonCreateUser)
	if err != nil {
    	fmt.Println("Did not get a response from the url")
	} else {
    	// the given username already exists
    	if response.Status == account_exists {
    		fmt.Println(exit_user_exists)
    	} else {
    		fmt.Println(response.Status)
    	}
	}
}

/**
 * This will set all of the proxy variables that are needed to get through
 * to the other side
 * @param None
 * @return None
 */
func setupProxy() {
	// By-pass proxy
	os.Setenv("HTTP_PROXY", "http://<username>:<password>@<proxy-info>:8080")
	os.Setenv("HTTPS_PROXY", "http://<username>:<password>@<proxy-info>:8080")
	os.Setenv("NO_PROXY", "<no-proxy-info>")
	os.Setenv("http_proxy", "http://<username>:<password>@<proxy-info>:8080")
	os.Setenv("https_proxy", "http://<username>:<password>@<proxy-info>:8080")
	os.Setenv("no_proxy", "<no-proxy-info>")
}

/**
 * This will create a client will the DTRs self-signed certificate such that
 * API calls can be made
 * @param None
 * @return client with the certificate added
 */
func createClient() (*http.Client) {
	cert := x509.NewCertPool()
    dtr_cert, err := ioutil.ReadFile("ca.crt")
    if err != nil {
    	fmt.Println("Could not read in certificate")
    	return nil
    }
	cert.AppendCertsFromPEM(dtr_cert)
	tr := &http.Transport{
		TLSClientConfig:    &tls.Config{RootCAs: cert},
		DisableCompression: true,
	}
	client := &http.Client{Transport: tr}
	return client
}

/**
 * This function will perform a GET request on the url you specified 
 * @param request url
 * @return array of bytes if retrieved successfully, otherwise the function
 * will return an error
 */
func getContent(url string, admin_username string, admin_password string) (*http.Response, error) {
    // Build the request
    req, err := http.NewRequest("GET", url, nil)
    if err != nil {
      fmt.Println("Build failed: ",err)
      return nil, err
    }
    req.SetBasicAuth(admin_username,admin_password)
    // Send the request via a client
    resp, err := createClient().Do(req)
    if err != nil {
      fmt.Println("Send request failed: ",err)
      return nil, err
    }
    // Defer the closing of the body
    defer resp.Body.Close()
    return resp, nil
}

func postContent(url string, admin_username string, admin_password string,
	jsonMessage []byte) (*http.Response, error) {
	// Build the request
	req, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonMessage))
	if err != nil {
      fmt.Println("Build failed: ",err)
      return nil, err
    }
	req.SetBasicAuth(admin_username,admin_password)
	req.Header.Set("Content-Type", "application/json")
	// Send the request via a client
	resp, err := createClient().Do(req)
	if err != nil {
      fmt.Println("Send request failed: ",err)
      return nil, err
    }
	// Defer the closing of the body
	defer resp.Body.Close()
	return resp, nil
}

/**
 * Simple test function to see if I can make a simple GET request
 * @param None
 * @return None
 */
func simpleTest() {
	resp, err := http.Get("https://www.google.com")
	if err != nil {
		fmt.Println("No Google :(")
	}
	defer resp.Body.Close()
	body, err := ioutil.ReadAll(resp.Body)
	fmt.Println(string(body))
}
