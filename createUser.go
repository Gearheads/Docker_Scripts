/* 
Rob Casale
This will:
 - Validate user does not exist and if it does throw Error
 - Create user
 - Activate user
Return codes:
 - 0 success
 - 1 user exist
 - 2 error create user
 - 8 others
*/

package main

import (
	"fmt"				// used for printing messages
	"os"				// used to setup proxy settings
	"io/ioutil"			// used to read in files and http responses
    "net/http"			// used for http requests
    "crypto/tls"		// used for certificate
    "crypto/x509"		// used for certificate
    "bytes"				// used to send json messages
)

func main() {
	// admin DTR credentials
	admin_username := "casaler"
	admin_password := <password>
	
	// DTR fully qualified hostname
	dtr_full_hostname := <dtr-hostname>
	
	// API responses
	activate_success := "200 OK"
	success := "201 Created"
	account_exists := "400 Bad Request"
	//json_not_specified := "415 Unsupported Media Type"
	
	// exit statuses
	exit_success := "exit(0): success"
	exit_user_exists := "exit(1): username already exists"
	exit_error_create_user := "exit(2): could not create username"
	exit_other := "exit(8): unknown error"
	incorrect_arguments := "exit(8): provide username only"
	
	// Set proxy settings
	setupProxy()
	
	// retrieve command line arguments
	if len(os.Args) == 2 {
		username := os.Args[1]
		
		// Request urls
		create_account_url := "https://"+dtr_full_hostname+"/api/v0/accounts/"
		activate_account_url := "https://"+dtr_full_hostname+"/api/v0/accounts/"+username+"/activate"
		
		var jsonCreateUser = []byte(`{"type":"user","name":"`+username+`","password":"`+admin_password+`"}`)
		
		response, err := postContent(create_account_url,admin_username,admin_password,jsonCreateUser)
		if err != nil {
			fmt.Println("Did not get a response from the url")
		} else {
			// the given username already exists
			if response.Status == account_exists {
				fmt.Println(exit_user_exists)
			} else if response.Status == success {
				// need to activate account
				activate_response, err := putContent(activate_account_url,admin_username,admin_password)
				if err != nil {
					fmt.Println("Did not get a response from the url")
				}
				// account was activated
				if activate_response.Status == activate_success {
					fmt.Println(exit_success)
				} else {
					// account was not activated - should not happen
					fmt.Println(exit_other)
				}
			} else {
				// received one of the other errors - 401, 403, 409
				fmt.Println(exit_error_create_user)
			}
		}
	} else {
		fmt.Println(incorrect_arguments)
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
	os.Setenv("HTTP_PROXY", "http://<username>:<password>@usproxy.es.oneadp.com:8080")
	os.Setenv("HTTPS_PROXY", "http://<username>:<password>@usproxy.es.oneadp.com:8080")
	os.Setenv("NO_PROXY", ".es.oneadp.com")
	os.Setenv("http_proxy", "http://<username>:<password>@usproxy.es.oneadp.com:8080")
	os.Setenv("https_proxy", "http://<username>:<password>@usproxy.es.oneadp.com:8080")
	os.Setenv("no_proxy", ".es.oneadp.com")
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

/**
 * This function will perform a POST request on the url you specified 
 * @param request url
 * @return array of bytes if retrieved successfully, otherwise the function
 * will return an error
 */
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
 * This function will perform a PUT request on the url you specified 
 * @param request url
 * @return array of bytes if retrieved successfully, otherwise the function
 * will return an error
 */
func putContent(url string, admin_username string, admin_password string) (*http.Response, error) {
	// Build the request
	req, err := http.NewRequest("PUT", url, nil)
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
