$(".message a").click(function () {
  $("form").animate({ height: "toggle", opacity: "toggle" }, "slow");
});
// function getToken() {
//   let data = document.cookie.split(";");
//   let hash = {};
//   for (d of data) {
//     let temp = d.trim().split("=");
//     hash[temp[0]] = temp[1];
//   }
//   return hash;
// }

// document.querySelector(".register-form").addEventListener("submit", (e) => {
//   e.preventDefault();
//   console.log("submit");
//   fetch(window.location.href, {
//     method: "POST",
//     headers: {
//       contentType: "application/json",
     
//     },
//   })
//     .then((res) => res.json())
//     .then((data) => console.log(data));
// });
// document.querySelector(".login-form").addEventListener("submit", (e) => {
//   e.preventDefault();
//   console.log("submit");
//   fetch(window.location.href, {
//     method: "POST",
//     headers: {
//       contentType: "application/json",
     
//     },
//   })
//     .then((res) => res.json())
//     .then((data) => console.log(data));
// });
