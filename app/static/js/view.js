document
  .querySelector('.article-list-body')
  .addEventListener('click', viewItem);

function viewItem(e) {
  if (e.target.parentElement.classList.contains('article-row')) {
    window.location.href = e.target.parentElement.id;
  }
}
