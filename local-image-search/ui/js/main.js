var htmlView = document.getElementById("htmlView");
var jsonView = document.getElementById("jsonView");
var jsonResponseContainer = document.getElementById("jsonResponseContainer");
var backendUrl = "http://localhost:8983/solr/my-collection/select";

function showImageTab(){
  htmlView.style.display = "table";
  jsonView.style.display = "none";
  document.getElementById("jsonTab").classList.remove("active");
  document.getElementById("htmlTab").classList.add("active");
}

function showJsonTab(){
  htmlView.style.display = "none";
  jsonView.style.display = "initial";
  document.getElementById("jsonTab").classList.add("active");
  document.getElementById("htmlTab").classList.remove("active");
}

function randomSearch(seed){
  if(seed===undefined)seed = Math.round(Math.random()*10000);
  getJSON(`${backendUrl}?rows=8&sort=random${seed} desc`, showSearchResults);
}

function randomColor() {
  var letters = "0123456789ABCDEF";
  var color = "";
  for (var i = 0; i < 6; i++) {
    color += letters[Math.floor(Math.random() * 16)];
  }
  return color;
}

function randomColorSearch(){
  color = randomColor();
  document.getElementById("color-palette").style.color = "#"+color;
  getJSON(`${backendUrl}?rows=8&rank.by=hex:0x${color}&rank.mode=color`, showSearchResults);
}

function randomImageSearch(){
  // Get random id
  getJSON(`${backendUrl}?fl=id&rows=1&sort=random${Math.round(Math.random()*10000)} desc`, function(status, msg, response){
    // Search by this id
    if(status==200){
      searchImages(response.response.docs[0].id);
    }
  });
}

function randomTextSpaceImages(){
  getJSON(`${backendUrl}?textspace.true=any&rows=8&sort=random${Math.round(Math.random()*10000)} desc`, showSearchResults);
}

function showSearchResults(status, statusText, resp){
  showJson(resp)
  html ="";
  if (status!=200) {
    msg = "Check your request";
    if(resp) {
      msg = resp.error.msg;
    }
    html += `
    <span class="professional-container">
    <h3>Statuscode ${status} ${statusText}</h3>
    <p>
    ${msg}
    </p>
    </span>
    `;
  } else {
    numFound = `Found ${resp.response.numFound} images in ${resp.responseHeader.QTime}ms`;
    document.getElementById("numFoundContainer").innerHTML = numFound;

    resp.response.docs.forEach((doc) => {
      filename = doc.url.substring(doc.url.lastIndexOf('/')+1);
      relevance = calcRelevanceIndex(doc.score);
      stars = "";
      for(var i = 0; i < relevance; i++) stars += '<i class="bi bi-star-fill"></i>';
      html+= `
      <div class="node">
        <div class="node-inner">
          <a onClick="searchImages(${doc.id})" title="Search for similar images">
            <div class="node-img">
              <img class="loading" src="${doc.url}" onload="imgLoaded(this)">
            </div>
          </a>
          <div class="node-details">
            <div>
              <div class="node-title" title="${doc.url}">${filename}</div>
              <div class="node-category" title="Score ${doc.score}">${stars}</div>
            </div>
            <a href="${doc.url}" target="_blank" title="Show image in new tab">
              <div class="abutton">
                <i class="bi bi-arrows-angle-expand"></i>
              </div>
            </a>
          </div>
        </div>
      </div>
      `;
    });
    if (resp.response.numFound<=1) {
      html += `
      <span class="professional-container">
        <h3>Not the results you are looking for?</h3>
        <p>
          We also provide specialized AI model training to exactly fit your use case.
        </p>
        <a class="abutton" href="https://pixolution.org/custom-ai" target="_blank">
          Learn more <i class="bi bi-arrow-right"></i>
        </a>
      </span>
      `;
    }
  }
  window.scrollTo(0,0);
  nodeCarrier.innerHTML = html;

}

function calcRelevanceIndex(score){
  if(score>0.85)return 4;
  if(score>0.7)return 3;
  if(score>0.6)return 2;
  if(score>0.5)return 1;
  return 0;
}


function showJson(json){
  code = JSON.stringify(json, null, 4);
  jsonResponseContainer.innerHTML = code;
  if(hljs) hljs.highlightElement(jsonResponseContainer);
}

function searchImages(id){
  getJSON(`${backendUrl}?rows=8&rank.by=id:${id}&rank.mode=default`, showSearchResults);
}



var getJSON = function(url, callback) {
  var xhr = new XMLHttpRequest();
  xhr.open("get", url, true);

  xhr.responseType = "json";
  xhr.onload = function() {
    callback(xhr.status, xhr.statusText, xhr.response);
  };
  xhr.onerror = function(evt){
    html =`
    <span class="professional-container">
    <h3><i class="bi bi-exclamation-diamond"></i> Is your server up and running?</h3>
    <p>
    An error occured. Please check that the server is up and running.
    </p>
    </span>
    `;
    nodeCarrier.innerHTML = html;
  }
  xhr.send();
  //Show url
  document.getElementById("searchInput").value = url;
};

////////////////////
// UI
////////////////////
document.addEventListener('readystatechange', event => {
  if (event.target.readyState === 'complete') {
    //All source loaded, init app
    showImageTab();
    randomSearch(1);
  }
});

function search(){
  var url = document.getElementById("searchInput").value;
  getJSON(url, showSearchResults);
}

function copyURL(){
  /* Get the text field */
  var copyText = document.getElementById("searchInput");
  /* Select the text field */
  copyText.select();
  copyText.setSelectionRange(0, 99999); /* For mobile devices */
  /* Copy the text inside the text field */
  document.execCommand("copy");
}


function onEnter(event) {
  if (event.keyCode==13) search();
}

function imgLoaded(obj){
    obj.classList.remove('loading');
}
