/**
 * Set action to happen on be submission
 */
function SetValueToSubmit() {
    let testId = document.getElementById("testId").textContent;
    let verificationId = document.getElementById("checkId").value;
    let verifyForm = document.getElementById("verifyForm");
    verifyForm.action = `${window.location.origin}/VerifyTest/${testId}/${verificationId}`;
}