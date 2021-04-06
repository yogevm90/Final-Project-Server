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
