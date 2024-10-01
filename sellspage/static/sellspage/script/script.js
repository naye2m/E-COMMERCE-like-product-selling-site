import * as Views from "./views.js"

// document.addEventListener("scroll",console.log)


document.addEventListener("scroll", function () {

})



// .                                              
// Scroll related
// .                                              
function getPercentageOfCurrentOffset() {
    return window.scrollY / (document.body.scrollHeight - window.innerHeight);
    // return window.pageYOffset / (document.body.scrollHeight - window.innerHeight);
}

function scrollYSmooth(Y) { return window.scroll({ top: Y, behavior: "smooth" }); }

function movetoElem(elem) { return scrollYSmooth(elem.offsetTop) }

function moveToSelector(selector) { return movetoElem(document.querySelector(selector)) }


