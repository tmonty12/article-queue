document.querySelector('#back-button').addEventListener('click', goBack);

function goBack() {
  window.location.href = document.referrer;
}
