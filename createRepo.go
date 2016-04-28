/* 
Rob Casale
This will:
 - Validate user does exist and if it does not throw Error
 - Validate repo does not exist and if it does throw Error
 - Create Repo
Return codes:
 - 0 success
 - 1 user does not exist
 - 2 repo exist
 - 3 error create repo
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
	admin_password := "adpadp11"
	
	// DTR fully qualified hostname
	dtr_full_hostname := "cdldvostk1vdtr001.es.ad.adp.com"
	
	// API responses
	success := "201 Created"
	account_exists := "200 OK"
	repo_exists := "400 Bad Request"
	//account_does_not_exist := "404 Not Found"
	//json_not_specified := "415 Unsupported Media Type"
	
	// exit statuses
	exit_success := "exit(0): success"
	exit_user_does_not_exist := "exit(1): username does not exists"
	exit_repo_exists := "exits(2): repository already exists"
	//exit_error_create_user := "exit(4): could not create username"
	//exit_error_create_repo := "exit(5): could not create repository"
	exit_other := "exit(8): unknown error"
	incorrect_arguments := "exit(8): provide username and password"
	
	
	// Set proxy settings
	setupProxy()
	
	// retrieve command line arguments
	if len(os.Args) == 3 {
		username := os.Args[1]
		image := os.Args[2]
		
		// Request urls
		account_details_url := "https://"+dtr_full_hostname+"/api/v0/accounts/"
		create_repo_url := "https://"+dtr_full_hostname+"/api/v0/repositories/"+username
		
		// official version - var jsonCreateRepo = []byte(`{"name": "string","shortDescription": "string","longDescription": "string","visibility": "public"}`)
		var jsonCreateRepo = []byte(`{"name": "`+image+`","visibility":"public"}`)
		
		response, err := getContent(account_details_url+username,admin_username,admin_password)
		if err != nil {
	    	fmt.Println("Did not get a response from the url")
		} else {
	    	// the given username exists
	    	if response.Status == account_exists {
	    		// create repo
	    		repo_response, err := postContent(create_repo_url,admin_username,admin_password,jsonCreateRepo)
	    		if err != nil {
	    			fmt.Println("Did not get a response from the url")
	    		} else {
	    			if repo_response.Status == success {
	    				fmt.Println(exit_success)
	    			} else if repo_response.Status == repo_exists {
	    				// could not create repo
	    				fmt.Println(exit_repo_exists)
	    			} else {
	    				// other errors
	    				fmt.Println(exit_other)
	    			}
	    		}
	    	} else {
	    		// username does not exist, cannot create repo
	    		fmt.Println(exit_user_does_not_exist)
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
	os.Setenv("HTTP_PROXY", "http://paascloud:8e)P4m)I5y(F9@usproxy.es.oneadp.com:8080")
	os.Setenv("HTTPS_PROXY", "http://paascloud:8e)P4m)I5y(F9@usproxy.es.oneadp.com:8080")
	os.Setenv("NO_PROXY", ".es.oneadp.com")
	os.Setenv("http_proxy", "http://paascloud:8e)P4m)I5y(F9@usproxy.es.oneadp.com:8080")
	os.Setenv("https_proxy", "http://paascloud:8e)P4m)I5y(F9@usproxy.es.oneadp.com:8080")
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