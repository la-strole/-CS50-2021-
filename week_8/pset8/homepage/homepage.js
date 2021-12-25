/* common way would be get json with request */
if (typeof data === 'undefined') {
  console.log('Can not find JSON file in root directory')
}
const mydata = JSON.parse(data)
if (typeof document === 'undefined') {
  console.log('Can not parse <document>')
}
const emptyCard = document.getElementsByClassName('card_column')[0]
const pageName = document.body.id

let cardCount = mydata[pageName].length

/* no more than 5 images on page */
if (cardCount > 5) {
  cardCount = 5
}
/* to cjange first zero-image on html page */
if (cardCount > 0) {
  const cardImage = emptyCard.getElementsByClassName('card-img-top')[0]
  cardImage.src = mydata[pageName][0][1]
  cardImage.alt = mydata[pageName][0][0]
  emptyCard.getElementsByClassName('card-text')[0].innerText = mydata[pageName][0][0]
}

for (let i = 1; i < cardCount; i++) {
  // copy card
  const c_card = emptyCard.cloneNode(true)
  // change card properties
  const cardImage = c_card.getElementsByClassName('card-img-top')[0]
  cardImage.src = mydata[pageName][i][1]
  cardImage.alt = mydata[pageName][i][0]
  c_card.getElementsByClassName('card-text')[0].innerText = mydata[pageName][i][0]
  // paste it in document
  document.getElementById('card_row').appendChild(c_card)
}
