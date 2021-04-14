/**
 * Set action to happen on be submission
 */
function SetValueToSubmit(path, id1, id2, isText=true) {
    let testId = document.getElementById(id1).value;
    if (isText) {
        testId = document.getElementById(id1).textContent;
    }
    let verificationId = document.getElementById(id2).value;
    window.location.replace(`${window.location.origin}/${path}/${testId}/${verificationId}`);
}


/**
 * Return a request object
 */
 function getRequestObject() {
    if (window.XMLHttpRequest) {
        return (new XMLHttpRequest());
    } 
    else {
        window.alert("Ajax is not supported!");
        return(null); 
    }
}

/**
 * Wrapper for handling the response of a request
 * 
 * @param {request object} request 
 * @param {function for handling the response of the request} responseHandler 
 */
function handleResponse(request, responseHandler) {
    console.log(`Ready State ${request.readyState}`);
    console.log(`status ${request.status}`);
    if ((request.readyState == 4) && (request.status == 200)) {
        responseHandler(request);
    }
}
  
/**
 * Make request for a given URL with a given method
 * 
 * @param {url for the request} url 
 * @param {handler for the response} responseHandler 
 * @param {GET / POST / PUT / etc.} method 
 * @param {data to send if needed} data 
 */
function MakeRequest(url, responseHandler, method="GET", data=null, headers={}) {
    let requestor = getRequestObject();
    requestor.onreadystatechange = function() {
        handleResponse(requestor, responseHandler); 
    };
    requestor.open(method, url, true);
    if(headers) {
        for(var key in headers) {
            requestor.setRequestHeader(key, headers[key]);
        }
    }
    requestor.send(data);
    return requestor;
}


function KeyDetails() {
    MakeRequest(
        "http://localhost:3001/OsDetails",
        (request) => {
            MakeRequest(
                "/CreateKey",
                (request) => {
                    document.getElementById("testKey").value = JSON.parse(request.responseText)["test_key"];
                    document.getElementById("loginButton").disabled = false;
                    document.getElementById("username").disabled = false;
                    document.getElementById("password").disabled = false;
                },
                "GET",
                request.responseText
            );
        }
    );
}
